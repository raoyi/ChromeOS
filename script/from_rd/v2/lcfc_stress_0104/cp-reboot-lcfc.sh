#!/bin/sh
cp warm-boot-lcfc.conf /etc/init

#count - lcfc
touch /usr/local/lcfc_stress_0104/wb_count
echo 0 > /usr/local/lcfc_stress_0104/wb_count

#rm -rf /var/log
echo > /var/log/messages

sync
reboot
