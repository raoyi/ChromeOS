#!/bin/bash

# Author: RaoYi
# Email: hi@raoyi.net
# USED FOR BATTERY CAPACITY LOGGING.
# Usage:
# run this file in VT#.

stwarn=0
warn=0

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

start_time=`date +%s`
start_cap=`cat /sys/class/power_supply/BAT0/capacity`
LOG_FILE=/usr/local/caplog.`date +%y%m%d%H%M%S`

echo
echo -e "\033[32m battery capacity logging... \033[m"
echo

function log(){
  echo "capacity: $start_cap -> `cat /sys/class/power_supply/BAT0/capacity` - $(date +"%Y-%m-%d %H:%M:%S") - spended: $[ (`date +%s` - $start_time) / 60 ] minutes - $(state)" >> ${LOG_FILE}
}

trap 'onCtrlC' INT
function onCtrlC(){
  log
  echo "Ctrl+C" >> ${LOG_FILE}
  exit 0
}

while true
do
  log
  if [ $(state) == AC -a $warn == 0 ]
    then
    echo -e "\033[31m Power supply switched to AC at $(date +"%Y-%m-%d %H:%M:%S") \033[m"
    warn=1
  fi
  sleep 60
done

