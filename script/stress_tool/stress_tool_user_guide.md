# stress tool user guide

1. mount /dev/sdX1 /media

2. cp -R /media/stress_tool /usr/local/

3. cd /usr/local/stress_tool 

4. umount /media(这一步就是为了拔U盘以便插到下一台机器拷贝文件，如果你只测一台，测完了再拔也行）

5. sh stress_auto.sh

选第一项 `remove SSD verification`,自动重启后先登录账户,再进VT2

6. sh /usr/local/stress_tool/stress_auto.sh(敲命令时输完前两个字母后就可以按tab键自动补全，这样省事一点）

7. 选择第三项 `run coldboot test`

8. 选择次数，如1000
