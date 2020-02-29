---
layout: post
title:  mount nonempty问题
date:   2019-11-02
tags:   Linux
permalink: /post/mount-nonempty
---

**问题：**

在 mount U盘的时候出了下面的错误

```
FUSE exfat 1.3.0
WARN: volume was not unmounted cleanly.
fuse: mountpoint is not empty
fuse: if you are sure this is safe, use the 'nonempty' mount option
```

**解决方法：**

在mount的时候加 `-o nonempty` 参数
