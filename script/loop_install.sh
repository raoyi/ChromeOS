#!/bin/sh

# Author: RaoYi
# Email: hi@raoyi.net
# USED FOR AUTO LOOP CHROMEOS-INSTALL TEST.
# Usage:
# put this file into test-image u-disk(such as /usr/local/),
# boot from u-disk and run this file in VT2.

LOG_FILE="/usr/local/osinstall.log"

read -p "Now input the install times:" ins_times

for i in `seq 1 $ins_times`
do
echo "[`date`] install $i times start" >> ${LOG_FILE};
chromeos-install --yes
echo "[`date`] install $i times end" >> ${LOG_FILE};
echo "you can press ctrl+C to stop, and umount usb disk in 1 mins."
sleep 1m
clear
sleep 10s
done
