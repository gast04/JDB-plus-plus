import os, sys, json, shutil
from typing import Dict, List, Any

from PreApp import createStoreFolder, parseCmdArguments, debugfiles_folder
from PreApp.smali_parser import SmaliClass

# prepare app for debugger
# * set debuggable flag
# * add line numbers      DONE
# * add param names       DONE
# * add ."local v2, "v2":Ljava/lang/String;"    DONE

# TODO: parsing manifest
# TODO: parse application main folder
#       -> don't parse library folders for now

# command line arguemnts
decomp_path = parseCmdArguments()

# TODO: parse from manifest file
MAIN_PATH = ""
#MAIN_PATH = ""  # anotate everything

# TODO: get via testing all smali folders
SMALI_DIR = "smali_classes2"
#SMALI_DIR = "smali"

smali_dirs = [x for x in os.listdir(decomp_path) if x.startswith("smali")]

# exclude ressources
EXCLUDE_FILES = ["R.smali", "BuildConfig.smali"]
EXCLUDE_STARTS = ["R$"]

dir_path = os.path.join(decomp_path, SMALI_DIR)
parsed_classes: List[SmaliClass] = []

# delete old debug files
if os.path.exists(debugfiles_folder):
  shutil.rmtree(debugfiles_folder)
os.mkdir(debugfiles_folder)

# parse through smali files
for smali_dir in smali_dirs:

  # check if assets files do even contain code
  if "assets" in smali_dir:
    continue

  for root_dir, dirs, files in os.walk(os.path.join(decomp_path, smali_dir)):
    for f in files:
      
      if root_dir[len(os.path.join(decomp_path, smali_dir)):].startswith("/android"):
        continue
      
      print(root_dir[len(os.path.join(decomp_path, smali_dir)):])
      print("Prepare File: {}".format(os.path.join(root_dir, f)))

      # replace smali extension with debug
      f_debug = f[:-5] + "debug"

      if f in EXCLUDE_FILES:
        continue
      if f.startswith("R$"):
        continue

      with open(os.path.join(root_dir, f), "r+") as ff:
        smali_lines = ff.readlines()

      smali_class = SmaliClass(smali_lines)
      smali_class.writeToFile(os.path.join(root_dir, f)) # append ".mod" for non overwriting

      # we have to store in same folder structure as given
      store_dir = os.path.join("DebugFiles", root_dir[root_dir.find(smali_dir):])
      createStoreFolder(store_dir)
      store_path = os.path.join(store_dir, f_debug)

      smali_class.storeDebugLines(store_path)
      parsed_classes.append(smali_class)


# store information about classes, to avoid going through the classes in the debugger again
dump_dict: Dict[str, List[Any]] = {}
for sclass in parsed_classes:

  # dict[class] = [methods] methods = [name, params, ret_type, func_type]

  dump_dict[sclass.name] = []
  for m in sclass.methods:
    sm = sclass.methods[m]
    dump_dict[sclass.name].append([sm.func_name, sm.params.params, sm.ret_type, sm.func_type])

with open("ParsedClasses.debug", "w+") as fd:
  json.dump(dump_dict, fd)


'''
    invoke-virtual {v3}, Landroid/os/Parcel;->readString()Ljava/lang/String;
    :try_end_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_0
    .line 59
    .local v0, "v0"::try_end_0
    move-result-object v0
'''

# wrong addition of local

'''
orig:
    .line 82
    invoke-virtual {v3}, Landroid/os/Parcel;->readString()Ljava/lang/String;
    :try_end_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_0

    move-result-object v0
'''

'''
stop in com.chelpus.ˆ:25458   - runtime check

'''


