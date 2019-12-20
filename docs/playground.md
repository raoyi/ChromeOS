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