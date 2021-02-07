import json, os, sys
from typing import List, Dict

from PreApp.parser_utils import *

CLASS_PREFIX  = ".class"
SUPER_PREFIX  = ".super"
SOURCE_PREFIX = ".source"
IMPL_PREFIX   = ".implements"
FIELD_PREFIX  = ".field"
FIELD_END     = ".end field"
METHOD_START  = ".method"
METHOD_END    = ".end method"
LOCALS        = ".locals"
LINE_NUM      = ".line"
PARAM_PREFIX  = ".param"
LOCAL_PREFIX  = ".local "  # space to distinguish between locals
ANNO_START    = ".annotation"
ANNO_END      = ".end annotation"
SWITCH_START  = ".sparse-switch"
SWITCH_END    = ".end sparse-switch"
ARRAY_START   = ".array-data"
ARRAY_END     = ".end array-data"

'''
  get difference of:
    .param p2,"p2"
    .param p2    # Ljava/io/IOException;
'''
def isParamDef(line:str):
  if "," in line:
    return True
  return False


class SmaliMethod:

  def __init__(self, code_lines:List[str]):

    self.code_lines = code_lines
    n, p, r, t = parseMethodSignature(self.code_lines[0])
    self.params = p
    self.ret_type = r
    self.func_type = t
    self.func_name = n
    self.is_static = any(['static' == x for x in self.func_type])
    self.ext_lines: List[str] = []        # code_lines with linenumbers and extensions
    self.debug_lines: Dict[int, str] = {} # linenum, code

  def paramCount(self) -> int:
    return self.params.getParamsSize()

  def getParams(self) -> MethodParams:
    return self.params

  def getRetType(self) -> str:
    return self.ret_type

  def getCodeLines(self) -> List[str]:
    return self.code_lines

  def addLineNumers(self, num_start: int) -> int:
    line_num = num_start

    avoid_lines = False
    for line in self.code_lines:

      if line.startswith(ANNO_END):
        avoid_lines = False
      if line.startswith(ANNO_START):
        avoid_lines = True

      if line.startswith(SWITCH_START):
        avoid_lines = True
      if line.startswith(SWITCH_END):
        avoid_lines = False

      if line.startswith(ARRAY_START):
        avoid_lines = True
      if line.startswith(ARRAY_END):
        avoid_lines = False

      if line.startswith(".") or line.startswith(":") or avoid_lines:  # or line.startswith("goto") -> bad when in loop
        self.ext_lines.append(line)
        continue

      self.ext_lines.append(".line {}".format(line_num))
      self.ext_lines.append(line)
      self.debug_lines[line_num] = line
      line_num += 1

    return line_num

  def addParamsDef(self):

    # .param p1, "savedInstanceState"
    # add param names to function
    for i, line in enumerate(self.ext_lines):
      if not line.startswith(LOCALS):
        continue

      param_lines = self.params.getParamLines()

      # add params to extended code lines
      self.ext_lines = self.ext_lines[:i+1] + param_lines + self.ext_lines[i+1:]
      break

  def addLocalsDef(self):
    self.ext_lines = sourceParserAddLocals(self.ext_lines, self.params, self.is_static)


  def __str__(self) -> str:

    if len(self.ext_lines) == 0:
      self.ext_lines = self.code_lines

    m_str = self.ext_lines[0] + "\n"
    for line in self.ext_lines[1:-1]:
      m_str += "    " + line + "\n"
    m_str += self.ext_lines[-1] + "\n"

    return m_str

