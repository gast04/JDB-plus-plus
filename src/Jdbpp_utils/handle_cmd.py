import sys
from termcolor import colored
from typing import List, Dict

from Jdbpp_utils import *
import Jdbpp_utils.definitions as defs
from Jdbpp_utils.print_utils import printUI
from NativeSupport.native import attachGdb, calcNativeBPoffset

''' 
  defined commands
'''
# 0: jdb command 1-x: short forms
CMD_LOCALS = ["locals", "l"]
CMD_STEPO = ["next", "n", "so"]
CMD_STEPI = ["stepi", "si"]
CMD_STEPU = ["step up", "su"]
CMD_QUIT  = ["exit", "quit", "q"]
CMD_CONT  = ["cont", "c", "continue"]
CMD_INTER = ["interactive"]
CMD_SHOW_BPS = ["clear", "bps", "breakpoints"]
CMD_TRACE = ["trace methods", "trace"]
CMD_UNTRACE = ["untrace"]

# special case
CMD_BREAKPOINT = ["bp", "b"] # need line number as argument

# native support
CMD_ATTACH_GDB = ["attach gdb", "agdb", "ag"]
CMD_NATIVE_BP  = ["native bp", "nbp"] # need load address as argument

'''
  execute single command
'''
def execCmd(p, cmd):
  if any([cmd == x for x in CMD_LOCALS]):
    handleLocals(p)
  elif any([cmd == x for x in CMD_STEPO]):
    handleStepO(p)
  elif any([cmd == x for x in CMD_STEPI]):
    handleStepI(p)
  elif any([cmd == x for x in CMD_STEPU]):
    handleStepU(p)
  elif any([cmd == x for x in CMD_QUIT]):
    handleQuit(p)
  elif any([cmd == x for x in CMD_CONT]):
    handleCont(p)
  elif any([cmd == x for x in CMD_SHOW_BPS]):
    handleBps(p)
  elif any([cmd == x for x in CMD_TRACE]):
    handleTrace(p)
  elif any([cmd == x for x in CMD_UNTRACE]):
    handleUnTrace(p)
  elif any([cmd == x for x in CMD_ATTACH_GDB]):
    attachGdb()
  elif any([cmd.startswith(x + " ") for x in CMD_BREAKPOINT]):
    handleBp(p, cmd)
  elif any([cmd.startswith(x + " ") for x in CMD_NATIVE_BP]):
    calcNativeBPoffset(cmd)
  elif cmd == CMD_INTER[0]:
    p.interactive()
    sys.exit(0)
  else:
    print("forward to jdb:")
    p.sendline(cmd)
    lines = p.recvlines(timeout=0.1)
    for l in lines:
      print(l.decode("UTF-8"))


###############################################################################
# Command Handlers

def handleQuit(p):
  print("ending jdb++")
  p.sendline(CMD_QUIT[0])
  p.close()
  sys.exit(0)

def handleBps(p):
  p.sendline(CMD_SHOW_BPS[0])
  p.readuntil("set:\n")
  set_bps = p.recvlines(timeout=0.1)

  print("Active Breakpoints:")
  # sample line
  # breakpoint com.example.firsttestapp.MainActivity.onCreate(android.os.Bundle)
  for bp in set_bps:
    print("  {}".format(bp.decode("UTF-8")[len("breakpoint "):]))

def handleLocals(p):
  printLocals(p)

def handleStepI(p):
  if defs.TRACING_ACTIVE:
    handleUnTrace(p)

  p.sendline(CMD_STEPI[0])
  handleStepCmd(p)

def handleStepU(p):
  if defs.TRACING_ACTIVE:
    handleUnTrace(p)

  p.sendline(CMD_STEPU[0])
  handleStepCmd(p)

def handleStepO(p):
  if defs.TRACING_ACTIVE:
    handleUnTrace(p)

  p.sendline(CMD_STEPO[0])
  handleStepCmd(p)

def handleCont(p):

  while True:
    p.sendline(CMD_CONT[0])
    defs.CONTINUE_CALLED = True
    if not handleStepCmd(p):
      break

def handleStepCmd(p) -> bool:
  output = p.readuntil("\n\n").decode("UTF-8")
  if defs.DEBUG_MODE: print("Output: " + output)

  # parse step line handles if tracing is active or not
  thread, function, linenum, retval = parseStepLine(output)
  debug_lines = getDebugFiles(function)

  if defs.DEBUG_MODE:
    print("Trace: {}, Cont: {}".format(defs.TRACING_ACTIVE, defs.CONTINUE_CALLED))
  if defs.TRACING_ACTIVE and defs.CONTINUE_CALLED:

    # only stop on a line which we have annotated, otherwise only print enter/exit info
    if debug_lines == None:
      if len(retval) != 0:
        print("  Exited:  {} ReturnValue: {}".format(function, retval))
      else:
        print("  Entered: {}".format(function))
      return True

  printUI(p, debug_lines, linenum, thread, function)
  defs.CONTINUE_CALLED = False
  return False

def handleBp(p, cmd):
  '''
    stop in <class id>.<method>[(argument_type,...)]   -- set a breakpoint in a method
    stop at <class id>:<line>                          -- set a breakpoint at a line
  '''
  # take current <class id> and given line

  tmp = cmd.split(" ")
  bp_line = int(tmp[1])

  p.sendline("stop at {}:{}".format(defs.debug_context.currClass(), bp_line))
  print("breakpoint set at {}:{}".format(defs.debug_context.currClass(), bp_line))

  output = p.recvlines(timeout=0.1)
  #print(output)

  # add to bp list
  if defs.debug_context.currClass() in defs.bp_dict:
    defs.bp_dict[defs.debug_context.currClass()].append(bp_line)
  else:
    defs.bp_dict[defs.debug_context.currClass()] = [bp_line]

def handleTrace(p):
  p.sendline(CMD_TRACE[0])

  # active tracing, once activated and continue is executed, we only stop at 
  # functions which we have annotated
  defs.TRACING_ACTIVE = True
  print(colored("Tracing Activated", "green", attrs=["bold"]))

def handleUnTrace(p):
  p.sendline(CMD_UNTRACE[0])
  defs.TRACING_ACTIVE = False
  print(colored("Tracing DEactivated", "green", attrs=["bold"]))
