#!/bin/bash

# Author: RaoYi
# Email: hi@raoyi.net
# USED FOR AUTO STRESS TEST MAIN.
# Usage:
# Please refer to the manual.

clear
echo
echo
cat << EOF
*****pelase enter your choise:(1-4)*****
echo
1.Remove SSD verification
2.Run S3 test
3.Run ColdBoot test
4.Run both S3 & ColdBoot test
5.Exit
EOF
echo
read -p "Now select the top option to:" input
s3_cycle=0
cb_cycle=0

case $input in
  1) 
    echo #####Disable ssd root verification#####
    cd /usr/share/vboot/bin/
    sh make_dev_ssd.sh --force --remove_rootfs_verification 
    reboot ;;
  2)
    read -p "Please Enter S3 Cycle:" s3_cycle
    ;;
  3)
    read -p "Please Enter ColdBoot Cycle:" cb_cycle
    ;;
  4)
    read -p "Please Enter S3 Cycle:" s3_cycle
    read -p "Please Enter ColdBoot Cycle:" cb_cycle
    ;;
  *)
    exit ;;
esac

if [ $s3_cycle != 0 ]
  then
    if [ -e "/usr/local/s3.log" ] 
      then 
        rm "/usr/local/s3.log"
    fi
    suspend_stress_test -c $s3_cycle >> /usr/local/s3.log
fi

if [ $cb_cycle != 0 ]
  then
    if [ -e "/usr/local/cold_boot.log" ] 
      then 
        rm "/usr/local/cold_boot.log"
    fi
    if [ -e "/usr/local/cold_boot.sh" ] 
      then 
        rm "/usr/local/cold_boot.sh"
    fi
    if [ -e "/etc/init/cold_boot.conf" ] 
      then 
        rm "/etc/init/cold_boot.conf"
    fi
    cur_dir=`pwd`
    cd $cur_dir
    sudo cp cold_boot.conf /etc/init/
    sudo cp cold_boot.sh /usr/local/
    chmod +x /usr/local/cold_boot.sh
    sh /usr/local/cold_boot.sh -c $cb_cycle
fi

