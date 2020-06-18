import r2pipe, os, sys
import subprocess as sp

import Jdbpp_utils.definitions as defs

# TODO:
# copy gdbserver to /data/local/tmp
# start and attach to process

# start new terminal and start gdb client
# get load address
# calc offsets to breakpoints and set

# TODO: r2
# get entry address
# get functions starting with "Java_"     suppose those are self implemented

def attachGdb():

  if defs.ROOTED_DEV:
    p = sp.Popen(["adb", "shell"], stdout=sp.PIPE, stdin=sp.PIPE)
    p.stdin.write(b"su\n")
    p.stdin.write("ls {}\n".format(defs.NS_GDBS_DIR).encode("UTF-8"))
    resp = p.communicate()[0]
  elif defs.EMULATOR:
    # make sure Fadbd runs as root (haven't tested without root)
    if defs.DEBUG_MODE: print("running adbd as root")
    p = sp.Popen(["adb", "root"], stdout=sp.PIPE, stdin=sp.PIPE, stderr=sp.PIPE)
    p.wait()

    cmd = ["adb", "shell", "ls", defs.NS_GDBS_DIR]
    p = sp.Popen(cmd, stdout=sp.PIPE, stdin=sp.PIPE, stderr=sp.PIPE)
    resp = p.stdout.read()
  else:
    print("Running on unrooted Device?")
    print("I dont know if this will work, not tested")
    print("exit before something breaks")
    sys.exit(0)

  files = resp.split(b"\n")

  new_gdbs = False
  if(any([b"gdbserver" == f for f in files])):
    print("Found gdbserver on Phone")
  else:
    # TODO: get architecture
    if defs.ROOTED_DEV:
      print("pushing {} to {}".format(defs.NS_GDBS_PATH_ARM64, defs.NS_GDBS_DIR))
      cmd = ["adb", "push", defs.NS_GDBS_PATH_ARM64, defs.NS_GDBS_DIR]
    else:
      print("pushing {} to {}".format(defs.NS_GDBS_PATH_X86, defs.NS_GDBS_DIR))
      cmd = ["adb", "push", defs.NS_GDBS_PATH_X86, defs.NS_GDBS_DIR]

    p = sp.Popen(cmd)
    p.wait(1)
    new_gdbs = True

    if new_gdbs:
      if defs.ROOTED_DEV:
        p = sp.Popen(["adb", "shell"], stdout=sp.PIPE, stdin=sp.PIPE)
        p.stdin.write(b"su\n")
        p.stdin.write("chmod +x {}/gdbserver\n".format(defs.NS_GDBS_DIR).encode("UTF-8"))
        p.communicate()
      else:
        cmd = ["adb", "shell", "chmod", "+x", "{}/gdbserver".format(defs.NS_GDBS_DIR)]
        p = sp.Popen(cmd, stdout=sp.PIPE, stdin=sp.PIPE)
        p.wait(1)

  # starting gdbserver and attaching to process
  if defs.ROOTED_DEV:
    defs.NS_GDBS_CON = sp.Popen(["adb", "shell"], stderr=sp.PIPE, stdout=sp.PIPE, stdin=sp.PIPE)
    defs.NS_GDBS_CON.stdin.write(b"su\n")
    defs.NS_GDBS_CON.stdin.write("{}/gdbserver --attach {}:{} {}\n".format(
        defs.NS_GDBS_DIR, defs.NS_GDBS_DEV_HOST, 
        defs.NS_GDBS_DEV_PORT, str(defs.APK_PID)).encode("UTF-8"))
    defs.NS_GDBS_CON.stdin.flush()
  else:
      cmd = ["adb", "shell", "{}/gdbserver".format(defs.NS_GDBS_DIR),
          "--attach", "{}:{} {}".format(
          defs.NS_GDBS_DEV_HOST, defs.NS_GDBS_DEV_PORT, str(defs.APK_PID))]
      if defs.DEBUG_MODE: print(" ".join(cmd))
      defs.NS_GDBS_CON = sp.Popen(cmd, stderr=sp.PIPE, stdout=sp.PIPE, stdin=sp.PIPE)

  if defs.DEBUG_MODE: print("started gdbserver")

  # forward adb port
  cmd = ["adb", "forward",
    "tcp:{}".format(defs.NS_GDB_LOCAL_PORT),  # PC/Localhost PORT
    "tcp:{}".format(defs.NS_GDBS_DEV_PORT)]   # Device PORT
  p = sp.Popen(cmd)
  if defs.DEBUG_MODE: print(" ".join(cmd))
  p.wait()

  cmd = [defs.NS_GDB_TERMINAL, defs.NS_GDB_TERMINAL_EXEC_CMD,
    defs.NS_GDB_PATH, "-q",
    # set solib-search-path and sysroot to avoid loading/fetching all libraries
    "--eval-command=set auto-solib-add on",
    "--eval-command=set solib-search-path {}".format(defs.NS_LIB_PATH),
    "--eval-command=set sysroot {}".format(defs.NS_LIB_PATH),
    "--eval-command=target remote localhost:{}".format(defs.NS_GDB_LOCAL_PORT),
    "--eval-command=sharedlibrary"  # load symbols of custom libraries
  ]
  if defs.DEBUG_MODE: print("Terminal cmd: " + ' '.join(cmd))
  defs.NS_GDB_CON = sp.Popen(cmd, stdout=sp.PIPE, stdin=sp.PIPE)


def calcNativeBPoffset(jdb_cmd):

  # parse address from cmd
  load_addr = int(jdb_cmd.split(" ")[-1],16)

  # load native library and get "Java_" prefixed functions
  if defs.DEBUG_MODE:
    print("loading binary into radare2 and extracting exports")
    print("this may take a while...")
  r2p = r2pipe.open(os.path.join(defs.NS_LIB_PATH, defs.NS_LIB_NAME))
  r2p.cmdj("iEj")
  exports = r2p.cmdj("iEj")

  java_funcs = []
  for e in exports: 
    if "Java_" in e['name']:
      java_funcs.append(e)

  '''
  sample r2 export entry
  {
    'name': 'Java_com_denuvo_vch_MainActivity_doFloatCalc',
    'flagname': 'sym.Java_com_denuvo_vch_MainActivity_doFloatCalc',
    'realname': 'Java_com_denuvo_vch_MainActivity_doFloatCalc',
    'ordinal': 257,
    'bind': 'GLOBAL',
    'size': 128,
    'type': 'FUNC',
    'vaddr': 203256,
    'paddr': 203256,
    'is_imported': False
  }
  '''

  # get entry0 address
  r2p.cmd("aa") # this may take a while...

  # grepping with json not working, so parsing manually r2 output
  entry_raw = r2p.cmd("afl ~entry0")
  entry_addr = int(entry_raw.split(" ")[0], 16)

  for f in java_funcs:
    print("Addr: {}    {}".format(hex(load_addr - entry_addr + f['vaddr']), f['realname']))
