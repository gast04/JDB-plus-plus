
echo "Debugging $1...\n"

# stop and clear before run
echo -n "Killing: "
adb shell pm clear $1
#adb shell am force-stop $1

# start application
adb shell am start -D -n $1/.$2
sleep 2 # sleep to be save

PID=$(adb shell ps | grep -i $1 | sed -r "s/[\ ]+/\ /g" | cut -d " " -f 2)
adb forward tcp:33333 jdwp:$PID
jdb -connect com.sun.jdi.SocketAttach:hostname=localhost,port=33333

