# JDB++

As I was not happy with the current debuggers available for APKs I 
tried writing my own. For the final outcome watch: https://asciinema.org/a/328262

It allows single stepping through smali code including watching and modifing locals.

It is based on two steps first it annotates the APK with extra debug
information and later debugs the annotated APK.
Of course if there are anti tamper checks those will trigger.

It starts the application on the emulator/device and connects to it using jdb.
Basically the debugger is a wrapper around jdb using extra debug information.

## Usage

It should be fairly easy to use, using the following steps:

```
pip install -r requirements.txt

# decompile using apktool
apktool d target.apk

# create annotated smali files
python prepare_app.py -f target

# recompile apk
apktool b target

# sign and install
testsign target/dist/target.apk
adb install target/dist/target.apk

# and start the debuggin
python jdb++.py -n com.example.target -a MainActivity
```

The apktool and install steps can be included into the prepare step, 
this is a future todo. 

If you want your apk to stop on the main entry point you have to set
a breakpoint in the `.jdbrc` file in your home directory.

```
stop in com.example.target.MainActivity.onCreate(android.os.Bundle)
```

After the debugger will stop on this breakpoint and you are free to debug
and investigate annotated locals.

## Commands

| Command       | Description   | Note   |
| ------------- |---------------| -------| 
| n, so, next   | single step over | |
| si, stepi     | single step into | |
| su, step up   | step until return| |
| c, cont, continue | continue execution | does not return without tracing |
| locals, l     | show locals/registers | | 
| interactive   | get jdb interavtive mode | | 
| bps, breakpoints | list breakpoints | | 
| bp, b | set breakpoint | bp 200 -> set bp on line 200 of current file |
| trace | start method tracing | | 
| untrace | stop method tracing | single steps also deactivate tracing |

All commands which are not handled are directly forwarded to jdb.

## TODOs
There are so many todos I dont know where to start, be aware it is
in a very beta state.

* add logic for adding Breakpoints automatically
* keep locals in order
* ...

## Questions
Dont hesitate to ask, leave a comment or a pull request

