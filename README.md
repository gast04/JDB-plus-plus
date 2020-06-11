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
| ag, agdb, attach gdb | attach gdb(server) | |
| native bp [la], nbp [la] | get native breakpoints | [la] defines load address of library |


All commands which are not handled are directly forwarded to jdb.

## Native Support
Only tested on `arm64-v8a` it pushes gdbserver to `/data/local/tmp` directory
and attaches to the process (APK). It opens a new terminal (xfce4-terminal) and
connects to it. It runs a series of gdb commands to avoid loading information 
of all shared libraries, because this simply takes ages. It only loads custom
libraries and no system libs, this minimizes the startup overhead. Breakpoints
on functions have to be set, this can be done by parsing the load address 
(`info shared` command) to the `nbp` command od jdb++. This will return all function 
addresses which start with `Java_`, this is done by invoking `radare2` so it migth
take a while.


## TODOs
There are so many todos I dont know where to start, be aware it is
in a very beta state.

* add logic for adding Breakpoints automatically
* keep locals in order
* ...

## Latest Updates
* (11.6.2020)
  1. command line flag for rooted devices
  2. minor bug fixes
  3. **native debugging support** using prebuilt gdbserver and gdb from the
    android ndk, paths have to be set in `definitions.py` file. The peda-arm 
    file is from [alset0326](https://github.com/alset0326/peda-arm).
    This appraoch works quite nice, and is less heavy than attaching IDA's 
    android server.   
    It also loads only custom libraries, no system libraries, this makes
    the whole startup really fast (seconds!).

## Questions
Dont hesitate to ask, leave a comment or a pull request
