#!/bin/sh
cp power-s5-lcfc.conf /etc/init

#count - lcfc
touch /usr/local/lcfc_stress_0104/cb_count
echo 0 > /usr/local/lcfc_stress_0104/cb_count

#rm -rf /var/log
echo > /var/log/messages

sync
reboot
