#!/bin/sh
stop warm-boot-lcfc 				
rm /etc/init/warm-boot-lcfc.conf 
cat -n /var/log/reboot.log
wc -l /var/log/reboot.log > tmp.txt
cut -d '/' -f 1 tmp.txt >tmp1.txt           

var="$(cat tmp1.txt)"                  

echo "reboot count:"
echo $((var/2))

rm tmp.txt
rm tmp1.txt






 

