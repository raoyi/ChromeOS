# 开发环境搭建笔记

## 系统要求：

- Ubuntu Linux (version 18.04 - Bionic Beaver)
- 64bit

**命令标识：**
```
(outside)	on your build computer, outside the chroot
(inside)	inside the chroot on your build computer
(device)	your Chromium OS computer
```
### step1. 安装git和curl
```
(outside)
sudo apt-get install git-core gitk git-gui curl lvm2 thin-provisioning-tools \
     python-pkg-resources python-virtualenv python-oauth2client xz-utils
```
### step2. 安装depot_tools

clone depot_tools
```
(outside)
git clone https://chromium.googlesource.com/chromium/tools/depot_tools.git
```
运行命令（假设depot_tools被clone到/path/to/depot_tools路径）
```
(outside)
export PATH=$PATH:/path/to/depot_tools
```
并把以上命令添加到 `~/.bashrc` 文件末尾

### step3. Making sudo a little more permissive ~~（存疑）~~

~~复制以下命令并运行~~
```
(outside)
cd /tmp
cat > ./sudo_editor <<EOF
#!/bin/sh
echo Defaults \!tty_tickets > \$1          # Entering your password in one shell affects all shells
echo Defaults timestamp_timeout=180 >> \$1 # Time between re-requesting your password, in minutes
EOF
chmod +x ./sudo_editor
sudo EDITOR=./sudo_editor visudo -f /etc/sudoers.d/relax_requirements
```
**这一步按照官网文档执行似乎有问题，做如下修改验证：（验证PASS）**
```
sudo cat /etc/sudoers    #可以看到sudoers文件内容（必须sudo）
```
打开sudoers文件准备修改：
```
sudo visudo
```
加上两行：
```
Defaults !tty_tickets    #空白字符为Tab
Defaults timestamp_timeout=180     #空白字符为Tab
```
屏幕下方提示的符号^为Ctrl

修改完成后保存，随后重启

### step4. Git配置
```
(outside)
git config --global user.email "you@example.com"
git config --global user.name "Your Name"
```

### step5. 再次确认系统位元（非必要）
```
(outside)
uname -m
```
显示结果：x86_64

### step6. 设置默认权限
```
(outside)
umask 022
```

### step7. 确认默认权限（非必要）
```
(outside)
touch ~/foo
ls -la ~/foo
-rw-r--r-- 1 user group 0 2012-08-30 23:09 /home/user/foo
```

### step8. 获取源码
```
(outside)
mkdir -p ${HOME}/chromiumos
cd ${HOME}/chromiumos
repo init -u https://chromium.googlesource.com/chromiumos/manifest.git --repo-url https://chromium.googlesource.com/external/repo.git
repo sync -j4
```

### step9. END
```
(outside)
cros_sdk
```

