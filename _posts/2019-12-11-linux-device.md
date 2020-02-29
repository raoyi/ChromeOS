---
layout: post
title:  设备在Linux内的文件名
date:   2019-12-11
tags:   Linux
permalink: /post/linux-device
---

|设备|设备在Linux内的文件名|
|----|-------------------|
|IDE硬盘|/dev/hd[a-d]|
|SCSI/SATA/USB硬盘/U盘|/dev/sd[a-p]|
|VirtI/O界面|/dev/vd[a-p] 用于虚拟机内|
|软驱|/dev/fd[0-7]|
|打印机|25针：/dev/lp[0-2]<br>USB：/dev/usb/lp[0-15]|
|鼠标|USB：/dev/usb/mouse[0-15]<br>PS2：/dev/psaux<br>当前鼠标：/dev/mouse|
|CD/DVD ROM|通用：/dev/scd[0-1]<br>通用：/dev/sr[0-1] CentOS较常见<br>当前CDROM：/dev/cdrom|
|磁带机|IDE：/dev/ht0<br>SATA/SCSI：/dev/st0<br>当前：/dev/tape|