class SmaliClass:

  def __init__(self, code: List[str]):

    self.class_name = ""
    self.super_class = ""
    self.source = ""
    self.implements: List[str] = []
    self.annotations: List[List[str]] = []
    self.fields: List[str] = []
    self.methods: Dict[str, SmaliMethod] = {}  # name, method_class
    self.debug_lines: Dict[int, str] = {}    # line_num, code_line

    # remove starting spaces
    code_lines = [x.strip() for x in code]

    cont1 = self.__parseClassDefs(code_lines)
    t, n = parseClassSignature(self.class_name)
    self.name = n
    self.type = t

    # check if file contains only definitions
    if cont1 == -1:
      return

    cont2 = self.__parseFields(code_lines[cont1:])
    if cont2 == -1:
      return

    self.__parseMethods(code_lines[cont1+cont2:])

  def __parseClassDefs(self, code_lines: List[str]) -> int:

    curr_anno: List[str] = []
    in_anno = False

    for i, line in enumerate(code_lines):

      if in_anno:
        curr_anno.append(line)
      if line.startswith(ANNO_END):
        in_anno = False
        self.annotations.append(curr_anno.copy())
        curr_anno = []
        continue

      if line.startswith(CLASS_PREFIX):
        self.class_name = line
      elif line.startswith(SUPER_PREFIX):
        self.super_class = line
      elif line.startswith(SOURCE_PREFIX):
        self.source = line
      elif line.startswith(IMPL_PREFIX):
        self.implements.append(line)
      elif line.startswith(ANNO_START):
        curr_anno.append(line)
        in_anno = True
      elif line.startswith(FIELD_PREFIX):
        return i
      elif line.startswith(METHOD_START):
        return i

    return -1

  def __parseFields(self, code_lines: List[str]) -> int:

    current_field = ""

    for i, line in enumerate(code_lines):
      if line.startswith(FIELD_PREFIX):
        if len(current_field) != 0:
          self.fields.append(current_field)

        current_field = line

      elif line.startswith(FIELD_END):
        current_field += "\n" + line
        self.fields.append(current_field)
        current_field = ""

      elif line.startswith(METHOD_START):
        if len(current_field) != 0:
          self.fields.append(current_field)
        return i

      elif line.startswith("#") or len(line.strip()) == 0:
          continue # filter comments and empty lines

      else:
        current_field += "\n" + line

    self.fields.append(current_field)
    return -1

  def __parseMethods(self, code_lines: List[str]):

    curr_method: List[str] = []
    method_name = ""

    code_line_num = 1

    in_method = False
    for line in code_lines:

      if line.startswith(METHOD_END):
        curr_method.append(line)

        # create method and extend it
        self.methods[method_name] = SmaliMethod(curr_method.copy())
        code_line_num = self.methods[method_name].addLineNumers(code_line_num)
        self.methods[method_name].addParamsDef()
        self.methods[method_name].addLocalsDef()

        curr_method = []
        in_method = False
        continue

      if line.startswith(METHOD_START):
        method_name = line
        curr_method.append(line)
        in_method = True
        continue

      if not in_method:
        continue
      if line.startswith(LINE_NUM):
        continue
      if line.startswith(PARAM_PREFIX):
        if isParamDef(line):  # distinguish between param block
          continue
      if line.startswith(LOCAL_PREFIX):
        continue
      if len(line) == 0:
        continue

      # append hopefully only code lines
      curr_method.append(line)

  def writeToFile(self, filepath):

    outfile = open(filepath, "w+")

    outfile.write(self.class_name + "\n")
    outfile.write(self.super_class + "\n")
    outfile.write(self.source + "\n")

    for impl in self.implements:
      outfile.write(impl + "\n")
    outfile.write("\n")

    for anno in self.annotations:
      for a in anno:
        outfile.write(a + "\n")
      outfile.write("\n")
    outfile.write("\n")

    for field in self.fields:
      outfile.write(field + "\n") # + "\n\n")
    outfile.write("\n")

    for m in self.methods:
      outfile.write(str(self.methods[m]) + "\n")

    outfile.close()

  def storeDebugLines(self, filepath):

    if os.path.exists(filepath):
      print("ERROR: overwriting file: {}".format(filepath))
      sys.exit(-1)

    output_lines = ""
    combined_lines = {}
    for m in self.methods:
      combined_lines.update(self.methods[m].debug_lines)
      #for dl in self.methods[m].debug_lines:
      #  output_lines += "{} {}\n".format(dl, self.methods[m].debug_lines[dl])

    with open(filepath, "w+") as f:
      json.dump(combined_lines, f)
      # f.write(output_lines)
