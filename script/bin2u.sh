#!/bin/bash

# Author: RaoYi
# Email: hi@raoyi.net
# USED FOR CREATE CHROMEOS-INSTALL U-DISK IN LINUX.
# Usage:
# run script in Linux terminal,
# use the binary file path as the first parameter.

echo "Please choose correct u-disk volume..."
var=$(ls /dev/sd[a-h])
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
echo "finished..."
