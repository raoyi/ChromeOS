#!/bin/bash

# Author: RaoYi
# Email: hi@raoyi.net
# USED FOR AUTO LOOP CHROMEOS-INSTALL TEST.
# Usage:
# put this file into test-image u-disk(such as /usr/local/),
# boot from u-disk and run this file in VT2.

LOG_FILE="/usr/local/osinstall.log"

trap 'onCtrlC' INT
function onCtrlC () {
  echo -e '\nyou can umount u-disk now...'
  exit 0
}

read -p "Now input the install times:" ins_times

for i in `seq 1 $ins_times`
  do
  echo "[`date`] install $i times start" >> ${LOG_FILE};
  chromeos-install --yes
  echo "[`date`] install $i times end" >> ${LOG_FILE};
  wait_sec=30
  echo "you can press ctrl+C to stop in ${wait_sec} seconds."
  tput sc
  while [ $wait_sec -gt 0 ]
    do
    echo -n $wait_sec
    sleep 1
    let "wait_sec--"
    tput rc
    tput ed
    done
done
