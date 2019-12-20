#!/bin/bash

# Author: RaoYi
# Email: hi@raoyi.net
# USED FOR BATTERY CAPACITY LOGGING.
# Usage:
# run this file in VT#.

# start power state warn flag
stwarn=0
# in flow AC warn flag
warn=0
# write log line flag
logline=0
# pre-cap for check log
precap=101

function state(){
  power_supply_info | grep "online" | grep -q "yes"
  if [ $? == 0 ]
  then
  echo "AC"
  else
  echo "DC"
  fi
}

while [ $(state) == "AC" ]
do
  if [ $stwarn == 0 ]
    then
    echo
    echo -e "\033[31m Please plug out AC to start logging capacity... \033[m"
    stwarn=1
  fi
  sleep 5
done

# log start time - sec
start_time=`date +%s`
# cap at log start
start_cap=`cat /sys/class/power_supply/BAT0/capacity`
# log path
LOG_FILE=/usr/local/caplog.`date +%y%m%d%H%M%S`

echo
echo -e "\033[32m battery capacity logging... \033[m"
echo

#logging function
function log(){
  if [ $cap == $precap ];then
    if [ $logline == 0 -o $logline == 1 ];then
      echo "capacity: $start_cap -> $cap - $(date +"%Y-%m-%d %H:%M:%S") - spended: $[ (`date +%s` - $start_time) / 60 ] minutes - $(state)" >> ${LOG_FILE}
      let "logline++"

    elif [ $logline == 2 ];then
      sed -n '$p' ${LOG_FILE} | grep $(state)
      if [ $? == 0 ];then
        sed -i '$d' ${LOG_FILE}
      fi
      echo "capacity: $start_cap -> $cap - $(date +"%Y-%m-%d %H:%M:%S") - spended: $[ (`date +%s` - $start_time) / 60 ] minutes - $(state)" >> ${LOG_FILE}
    fi
  elif [ $cap != $precap ];then
    echo "capacity: $start_cap -> $cap - $(date +"%Y-%m-%d %H:%M:%S") - spended: $[ (`date +%s` - $start_time) / 60 ] minutes - $(state)" >> ${LOG_FILE}
    precap=$cap
    logline=0
  fi
}

# Ctrl+C function
trap 'onCtrlC' INT
function onCtrlC(){
  echo "capacity: $start_cap -> `cat /sys/class/power_supply/BAT0/capacity` - $(date +"%Y-%m-%d %H:%M:%S") - spended: $[ (`date +%s` - $start_time) / 60 ] minutes - $(state)" >> ${LOG_FILE}
  echo "Ctrl+C" >> ${LOG_FILE}
  exit 0
}

# logging loop
while true
do
  cap=`cat /sys/class/power_supply/BAT0/capacity`
  log
  if [ $(state) == AC -a $warn == 0 ]
    then
    echo -e "\033[31m Power supply switched to AC at $(date +"%Y-%m-%d %H:%M:%S") \033[m"
    warn=1
  fi
  sleep 30
done

