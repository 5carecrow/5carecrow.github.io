---
title: "博客上线了"
date: 2026-11-23T19:35:00+08:00
lastmod: 2026-11-23T19:35:00+08:00
draft: false
description: "第一篇：记录博客的搭建过程。"
tags: ["随笔", "Hugo"]
categories: ["记录"]
toc: true
---

博客搭起来了。用的是 Hugo + PaperMod，源码放在 GitHub，推送到 `main` 后由 GitHub Actions 自动构建并发布。

## 这里会写什么

- AI 工具与工作流实践
- 开发过程中的踩坑记录
- 一些值得留下的想法

## 本地写文章

```bash
hugo new posts/2026-11-23-my-post.md
hugo server -D
```

写完 `git add . && git commit -m "new post" && git push`，等几分钟就能在线上看到。
