import re, time, json, os, sys, argparse
import subprocess as sp
from termcolor import colored
from typing import List, Dict, Tuple

class DebugContext:

  def __init__(self):
    self.thread = ""
    self.method = ""
    self.cname  = ""

  def setCurrentThread(self, thread: str):
    self.thread = thread

  def setCurrentMethod(self, method: str):
    tmp = method.split(".")
    self.method = tmp[-1]
    self.cname = '.'.join(tmp[:-1])
  
  def currMethod(self) -> str:
    return self.method

  def currClass(self) -> str:
    return self.cname

import jdbpp_utils.definitions as defs
from jdbpp_utils.print_utils import printByteCode, printLocals


def parseCmdArguments() -> Tuple[str, str]:
  global DEBUG_MODE

  parser = argparse.ArgumentParser(description='Debug APK files easily')
  parser.add_argument('-d', "--Debug", dest='debug_mode', default=False,
                      help='Enable Debug Mode', action="store_true")
  parser.add_argument('-n', "--AppName", type=str, metavar="", dest='app_name', default=None,
                      help='App Name used to start Application')
  parser.add_argument('-a', "--MainActivity", type=str, metavar="", dest='activity', default=None,
                      help='start activity of the Application')

  args = parser.parse_args()

  defs.DEBUG_MODE = args.debug_mode

  if args.app_name == None or args.activity == None:
    parser.print_help()
    sys.exit(0)
  
  return args.app_name, args.activity


def emulatorSetup(name, entry):
  p = sp.Popen(["adb", "shell", "pm", "clear", name], stdout=sp.PIPE)
  p.wait()

  p = sp.Popen(["adb", "shell", "am", "start", "-D", "-n", name+"/."+entry], stdout=sp.PIPE)
  p.wait()
  time.sleep(0.5)

  p = sp.Popen(["adb", "shell", "ps"], stdout=sp.PIPE)
  p.wait()

  processes = p.stdout.readlines()
  for proc in processes:
    if name in str(proc):
      break

  if len(processes) == 0:
    print("NO emulator or devices found")
    sys.exit(0)

  m = re.search("[\ ]+[0-9]+[\ ]",str(proc))
  pid = int(m.group(0).strip())

  p = sp.Popen(["adb", "forward", "tcp:33333", "jdwp:{}".format(pid)])
  p.wait()

'''
  load all debug files prepared from the PreApp analyzer
'''
def loadDebugFiles():
  for root_dir, dirs, files in os.walk(defs.DEBUGFILE_FOLDER):
    for f in files:
      with open(os.path.join(root_dir, f), "r+") as fd:
        defs.debug_files[os.path.join(root_dir, f)[len(defs.DEBUGFILE_FOLDER)+1:]] = json.load(fd)


def getDebugFiles(parsed_class:str) -> Dict[str, str]:

  dbg_file = "/".join(parsed_class.split(".")[:-1]) + ".debug"
  if defs.DEBUG_MODE:
    print("dbg_file: {}".format(dbg_file))

  # go through smali folders and see where it exists
  for d in os.listdir(defs.DEBUGFILE_FOLDER):
    if not d.startswith("smali"):
      continue

    if os.path.exists(os.path.join(defs.DEBUGFILE_FOLDER, d, dbg_file)):
      return defs.debug_files[os.path.join(d, dbg_file)]

  return None


def parseJdbHeader(p, header, start_line):
  # print header
  print("\nJDB-Header:")
  for l in header.split(b"\n"):
    l = l.decode("UTF-8")
    if len(l) == 0:
      continue
    print("  " + l)
  p.readline() # read empty newline
  print("")

  #print("\nparsing breakpoint line: {}".format(start_line))

  # pares breakpoint line, to init context
  thread, function, linenum, _ = parseStepLine(start_line)
  debug_lines = getDebugFiles(function)

  print(colored("Thread: ","cyan") + thread + ", " + colored("Function: ", "cyan") + function)
  printLocals(p)
  printByteCode(debug_lines, linenum)

'''
  TODO: setup breakpoints:
  * on entry
  * on every button call
'''
def setBreakpoints():
  # parse layout folder and search for all Buttons and if they have an "onClick"-tag we
  # add a breakpoint there
  
  # TODO: see develop.py

  layout_folder = "res/layout"
  pass


def parseStepLine(line: str) -> Tuple[str, str, int, str]:
  
  # parse output line, like
  # Step completed: "thread=main", com.example.firsttestapp.MainActivity.onCreate(), line=21 bci=3

  # Method entered: "thread=main", android.app.Activity.getWindow(), line=939 bci=0
  # Method exited: return value = instance of com.android.internal.policy.PhoneWindow(id=11073), "thread=main", android.app.Activity.getWindow(), line=939 bci=2

  # > Method exited: return value = <void value>, "thread=main", android.os.Parcel.freeBuffer(), line=2,985 bci=17

  # Method exited: return value = "DexPathList[[zip file "/system/framework/org.apache.http.legacy.boot.jar", zip file "/data/app/ru.LCqASDGk.nGHqpcNnA-tyJA60rCNmGWVcRoIzQFcg==/base.apk"],nativeLibraryDirectories=[/data/app/ru.LCqASDGk.nGHqpcNnA-tyJA60rCNmGWVcRoIzQFcg==/lib/x86, /system/lib]]", "thread=main", dalvik.system.DexPathList.toString(), line=201 bci=65

  if line.startswith("> "):
    line = line[2:]

  retval = ""
  if line.startswith("Method exited:"):
    start_tag = "return value = "
    end_tag = ' "thread='
    retval = re.search("{}.*{}".format(start_tag, end_tag), line).group(0)[len(start_tag):-len(end_tag)+1]

  thread = line.split('"thread=')[1].split('"')[0]
  function = re.search(", .*, line", line.split('"thread=')[1]).group(0)[2:-6]

  # linenum above 999 -> 2,909
  tmp_linenum = re.search(", line=[0-9,-]* bci=", line).group(0)[7:-4].replace(",","")
  linenum = int(tmp_linenum)

  # directly set debug_context
  defs.debug_context.setCurrentThread(thread)
  defs.debug_context.setCurrentMethod(function)

  if defs.DEBUG_MODE:
    print("parsed line: {} {} {} {}".format(thread, function, linenum, retval))

  return thread, function, linenum, retval
