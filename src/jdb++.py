import pwn, time, re, readline, json
from termcolor import colored
import subprocess as sp

import Jdbpp_utils.definitions as defs
from Jdbpp_utils.handle_cmd import *
from Jdbpp_utils import emulatorSetup, parseJdbHeader

# TODO: parse from manifest
APP_NAME, APP_ENTRY = parseCmdArguments()

# setup debugger
print("load debug files")
loadDebugFiles()

print("Setup emulator")
emulatorSetup(APP_NAME, APP_ENTRY)

# TODO: check if some leftover gdbserver are running

# setup breakpoints
setBreakpoints()

# and finally spawn the process
print("connect to app")
cmd = ["jdb", "-connect", "com.sun.jdi.SocketAttach:hostname=localhost,port=33333"]
# this hangs, if Android Studio runs, or crashes if the APK does not have
# the debuggable flag set
if defs.DEBUG_MODE: print(" ".join(cmd))
p = pwn.process(cmd)
print("waiting")

# parse jdb header
header = p.readuntil("Breakpoint hit:", drop=True)
'''
> > Unable to set deferred breakpoint com.ui.App.onCreate(android.os.Bundle) : No method onCreate in com.ui.App

Stopping due to deferred breakpoint errors.
"thread=main", java.lang.VMClassLoader.findLoadedClass(), line=-1 bci=-1

b'main[1] > Unable to set deferred breakpoint com.air.sdk.addons.airx.AirBannerListener.onAdLoaded(android.view.View) : Breakpoints can be located only in classes.  com.air.sdk.addons.airx.AirBannerListener is an interface or array.\n\n
'''


start_line = p.readline().decode("UTF-8")
parseJdbHeader(p, header, start_line)

last_cmd = "l" # set default to locals
while True:
  print(defs.cmd_sep_line)
  cmd = input(defs.cmd_prefix).decode("UTF-8").strip()

  if len(cmd) == 0:
    # exec previous command
    cmd = last_cmd
  else:
    last_cmd = cmd

  execCmd(p,cmd)
