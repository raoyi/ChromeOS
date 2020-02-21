# 常用命令相关

1. `crossystem` 查看host版本（或者在开机叹号位置按 `Tab` 键2次）

2. `ectool version` 查看ec版本

3. 查看硬件信息：
```
cat /proc/cpuinfo	# cpu信息
cat /proc/meminfo	# 内存信息
lsblk	# 硬盘（EMMC/SSD）信息
```

4. `cat /etc/lsb-release` 查看系统版本

5. OOB锁电池U盘就是factory image

6. 测试程序按装：机器安装test image，从ChromeOS-factory-版本号-平台号.zip包中得到 `toolkit/install_factory_toolkit.run` 文件，运行

7. 安装有工厂测试程序的机器，把 `/usr/local/factory/enabled` 文件删除（或改名）就可以进入终端用户界面

8. `ctrl+alt+?` 调出快捷键列表

9. test image在BIOS、EC、firmware版本匹配的前提下，normal mode可以进VT2，此时set GBB `0x0` 为normal mode，`0x39` dev mode

10. `ctrl+鼠标左键` 循环播放视频，操作鼠标键盘自动退出循环播放

11. 查看VPD信息
```
vpd -i RO_VPD -l
vpd -i RW_VPD -l
```

12. 保存VPD信息成bin文件
```
flashrom -p host -r -i RO_VPD:/usr/local/vpd-ro.bin
flashrom -p host -r -i RW_VPD:/usr/local/vpd-rw.bin
```

13. 刷BIOS / EC
```
flashrom -p host -w <bios文件>
flashrom -p ec -w <ec文件>
```

14. 从bin文件中restore VPD信息
```
flashrom -p host -w -i RO_VPD:/usr/local/vpd-ro.bin --fast-verify
flashrom -p host -w -i RW_VPD:/usr/local/vpd-rw.bin --fast-verify
```

15. build packages的命令
```
(inside)
./build_packages --board=${BOARD} --accept_licenses="Google-TOS" --autosetgov
```

16. 改CBI
```
ectool cbi set 2 1 1 0  (改成SKU1)
# 操作前确保EC写保护状态为disabled
```

17. power load test的命令（要连servo board）
```
(outside)
cd <chromoiumos-dir>
cros_sdk --no-ns-pid
```
```
(inside)
test_that <DUT IP> power_LoadTest
```
```
(DUT)
cd /usr/local/autotest/
bin/autotest tests/power_LoadTest/control
```

18. MobLab测试时U盘创建ext4分区别加label的方法

> 先决条件：

- 确保U盘要是未分区状态，建议在Windows下用diskpart clean

- 可以用MobLab的VT2（username: `moblab`），也可以用Ubuntu操作

> 命令步骤：
```
sudo mkfs.ext4 <device_path>
sudo e2label <device_path> MOBLAB-STORAGE
```

> 提示：完成后可在ChromeOS或Ubuntu中查看label变化

19. 开发环境文件结构

- <chromiumos-dir>/src/platform/ 下的文件源于 `https://chromium.googlesource.com/chromiumos/platform/`
  
