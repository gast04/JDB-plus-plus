import os, sys, argparse

debugfiles_folder = "DebugFiles"

def parseCmdArguments() -> str:
  parser = argparse.ArgumentParser(description='Anotate APK and prepare for jdb++')
  parser.add_argument('-f', "--folder", type=str, metavar="", dest='apk_path', default=None,
                      help='relativ path to smali directories, unpacked by apktool')

  args = parser.parse_args()
  if args.apk_path == None:
    parser.print_help()
    sys.exit(0)
  
  return args.apk_path


def checkFolderStructure(folderpath: str):

  parent, child = os.path.split(folderpath)

  if not os.path.exists(parent):
    # create parent first
    checkFolderStructure(parent)

  os.mkdir(folderpath)


def createStoreFolder(folderpath: str):

  # remove trailing slash
  if folderpath[-1] == "/":
    folderpath = folderpath[:-1]

  if not os.path.exists(folderpath):
    checkFolderStructure(folderpath)
