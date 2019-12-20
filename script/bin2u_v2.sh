#!/bin/bash

# Author: RaoYi
# Email: hi@raoyi.net
# USED FOR CREATE CHROMEOS-INSTALL U-DISK IN LINUX.
# Usage:
# run script in Linux terminal,
# use the binary file path as the first parameter.

# get bin file path
if [ ! -n "$1" ]
  then
  read -p "Please input the binary file path: " bin_path
else
  bin_path=$1
fi

# get u-disk volume
var=$(ls /dev/sd[a-h])
OLD_IFS="$IFS"
IFS=" "
var=($var)
IFS="$OLD_IFS"
vol_int=0
for s in ${var[a]}
do
  num=${s#*sd}
  echo $num": "$s
  let "vol_int++"
done

if [ $vol_int == 1 ]
then
  num=$num
else
  read -p "Please choose correct u-disk volume: " num
fi

# check and install pv
dpkg -V pv
if [ $? != 0 ]
  then
    sudo apt install -y pv
    if [ $? != 0 ]
      then
        echo -e "\n\033[31mInstall pv fail! press Ctrl+C and check network connection.\n\nOr wait 5 seconds to start without progress bar...\033[m"
      wait_sec=5
      tput sc
      while [ $wait_sec -gt 0 ]
        do
        echo -n $wait_sec
        sleep 1
        let "wait_sec--"
        tput rc
        tput ed
        done
      status=1
    fi
fi

# do
if [ $status == 1 ]
  then
    sudo dd if=$bin_path of=/dev/sd$num bs=8M iflag=fullblock oflag=dsync
  else
    pv -preb $bin_path | sudo dd of=/dev/sd$num bs=8M iflag=fullblock oflag=dsync
fi

sync
echo -e "\033[32mFinished! You can unplug u-disk now...\033[m"
