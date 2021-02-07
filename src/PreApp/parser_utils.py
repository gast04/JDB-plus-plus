from typing import Tuple, List, Dict

from PreApp.smali_insts import *

T_VOID = "V"
T_BOOL = "Z"
T_SHORT = "S"
T_CHAR = "C"
T_BYTE = "B"
T_INT = "I"
T_LONG = "J"     # 64 bit
T_FLOAT = "F"
T_DOUBLE = "D"   # 64 bit

T_ARRAY = "["    # startwith
T_OBJECT = "L"   # startwith

# primitive types
PRIM_TYPES = [T_VOID, T_BOOL, T_SHORT, T_CHAR, T_BYTE, T_INT, T_LONG, T_FLOAT, T_DOUBLE]

class MethodParams:
  def __init__(self, params: List[str], is_static: bool):
    self.params = params

    # first param is always "this" for non static functions
    self.is_static = is_static

    self.typed_params: Dict[str, str] = {}  # variable scope: name:type
    self.size = 0

    for p in self.params:
      if self.is_static:
        self.typed_params["p{}".format(self.size)] = p
      else:
        self.typed_params["p{}".format(self.size+1)] = p

      if p in [T_LONG, T_DOUBLE]:
        self.size += 2
      else:
        self.size += 1

  def getParamsSize(self)->int:
    return self.size

  def getParamLines(self) -> List[str]:
    name_lines: List[str] = []
    
    i = 0 if self.is_static else 1

    for p in self.params:
      name_lines.append(".param p{0}, \"p{0}\"".format(i))
      i += 2 if p in [T_LONG, T_DOUBLE] else 1

    return name_lines

  def getTypedParams(self) -> Dict[str, str]:
    return self.typed_params



'''
  Examples:
  .method private calcOffset(IILjava/lang/String;)I
  .method public constructor <init>()V
  .method static synthetic access$000(Lcom/example/firsttestapp/MainActivity;)Landroid/widget/Button;
  .method private rbtnSetting()V
  .method constructor <init>(Lcom/ui/ʻ/ʼ;Landroid/widget/CheckBox;)V
  .method private ʻ(Ljava/util/jar/Manifest;Ljava/util/Map;Ljava/util/jar/JarOutputStream;JLjava/util/ArrayList;)V

  .method public constructor <init>([B[I[B[ILjava/lang/String;Z)V
  .method public constructor <init>([B[I[B[Ljava/lang/String;Z)V
  .method public constructor <init>([B[I[Ljava/lang/String;Z[B)V
  .method public constructor <init>([B[[I[[Ljava/lang/String;Z[B)V
'''
def parseMethodSignature(sig: str) -> Tuple[str, MethodParams, str, str]:

  params_raw = sig.split("(")[1].split(")")[0]

  ret_type = sig.split(")")[1]
  func_types = sig.split(" ")[1:-1]
  func_name = sig.split("(")[0].split(" ")[-1]

  params = []
  raw_str = params_raw
  while True:
    do_break = True
    for i, c in enumerate(raw_str):
      if c in PRIM_TYPES:
        params.append(c)
        continue

      if c == T_OBJECT:
        tmp = raw_str[i:].split(";")[0]
        params.append(tmp + ";")
        raw_str = raw_str[i+len(tmp)+1:]
        do_break = False
        break

      if c == T_ARRAY:
        # get dimension of array
        dim = 1
        while True:
          if raw_str[i+dim] == "[":
            dim+=1
          else:
            break

        if raw_str[i+dim] in PRIM_TYPES:
          params.append(raw_str[i:i+dim+1])
          raw_str = raw_str[i+dim+1:]
        else:
          tmp = raw_str[i:].split(";")[0]
          params.append(tmp + ";")
          raw_str = raw_str[i+len(tmp)+1:]
        do_break = False
        break

    if do_break:
      break

  parsed_params = MethodParams(params, any(['static' == x for x in func_types]))
  return func_name, parsed_params, ret_type, func_types

def parseLocal(line: str):
  var_name = line.split(" ")[1].split(",")[0]
  #if var_name[0] == "{":
  #  # filled-new-array {v2}, [Ljava/lang/String;
  #  return var_name[1:-1]
  return var_name

def parseLocals(line: str):
  tmp = line.split(" ")
  l1 = tmp[1][:-1]      # remove ","
  l2 = tmp[2]
  return l1, l2

