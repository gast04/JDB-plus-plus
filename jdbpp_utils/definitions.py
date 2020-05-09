from termcolor import colored
from typing import List, Dict, Tuple

from jdbpp_utils import DebugContext

cmd_sep_line = colored(u"\u2014"*80, "blue")  # em dash
cmd_prefix = colored("jdb++", "blue") + colored("> ", "green")
debug_files: Dict[str, Dict[str, str]] = {}
debug_context: DebugContext = DebugContext()
bp_dict: Dict[str, List[int]] = {}  # classid, breakpoints

DEBUGFILE_FOLDER:str ="DebugFiles"

CONTINUE_CALLED:bool = False
TRACING_ACTIVE:bool = False
DEBUG_MODE:bool = False
