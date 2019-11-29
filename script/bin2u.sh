#!/bin/bash

# Author: RaoYi
# Email: hi@raoyi.net
# USED FOR CREATE CHROMEOS-INSTALL U-DISK IN LINUX.
# Usage:
# run script in Linux Terminal,
# type the binary file path as the first parameter.

echo "please choose u-disk volume..."
var=$(ls /dev/sd[a-p])
OLD_IFS="$IFS"
IFS=" "
var=($var)
IFS="$OLD_IFS"
for s in ${var[a]}
do
    num=${s#*sd}
    echo $num": "$s
done
read num

pv -preb $1 | sudo dd of=/dev/sd$num bs=8M iflag=fullblock oflag=dsync
sync
sync
echo "finished..."
