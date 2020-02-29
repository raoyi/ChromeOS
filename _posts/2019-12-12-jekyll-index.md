---
layout: post
title:  Jekyll添加目录
date:   2019-12-12
tags:   Jekyll
permalink: /post/jekyll-index
---

Jekyll中给md文档添加目录的方法

目录层级的规则：以标题层级指明目录层级

- 在根目录中的 `_config.yml` 里添加以下内容

```
markdown: kramdown
markdown_ext: "markdown,mkdown,mkdn,mkd,md"
highlighter: rouge

kramdown:
  input: GFM
  syntax_highlighter: rouge
```

- 或者简约的写成这样

```
markdown: kramdown
```

- 在需要加目录的地方增加以下代码

```
* 目录
{:toc}
```

第一行的 `* 目录` 不可少

