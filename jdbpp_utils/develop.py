import os, json
import xml.etree.ElementTree as ET

from typing import List

'''
  simply parse line by line
'''
def parseXMLfile(fd):
  lines = fd.readlines()
  handlers = []

  for line in lines:
    if "<Button" not in line or "android:onClick=" not in line:
      continue
    hd = line.split('android:onClick="')[1].split('"')[0]
    handlers.append(hd)

  return handlers

def getBpOnButtonHandlesOLD() -> List[str]:
  button_click_functions: List[str] = []

  layout_folder = "../TestApks/app-debug/res/layout"

  for fxml in os.listdir(layout_folder):
    if fxml.startswith("abc_") or fxml.startswith("design_") or fxml.startswith("notification_"):
      continue

    with open(os.path.join(layout_folder, fxml), "r+") as fd:
      hds = parseXMLfile(fd)
    
    button_click_functions += hds

  # unique list
  btn_handlers = list(set(button_click_functions))
  print(btn_handlers)
  print()

  # now find all implementations
  # all handler functions must have the signature <name>(Landroid/view/View;)V

  with open("../ParsedClasses.debug", "r+") as fd:
    parsed_classes = json.load(fd)

  bp_lines:List[str] = []
  for sc in parsed_classes:
    for mname, mparams, mret_type, m_type in parsed_classes[sc]:
      if mname in btn_handlers and mparams[0] == "Landroid/view/View;":
        bp_lines.append("stop in {}.{}({})\n".format(sc.replace("/","."), mname, mparams[0].replace("/",".")[1:-1]))

  return bp_lines

def getBpOnButtonHandles() -> List[str]:

  ret: List[str] = []

  with open("ParsedClasses.debug", "r+") as fd:
    parsed = json.load(fd)

  for sclass in parsed:
    for smethod in parsed[sclass]:

      # only one parameter
      if len(smethod[1]) != 1:
        continue
      
      # return type must be void
      if smethod[2] != 'V':
        continue
      
      # avoid android functions
      if sclass.startswith("android"):
        continue
      
      # parameter has to be Landroid/view/View;
      if smethod[1][0] == "Landroid/view/View;":
        ret.append("stop in " + sclass.replace("/",".")+"."+smethod[0]+"(android.view.View)\n")

  return ret

def getBpOnCreate() -> List[str]:
  bp_lines = ["stop in com.example.firsttestapp.MainActivity.onCreate(android.os.Bundle)"]
  bp_lines = ["stop in com.ui.App.onCreate(android.os.Bundle)\n",
    "stop in ru.LCqASDGk.nGHqpcNnA.MainActivity.onCreate(android.os.Bundle)\n",
    "stop in com.ui.InstallApp.onCreate(android.os.Bundle)\n",
    "stop in com.ui.HelpCommon.onCreate(android.os.Bundle)\n",
    "stop in com.ui.HelpCustom.onCreate(android.os.Bundle)\n",
    "stop in com.ui.PackageChangeReceiver.onCreate(android.os.Bundle)\n"]
  return bp_lines

def setBreakpoints():
  # parse layout folder and search for all Buttons and if they have an "onClick"-tag we
  # add a breakpoint there
  bp_lines = getBpOnButtonHandles()
  bp_lines += getBpOnCreate()

  with open(os.path.join(os.path.expanduser("~"), ".jdbrc"), "w+") as fd:
    fd.writelines(bp_lines)

setBreakpoints()

# I dont know whats the best way for automatic breakpoints,
# probably to add it manually into the .jdbrc file
