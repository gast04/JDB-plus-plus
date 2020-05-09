from typing import List

class variable:

  def __init__(self, name: str, value: str):
    self.name = name

    if value.isdigit():
      self.value = int(value)
      self.isint = True
    else:
      self.value = value
      self.isint = False

class variable_list:

  def __init__(self, raw_varlist:List[str]):
    self.varlist:List[variable] = []

    last_var = ""
    for v in raw_varlist:
      tmp = v.split(" ")
      if tmp[1] != "=": # needed for multiline strings
          self.varlist[-1] = variable(last_var, self.varlist[-1].value + "\n" + v)
      else:
          self.varlist.append(variable(tmp[0], ' '.join(tmp[2:])))
          last_var = tmp[0]

    '''
    try:
      for v in raw_varlist:
        tmp = v.split(" = ")
        self.varlist.append(variable(tmp[0], tmp[1]))
    except:
      print("ERROR: in varlist")
      print("INPUT: {}".format(raw_varlist))
    '''

  def size(self)-> int:
    return len(self.varlist)

  def __str__(self):
    ret = ""
    for v in self.varlist:
      ret += (v.name).rjust(7, " ") + " = "
      if v.isint:
        ret += hex(v.value) + "\n"
      else:
        ret += v.value + "\n"

    return ret[:-1] # remove last "\n"
