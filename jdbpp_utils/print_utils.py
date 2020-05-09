from typing import Dict
from termcolor import colored

from jdbpp_utils import *
from jdbpp_utils.var_utils import variable_list
from jdbpp_utils.definitions import *

def printByteCode(debug_lines: Dict[str, str], execline: int):

  if debug_lines == None:
    print(colored("ByteCode:", "green"))
    print(colored("    not available", "red"))
    return

  # print lines, 3 before and after
  print_start  = execline - 3
  print_end  = execline + 4

  # get list of breakpoints for current class
  if debug_context.currClass() in bp_dict:
    bps = bp_dict[debug_context.currClass()]
  else:
    bps = []

  output = ""
  for ln in range(print_start, print_end):

    if str(ln) not in debug_lines:
      line_msg = "{}: ".format(str(ln)).rjust(8, " ")
      output += line_msg + "not available (out of debug line range)" + "\n"
    elif ln == execline:
      line_msg = "->{}: ".format(str(ln)).rjust(8, " ")
      output +=  colored(line_msg + debug_lines[str(ln)], "red") + "\n"
    elif ln in bps: # check if line has breakpoint
      line_msg = "* {}: ".format(str(ln)).rjust(8, " ")
      output +=  colored(line_msg + debug_lines[str(ln)], "yellow") + "\n"
    else:
      line_msg = "{}: ".format(str(ln)).rjust(8, " ")
      output += line_msg + debug_lines[str(ln)] + "\n"

  print(colored("ByteCode:", "green"))
  print(output)


def printLocals(p):
  p.sendline("locals")
  output = p.recvlines(timeout=0.1)[1:] # first line: "Method arguments:"

  variables = []
  for l in output:
    if b"Local variables:" in l:
      continue
    variables.append(l.decode("UTF-8"))
  varlist = variable_list(variables)
  print(colored("Locals:\n", "magenta") + str(varlist))