'''
  sample: new-instance v1, Lcom/example/firsttestapp/PinHandling;
'''
def parseLocalAndObject(line:str):
  tmp = line.split(" ")
  local_name = tmp[1][:-1]
  obj = tmp[2]
  return local_name, obj


'''
  parse through function, and append locals type
'''
def sourceParserAddLocals(code_lines: List[str], params_list: MethodParams, is_static: bool) -> List[str]:

  ext_lines: List[str] = []

  # add all params to scope
  var_scope: Dict[str, str] = params_list.getTypedParams()  # variable scope: name:type

  last_code_line = ""
  for line in code_lines:
    ext_lines.append(line)

    if line.startswith(I_CONST) or line.startswith(I_CONST_I4) or \
        line.startswith(I_CONST_I8) or line.startswith(I_CONST_I16):
      local_name = parseLocal(line)
      ext_lines.append(".local {0}, \"{0}\":I".format(local_name))
      var_scope[local_name] = "I"

    elif line.startswith(I_CONST_S):
      local_name = parseLocal(line)
      ext_lines.append(".local {0}, \"{0}\":Ljava/lang/String;".format(local_name))
      var_scope[local_name] = "Ljava/lang/String;"

    elif line.startswith(I_ADD_I8):
      local_name = parseLocal(line)
      ext_lines.append(".local {0}, \"{0}\":I".format(local_name))
      var_scope[local_name] = "I"

    elif line.startswith(I_NEW_ARRAY):
      # new-array v13, v12, [B
      # v13 -> holds array
      # v12 -> array size
      local_name = parseLocal(line)
      array_type = line.split(" ")[-1]
      ext_lines.append(".local {0}, \"{0}\":{1}".format(local_name, array_type))
      var_scope[local_name] = array_type

    elif line.startswith(I_MOVE):
      local_t, local_s = parseLocals(line)

      if local_s in var_scope:
        ext_lines.append(".local {0}, \"{0}\":{1}".format(local_t, var_scope[local_s]))
        var_scope[local_t] = var_scope[local_s]

    # check-cast v1, Landroid/widget/Button;
    elif line.startswith(I_NEW_INST) or line.startswith(I_CHECK_CAST):
      local_name, obj = parseLocalAndObject(line)
      ext_lines.append(".local {0}, \"{0}\":{1}".format(local_name, obj))
      var_scope[local_name] = obj

    elif line.startswith(I_MOVE_RESULT_OBJ):
      if ")" in last_code_line:
        # invoke-static {v0, v1}, Ljavax/crypto/KeyGenerator;->getInstance(Ljava/lang/String;Ljava/lang/String;)Ljavax/crypto/KeyGenerator;
        return_type = last_code_line.split(")")[-1]
      else:
        # filled-new-array {v2}, [Ljava/lang/String;
        return_type = last_code_line.split(" ")[-1]
      local_name = parseLocal(line)
      ext_lines.append(".local {0}, \"{0}\":{1}".format(local_name, return_type))

    elif line.startswith(I_IGET_OBJ):
      # iget-object v0, p0, Lcom/example/firsttestapp/MainActivity;->btnFirstPin:Landroid/widget/Button;
      # iget-object v3, p0, Lcom/example/firsttestapp/PinHandling;->iv:[B
      local_name = parseLocal(line)
      obj_type = line.split(":")[1]
      ext_lines.append(".local {0}, \"{0}\":{1}".format(local_name, obj_type))

    elif line.startswith(I_MOVE_RESULT):
      # invoke-virtual {v3}, Ljava/lang/String;->length()I
      # move-result v6
      local_name = parseLocal(line)
      return_type = last_code_line.split(")")[1]
      ext_lines.append(".local {0}, \"{0}\":{1}".format(local_name, return_type))

    # because line numbers are added before, and ":try_end_0"-lines can occur as well
    if not line.startswith(".") and not line.startswith(":"):
      last_code_line = line

  return ext_lines


'''
  Examples:
  .class Lcom/example/firsttestapp/MainActivity$1;
  .class public Lcom/example/firsttestapp/MainActivity;
  .class public Lcom/example/firsttestapp/PinHandling;
'''
def parseClassSignature(sig:str) -> Tuple[str, str]:

  tmp = sig.split(" ")
  name = tmp[-1][1:-1]
  typ = tmp[1:-1]

  return typ, name
