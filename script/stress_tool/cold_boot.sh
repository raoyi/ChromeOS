#!/bin/bash

# Author: RaoYi
# Email: hi@raoyi.net
# USED FOR AUTO STRESS COLD_BOOT TEST.
# Usage:
# Please refer to the manual.

. /usr/share/misc/shflags

DEFINE_integer count 50 "The number of iterations" c
DEFINE_integer waiting_reboot 20 "The number of seconds to wait for reboot" w

# Minimum interval seconds from current time to previous reboot.
MINIMUM_INTERVAL=$((2 * 60))

LOG_FILE="/usr/local/cold_boot.log"
FLAG_FILE="/usr/local/cold_boot_flag"

# Check auto run flag when reboot in test process.
if [ "conf" = "$1" ]; then
    if [ ! -f "$FLAG_FILE" ]; then
        exit 0
    fi
fi

FLAGS "$@" || exit 1

# Check whether the previous reboot has successfully completed.
# The time intervals between current and previous shut down not exceeding
# the number of seconds to wait for reboot plus minimum interval seconds.
cur_count=0
previous_time=0
current_time=$(date +%s)
if [ -f "$FLAG_FILE" ]; then
  eval $(awk -F ":" '{print "cur_count="$1" FLAGS_count="$2" FLAGS_waiting_reboot="$3" previous_time="$4""}' ${FLAG_FILE})
  intervals=`expr ${current_time} - ${previous_time} - ${FLAGS_waiting_reboot}`

  if [ ${intervals} -gt ${MINIMUM_INTERVAL} ]; then
    echo "Current time is:" >> ${LOG_FILE}
    date >> ${LOG_FILE}
    echo "[Fail] Too long reboot intervals." | tee -a ${LOG_FILE}
    rm -rf ${FLAG_FILE}
    exit 1
  elif [ ${cur_count} -eq ${FLAGS_count} ]; then
    printf "Reboot test was successful!\n" | tee -a ${LOG_FILE}
    rm -rf ${FLAG_FILE}
    exit 0
  fi
elif [ ${cur_count} -eq 0 ]; then
  echo "Reboot test begins." | tee -a ${LOG_FILE}
fi

cur_count=`expr $cur_count + 1`
printf "Reboot %d of ${FLAGS_count}: " ${cur_count} | tee -a ${LOG_FILE}
date >> ${LOG_FILE}
printf "sleep for %d seconds...\n" ${FLAGS_waiting_reboot}

printf "%d:%d:%d:" ${cur_count} ${FLAGS_count} ${FLAGS_waiting_reboot}> ${FLAG_FILE}
echo ${current_time} >> ${FLAG_FILE}

sleep ${FLAGS_waiting_reboot}

ectool reboot_ec cold at-shutdown
sudo shutdown -h now
