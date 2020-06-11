from termcolor import colored
from typing import List, Dict, Tuple

from Jdbpp_utils import DebugContext

JDBPP_VERSION:str = "2.0.0" # codename quiteblue

cmd_sep_line = colored(u"\u2014"*80, "blue")  # em dash
cmd_prefix = colored("jdb++", "blue") + colored("> ", "green")
debug_files: Dict[str, Dict[str, str]] = {}
debug_context: DebugContext = DebugContext()
bp_dict: Dict[str, List[int]] = {}  # classid, breakpoints

DEBUGFILE_FOLDER:str ="DebugFiles"

CONTINUE_CALLED:bool = False
TRACING_ACTIVE:bool = False
DEBUG_MODE:bool = False
ROOTED_DEV:bool = False

APK_PID:int = 0

# Native Support Vars
NS_GDBS_DIR:str = "/data/local/tmp"
NS_GDBS_PATH:str = "/home/niku/Android/NDKs/android-ndk-r21d/prebuilt/android-arm64/gdbserver/gdbserver"
NS_GDBS_CON = None
NS_GDBS_DEV_HOST:str = "0.0.0.0"
NS_GDBS_DEV_PORT:str = "12345"

NS_GDB_LOCAL_PORT:str = "54321"
NS_GDB_CON = None
NS_GDB_TERMINAL:str = "xfce4-terminal"
NS_GDB_TERMINAL_EXEC_CMD:str = "-x"
NS_GDB_PATH:str = "/home/niku/Android/NDKs/android-ndk-r21d/prebuilt/linux-x86_64/bin/gdb"

# TODO, these might be a problem...
NS_LIB_PATH:str = "/home/niku/git-repos/JDB-plus-plus/src/TestApks/vch/lib/arm64-v8a"
NS_LIB_NAME:str = "libnative-lib.so"