'''
05-07 23:13:28.217 25379 25379 D AndroidRuntime: Shutting down VM
05-07 23:13:28.218 25379 25379 E AndroidRuntime: FATAL EXCEPTION: main
05-07 23:13:28.218 25379 25379 E AndroidRuntime: Process: ru.LCqASDGk.nGHqpcNnA, PID: 25379
05-07 23:13:28.218 25379 25379 E AndroidRuntime: java.lang.ClassCastException: android.support.v7.view.menu.ActionMenuItemView cannot be cast to android.support.v7.view.menu.ٴ$ʻ
05-07 23:13:28.218 25379 25379 E AndroidRuntime: 	at android.support.v7.view.menu.ʼ.ʼ(BaseMenuPresenter.java:131)
05-07 23:13:28.218 25379 25379 E AndroidRuntime: 	at android.support.v7.view.menu.ʼ.ʻ(BaseMenuPresenter.java:28)
05-07 23:13:28.218 25379 25379 E AndroidRuntime: 	at android.support.v7.widget.ʾ.ʻ(ActionMenuPresenter.java:59)
05-07 23:13:28.218 25379 25379 E AndroidRuntime: 	at android.support.v7.widget.ʾ.ʻ(ActionMenuPresenter.java:352)
05-07 23:13:28.218 25379 25379 E AndroidRuntime: 	at android.support.v7.view.menu.ˉ.ˋ(MenuBuilder.java:1183)
05-07 23:13:28.218 25379 25379 E AndroidRuntime: 	at android.support.v7.view.menu.ʼ.ʻ(BaseMenuPresenter.java:63)
05-07 23:13:28.218 25379 25379 E AndroidRuntime: 	at android.support.v7.widget.ʾ.ʻ(ActionMenuPresenter.java:194)
05-07 23:13:28.218 25379 25379 E AndroidRuntime: 	at android.support.v7.view.menu.ˉ.ʾ(MenuBuilder.java:162)
05-07 23:13:28.218 25379 25379 E AndroidRuntime: 	at android.support.v7.view.menu.ˉ.ʻ(MenuBuilder.java:797)
05-07 23:13:28.218 25379 25379 E AndroidRuntime: 	at android.support.v7.view.menu.ˉ.ˉ(MenuBuilder.java:1130)
05-07 23:13:28.218 25379 25379 E AndroidRuntime: 	at android.support.v7.app.ᐧ.ˊ(ToolbarActionBar.java:172)
05-07 23:13:28.218 25379 25379 E AndroidRuntime: 	at android.support.v7.app.ᐧ$1.run(ToolbarActionBar.java:5)
05-07 23:13:28.218 25379 25379 E AndroidRuntime: 	at android.os.Handler.handleCallback(Handler.java:873)
05-07 23:13:28.218 25379 25379 E AndroidRuntime: 	at android.os.Handler.dispatchMessage(Handler.java:99)
05-07 23:13:28.218 25379 25379 E AndroidRuntime: 	at android.os.Looper.loop(Looper.java:193)
05-07 23:13:28.218 25379 25379 E AndroidRuntime: 	at android.app.ActivityThread.main(ActivityThread.java:6669)
05-07 23:13:28.218 25379 25379 E AndroidRuntime: 	at java.lang.reflect.Method.invoke(Native Method)
05-07 23:13:28.218 25379 25379 E AndroidRuntime: 	at com.android.internal.os.RuntimeInit$MethodAndArgsCaller.run(RuntimeInit.java:493)
05-07 23:13:28.218 25379 25379 E AndroidRuntime: 	at com.android.internal.os.ZygoteInit.main(ZygoteInit.java:858)
05-07 23:13:28.218 25379 25379 I System.out: LP:FATAL Exception LP java.lang.ClassCastException: android.support.v7.view.menu.ActionMenuItemView cannot be cast to android.support.v7.view.menu.ٴ$ʻ
05-07 23:13:28.218 25379 25379 I System.out: LP:Lucky Patcher not found utils.
05-07 23:13:28.218 25379 25379 I chatty  : uid=10123(ru.LCqASDGk.nGHqpcNnA) identical 1 line
05-07 23:13:28.219 25379 25379 I System.out: LP:Lucky Patcher not found utils.
05-07 23:13:28.220 25379 25379 I System.out: LP:...rrunning my app...

05-07 23:13:28.221 25379 25379 W System.err: java.lang.ClassCastException: android.support.v7.view.menu.ActionMenuItemView cannot be cast to android.support.v7.view.menu.ٴ$ʻ
05-07 23:13:28.221 25379 25379 W System.err: 	at android.support.v7.view.menu.ʼ.ʼ(BaseMenuPresenter.java:131)
05-07 23:13:28.221 25379 25379 W System.err: 	at android.support.v7.view.menu.ʼ.ʻ(BaseMenuPresenter.java:28)
05-07 23:13:28.221 25379 25379 W System.err: 	at android.support.v7.widget.ʾ.ʻ(ActionMenuPresenter.java:59)
05-07 23:13:28.221 25379 25379 W System.err: 	at android.support.v7.widget.ʾ.ʻ(ActionMenuPresenter.java:352)
05-07 23:13:28.221 25379 25379 W System.err: 	at android.support.v7.view.menu.ˉ.ˋ(MenuBuilder.java:1183)
05-07 23:13:28.221 25379 25379 W System.err: 	at android.support.v7.view.menu.ʼ.ʻ(BaseMenuPresenter.java:63)
05-07 23:13:28.221 25379 25379 W System.err: 	at android.support.v7.widget.ʾ.ʻ(ActionMenuPresenter.java:194)
05-07 23:13:28.221 25379 25379 W System.err: 	at android.support.v7.view.menu.ˉ.ʾ(MenuBuilder.java:162)
05-07 23:13:28.221 25379 25379 W System.err: 	at android.support.v7.view.menu.ˉ.ʻ(MenuBuilder.java:797)
05-07 23:13:28.221 25379 25379 W System.err: 	at android.support.v7.view.menu.ˉ.ˉ(MenuBuilder.java:1130)
05-07 23:13:28.221 25379 25379 W System.err: 	at android.support.v7.app.ᐧ.ˊ(ToolbarActionBar.java:172)
05-07 23:13:28.222 25379 25379 W System.err: 	at android.support.v7.app.ᐧ$1.run(ToolbarActionBar.java:5)
05-07 23:13:28.222 25379 25379 W System.err: 	at android.os.Handler.handleCallback(Handler.java:873)
05-07 23:13:28.222 25379 25379 W System.err: 	at android.os.Handler.dispatchMessage(Handler.java:99)
05-07 23:13:28.222 25379 25379 W System.err: 	at android.os.Looper.loop(Looper.java:193)
05-07 23:13:28.222 25379 25379 W System.err: 	at android.app.ActivityThread.main(ActivityThread.java:6669)
05-07 23:13:28.222 25379 25379 W System.err: 	at java.lang.reflect.Method.invoke(Native Method)
05-07 23:13:28.222 25379 25379 W System.err: 	at com.android.internal.os.RuntimeInit$MethodAndArgsCaller.run(RuntimeInit.java:493)
05-07 23:13:28.222 25379 25379 W System.err: 	at com.android.internal.os.ZygoteInit.main(ZygoteInit.java:858)
05-07 23:13:28.227 25379 25399 I System.out: LP:Lucky Patcher: add new pkg name com.android.nfc
05-07 23:13:28.241 25379 25379 W System.err: java.io.IOException: Cannot run program "su": error=13, Permission denied
05-07 23:13:28.241 25379 25379 W System.err: 	at java.lang.ProcessBuilder.start(ProcessBuilder.java:1050)
05-07 23:13:28.241 25379 25379 W System.err: 	at java.lang.Runtime.exec(Runtime.java:695)
05-07 23:13:28.241 25379 25379 W System.err: 	at java.lang.Runtime.exec(Runtime.java:525)
05-07 23:13:28.241 25379 25379 W System.err: 	at java.lang.Runtime.exec(Runtime.java:422)
05-07 23:13:28.242 25379 25379 W System.err: 	at com.ui.ˑ.ʻ(LogCollector.java:289)
05-07 23:13:28.242 25379 25379 W System.err: 	at com.ui.ˑ.ʻ(LogCollector.java:673)
05-07 23:13:28.242 25379 25379 W System.err: 	at com.ui.App$1.uncaughtException(App.java:132)
05-07 23:13:28.242 25379 25379 W System.err: 	at java.lang.ThreadGroup.uncaughtException(ThreadGroup.java:1068)
05-07 23:13:28.242 25379 25379 W System.err: 	at java.lang.ThreadGroup.uncaughtException(ThreadGroup.java:1063)
05-07 23:13:28.242 25379 25379 W System.err: 	at java.lang.Thread.dispatchUncaughtException(Thread.java:1955)
05-07 23:13:28.242 25379 25379 W System.err: Caused by: java.io.IOException: error=13, Permission denied
05-07 23:13:28.242 25379 25379 W System.err: 	at java.lang.UNIXProcess.forkAndExec(Native Method)
05-07 23:13:28.243 25379 25379 W System.err: 	at java.lang.UNIXProcess.<init>(UNIXProcess.java:133)
05-07 23:13:28.243 25379 25379 W System.err: 	at java.lang.ProcessImpl.start(ProcessImpl.java:132)
05-07 23:13:28.243 25379 25379 W System.err: 	at java.lang.ProcessBuilder.start(ProcessBuilder.java:1029)
05-07 23:13:28.243 25379 25379 W System.err: 	... 9 more

'''
