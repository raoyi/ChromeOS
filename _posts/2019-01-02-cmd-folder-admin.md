---
layout: post
title:  CMD获取文件夹的管理员权限
date:   2019-01-02
tags:   CMD Windows 管理员权限
permalink: /post/cmd-folder-admin
---

以管理员身份运行cmd

```
takeown /f 文件夹名称 /r
```

如D盘下面的mypc文件夹，命令为

```
takeown /f d:\mydata /r
```
