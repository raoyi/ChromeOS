#!/bin/sh
stop power-s5-lcfc
rm /etc/init/power-s5-lcfc.conf
cat -n /var/log/power_on_off.log
wc -l /var/log/power_on_off.log > tmp.txt

cut -d '/' -f 1 tmp.txt >tmp1.txt           

var="$(cat tmp1.txt)"                  

echo "S5 count:"
echo $((var/2))

rm tmp.txt
rm tmp1.txt





