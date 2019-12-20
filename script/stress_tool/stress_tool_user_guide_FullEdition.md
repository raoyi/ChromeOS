**基础说明：**

1. S3循环可以用suspend_stress_test –c 1000命令来执行，而无需使用本工具。具体为：断开网络，ctrl+alt+T打开cros界面，敲shell进入shell，敲sudo su获得权限，再敲stop shill&& suspend_stress_test –c 1000（stop shill是为了避免shill影响到S3循环以免意外中止。
2. 测试工具文件夹stress tool下包含cold_boot.conf、cold_boot.sh、stress_auto.sh三个文件，测试时执行stress_auto.sh即可，具体见下面步骤说明。
3. 工具文件夹名是Stress tool或者Stresstool或者tool for stress或者其它任何名字都没关系，只要里面有上述三个文件，并且敲命令的时候注意保持一致就行了。
4. 执行这一测试前要先把测试工具文件夹stress tool从U盘拷贝到笔记本本身的emmc（或者磁盘）上。
5. 拷贝测试工具文件夹stress tool不能在一般消费者界面下进行，而要在VT2界面下用Linux命令来执行。所以拷贝前先用mount命令把U盘挂载到虚拟的media路径下，具体见下面步骤说明。
6. Media位于根目录下，是一个用于挂载移动设备比如U盘的目录（文件夹），在没有挂载移动设备前，media目录下没有内容，只有archive和removable两个空文件夹。用cd(这里要空一格，所有cd命令都是如此)/media命令可以进入该目录（文件夹），再用ls命令查看目录内容，即可看到上述内容。
7. 当移动设备如U盘挂载到media路径（即目录）下之后，media目录（文件夹的内容就变成了U盘的内容，此时用cd(空一格)/media命令可以进入该目录，再用ls命令查看目录内容，会发现里面就是U盘上的文件。
8. 此时把测试工具文件夹stress tool从media文件夹下面拷贝到笔记本上面的/home/chronos目录（文件夹）下面。（第一个/是表示根目录）

**好了，具体步骤如下：**

1. 插上U盘，进入VT2界面
2. mount /dev/sdX1 /media（这是完整命令，比如mount /dev/sda1 /media）

（x=sd后面跟的字母，n=sdx后面跟的数字，如sda1，sda4,sdb1，多按几次TAB键查看x与n）

具体动作是，先敲命令: mount(空格)/dev/sd然后按tab键查看x与n，确认之后继续敲把命令补全

3. cd(空格)/media

（此时可以用ls命令查看一下media的内容是否就是U盘的内容，熟练之后就不用了）

4. cp -R stress\(空格)tool/ /home/chronos/

或者

cp -R stresstool/ /home/chronos/ 

（如前所述，stress工具文件夹名是Stress tool或者Stresstool或者tool for stress或者其它任何名字都没关系，敲命令的时候注意保持一致就行了）

5. cd /home/chronos/stress tool（或者stresstool,总之这个命令的目的是转到shell文件所在目录，以便执行下一步的运行shell脚本命令）
6. sh stress_auto.sh  （sh命令就是执行shell脚本，如本例中的stress_auto.sh脚本文件）
7. 选1 remove SSD verification
8. 自动重启后先登录账户,再进VT2, sh /home/chronos/stress/stress_auto.sh(敲命令时输完前两个字母后就可以按tab键自动补全，这样省事一点）。根据需要选2 run S3 test或3 run coldboot test, （如一开始所说，S3可以用suspend_stress_test –c 1000命令来做，更简单）
9. 输入次数
10. 查看log： cd /usr/local
11. cat cold_boot.log

