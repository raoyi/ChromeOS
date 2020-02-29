---
layout: post
title:  Linux 系统中 /etc/passwd 和 /etc/shadow文件详解
date:   2019-11-14
tags:   Linux
permalink: /post/linux-passwd-shadow
---

Linux系统中，所有用户（包括系统管理员）的账号和密码都可以在/etc/passwd和/etc/shadow这两个文件中找到，用户和密码就放在文件中。

/etc/passwd文件中的每个用户都有一个对应的记录行，记录着这个用户的一下基本属性。/etc/passwd只有系统管理员才可以修改的，该文件对所有用户可读。而/etc/shadow文件正如他的名字一样，他是passwd文件的一个影子，/etc/shadow文件中的记录行与/etc/passwd中的一一对应，它由pwconv命令根据/etc/passwd中的数据自动产生。但是/etc/shadow其他用户看不了，/etc/shadow文件只有系统管理员才能够进行修改和查看。

```
raoyi@Linux:~$ ls -al /etc/passwd /etc/shadow
-rw-r--r-- 1 root root  2469 5月  17 07:12 /etc/passwd
-rw-r----- 1 root shadow 1303 5月  17 07:12 /etc/shadow
```

上面分别列出了passwd和shadow文件的访问权限信息，其中passwd保存的是账号，shadow保存的是账号的密码等信息，下面就具体看看这两个文件的内容：

## /etc/passwd文件介绍

首先，我们通过命令vim /etc/passwd进行查看/etc/passwd文件内容：

```
raoyi@Linux:~$ vim /etc/passwd

root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
sys:x:3:3:sys:/dev:/usr/sbin/nologin
sync:x:4:65534:sync:/bin:/bin/sync
games:x:5:60:games:/usr/games:/usr/sbin/nologin
man:x:6:12:man:/var/cache/man:/usr/sbin/nologin
lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin
mail:x:8:8:mail:/var/mail:/usr/sbin/nologin
news:x:9:9:news:/var/spool/news:/usr/sbin/nologin
uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin
......
```

从文件中我们可以看到，/etc/passwd中一行记录对应着一个用户，每行记录又被冒号(:)分隔为7个字段，其格式和具体含义如下：

第一列为账户名称

第二列为密码占位符（x表示该账户需要密码才能登录，为空时，账户无须密码即可登录）

第三列为账户UID

第四列为GID

第五列为账户附加基本信息，一般存储账户名全称，联系方式等信息

第六列为账户家目录位置

第七列为账户登录Shell，/bin/bash为可登录系统Shell，/sbin/nologin表示账户无法登录系统。

## /etc/shadow文件介绍

/etc/shadow文件格式与/etc/passwd文件格式类似，同样由若干个字段组成，字段之间用“:”隔开。

通过命令行输入sudo vim /etc/shadow进行文件内容查看：

```
raoyi@Linux:~$ sudo vim /etc/shadow

root:!:18004:0:99999:7:::
daemon:*:17937:0:99999:7:::
bin:*:17937:0:99999:7:::
sys:*:17937:0:99999:7:::
sync:*:17937:0:99999:7:::
games:*:17937:0:99999:7:::
man:*:17937:0:99999:7:::
lp:*:17937:0:99999:7:::
mail:*:17937:0:99999:7:::
news:*:17937:0:99999:7:::
uucp:*:17937:0:99999:7:::
proxy:*:17937:0:99999:7:::
www-data:*:17937:0:99999:7:::
backup:*:17937:0:99999:7:::
list:*:17937:0:99999:7:::
irc:*:17937:0:99999:7:::
```

文件以冒号为分隔符

**说明：**

第一列为账户名称

第二列为密码（账户未设置密码时为!!，设置密码后加密显示）

第三列为上次修改密码的时间距离1970年01月01日多少天

第四列为密码最短有效天数，0表示无限制

第五列为密码最长有效天数（默认位99999天，可以理解为永不过期）

第六列为密码过期后的宽限天数（密码过期后，预留几天给账号修改密码，此时已无法使用旧密码登录）

第八列为账户失效日期（从1970年01月01日起多少天后账户失效）

第九列暂时保留未使用。

