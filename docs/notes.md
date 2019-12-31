# 常用命令相关
1. crossystem 查看host版本（或者在开机叹号位置按 `Tab` 键2次）
2. ectool version 查看ec版本
3. 查看硬件信息：
```
cat /proc/cpuinfo	# cpu信息
cat /proc/meminfo	# 内存信息
lsblk	# 硬盘（EMMC/SSD）信息
```
4. cat /etc/lsb-release 查看系统版本
5. OOB锁电池U盘就是factory image
6. 测试程序按装：机器安装test image，从ChromeOS-factory-版本号-平台号.zip包中得到toolkit/install_factory_toolkit.run文件，运行
7. 安装有工厂测试程序的机器，把/usr/local/factory/enabled文件删除（或改名）就可以进入终端用户界面
8. ctrl+alt+? 调出快捷键列表
9. test image在BIOS、EC、firmware版本匹配的前提下，normal mode可以进VT2，此时set GBB 0x0为normal mode，0x39为开发模式
10. ctrl+鼠标左键 循环播放视频，操作鼠标键盘自动退出循环播放
11. 查看VPD信息
```
vpd -i RO_VPD -l
vpd -i RW_VPD -l
```
12. 保存VPD信息成bin文件
```
flashrom -p host -r -i RO_VPD:/tmp/vpd-ro.bin
flashrom -p host -r -i RW_VPD:/tmp/vpd-rw.bin
```
14. 刷BIOS / EC
```
flashrom -p host -w <bios文件>
flashrom -p ec -w <ec文件>
```
13. 从bin文件中restore VPD信息
```
flashrom -p host -w -i RO_VPD:/tmp/vpd-ro.bin --fast-verify
flashrom -p host -w -i RW_VPD:/tmp/vpd-rw.bin --fast-verify
```
14. build packages的命令
```
(inside)
./build_packages --board=${BOARD} --accept_licenses="Google-TOS" --autosetgov
```
15. 改CBI
```
ectool cbi set 2 1 1 0  (改成SKU1)
```
