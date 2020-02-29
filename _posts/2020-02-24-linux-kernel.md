---
layout: post
title:  深入理解Linux内核（第三版）笔记
date:   2020-02-24
tags:   Linux
permalink: /post/linux-kernel
---

* 目录
{:toc}

# 第一章 绪论

发行版中Linux源代码位置：`/usr/src/linux`

**地址空间：**允许进程引用的内存地址集合

几个进程能并发地执行同一程序，而同一个进程能顺序地执行几个程序

（`内核态(Kernel Mode)` / `用户态(User Mode)`）能否直接访问内核数据结构或内核的程序

微内核(Micro Kernel) / 宏内核(Monolithic Kernel) / 混合内核(Hybrid Kernel)

## 硬链接：（即链接）

```
ln P1 P2
```

为由路径P1标识的文件创建一个路径名为P2的硬链接

*硬链接的限制：*
- 不允许用户给目录创建硬链接
- 只有在同一文件系统中的文件之间才能创建链接

## 软链接：（即符号链接）

```
ln -s P1 P2
```

创建一个路径名为P2的软链接，P2指向路径P1

## 文件类型：
- 普通文件（regular file）
- 目录
- 符号链接（软链接）
- 面向块的设备文件（block-oriented device file）
- 面向字符的设备文件（character-oriented device file）
- 管道（pipe）和命名管道（named pipe）(也叫FIFO)
- 套接字（socket）

## 文件潜在用户类型：
- file owner
- 同组用户，不包含owner
- 其他

**访问权限：**`rwx`

**附加标记：**
- `suid`(Set User ID):如果设置了可执行文件的suid的标志位，进程就获得了该文件拥有者的UID
- `sgid`(Set Group ID):如果设置了可执行文件的sgid的标志位，进程就获得了该文件用户组的UID
- `sticky`(已过时):

## 文件操作的系统调用

*进程只能访问打开的文件*

### 打开文件：

```
fd=open(path, flag, mode)
```

- `path`:文件路径
- `flag`:r, w, rw, a
- `mode`:指定新建文件的访问权限

### 访问打开的文件：

顺序访问 / 随机访问

`设备文件` 和 `命名管道文件` 通常只能顺序访问

```
newoffset=lseek(fd, offset, whence)
```

- `fd`:文件描述符
- `offset`:有符合整数，用来计算文件指针的新位置
- `whence`:指定指针位置的计算方式，指针偏移量

```
nread=read(fd, buf, count)
```

- `fd`:打开文件的文件描述符
- `buf`:指定在进程地址空间中缓冲区的地址，所读的数据就放在这个缓冲区
- `count`:所读的字节数

### 关闭文件

```
res=close(fd)	#释放与文件描述符fd相对应的打开文件对象
```

### 更名及删除文件

```
res=rename(oldpath, newpath)	#改变了文件链接的名字
```

```
res=unlink(pathname)	#减少了文件链接数，删除了相应的目录项。当链接数为0时，文件才被真正删除
```

重命名或删除文件时无需打开文件，只是对一个或多个目录的内容起作用

## 进程/内核模式

内核是进程的管理者

内核线程（kernel thread）是特权进程，特点：
- 以内核态运行在内核地址空间
- 不与用户直接交互，不需要终端设备
- 在系统启动时创建，一直活跃直至系统关闭

激活内核例程的几种方式：
1. 进程调用系统调用
2. 正在执行进程的CPU发出一个异常信号，内核代表产生异常的进程处理异常
3. 外围设备向CPU发出一个中断信号以通知一个事件的发生。中断在不可预知的时间发生，由内核的中断处理程序来处理
4. 内核线程被执行

