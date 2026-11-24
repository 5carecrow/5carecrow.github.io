# 5carecrow 的博客

基于 Hugo + 自定义 QQZone 主题（经典 QQ 空间风格）的 GitHub Pages 博客。推送到 `main` 后，GitHub Actions 会自动构建并发布到 <https://5carecrow.github.io/>。

## 本地开发

仓库位置：`E:\devprojects\5carecrow.github.io`，已加入 WorkBuddy 工作空间。桌面入口 `5carecrow-blog.bat` 提供新建文章、预览、构建检查、提交推送等常用操作。

工具已随仓库放在 `tools/`（Hugo 0.170.1 Extended、Dart Sass 1.108.2、Gitleaks 8.30.1），无需全局安装。

命令行方式（Git Bash）：

```bash
cd /e/devprojects/5carecrow.github.io
export PATH="/e/devprojects/5carecrow.github.io/tools/dart-sass/dart-sass:$PATH"
./tools/hugo/hugo.exe server -D
```

打开 <http://localhost:1313> 查看效果。

## 写文章

```bash
hugo new posts/2026-11-24-my-post.md
```

编辑 `content/posts/` 里生成的 Markdown 文件，把 `draft` 改成 `false` 就会在正式站点显示。本仓库统一用 `posts` 作为日志 section，主题会按 `posts` 读取文章。

发布：

```bash
git add .
git commit -m "new post"
git push
```

注意：本机直连 GitHub 不稳定，`git push` 需要走 `127.0.0.1:7890` 代理；桌面菜单已自动设置代理变量。

## 手机上发文（Issue 发文）

不用带电脑、不用装 Git：手机装 GitHub App，进 `5carecrow/5carecrow.github.io` 仓库 → **Issues** → **New issue**：

- **标题**：文章标题
- **正文**：文章内容，直接写 Markdown（粘贴图片会自动生成 GitHub 外链，不用图床）
- **标签**：分类和标签

常用标签写法：

| 标签 | 作用 |
|---|---|
| `随笔`、`Hugo` 等 | 作为文章标签，显示在标签云 |
| `分类:记录` 或 `category:记录` | 作为日志分类 |
| `draft` 或 `草稿` | 存为草稿，站点不显示；去掉后自动发布 |

提交后机器人会在 issue 下回复一条带文章链接的评论。约 1 分钟后文章上线，网址固定为 `https://5carecrow.github.io/posts/issue-<编号>/`，以后改标题也不会变。

补充说明：

- 再次**编辑** issue 会同步更新文章；**删除** issue 会一并删除对应文章。
- 只有 `5carecrow` 账号发的 issue 会被处理，其他人发的不会写进仓库。
- 工作流在 `.github/workflows/issue-to-post.yml`，转换脚本在 `scripts/issue-to-post.py`。
- 草稿和发布状态只由 `draft` 标签控制，不需要改文件。

## 自定义 QQZone 主题

- 主题目录：`themes/qqzone/`（普通目录，不是 git 子模块，可直接改）
- 站点标题、菜单、QQ 空间昵称、公告、心情、音乐盒、访客：`hugo.toml` 的 `[params.qqzone]`
- 样式：`themes/qqzone/static/css/qqzone.css`
- 交互脚本：`themes/qqzone/static/js/qqzone.js`
- 相册图片：放到 `themes/qqzone/static/photos/`，自动显示在 `/photos/`
- 留言板：`/guestbook/`，留言保存在访问者自己的浏览器（localStorage）
- 浏览器标签图标：替换仓库根目录 `static/favicon.ico`、`static/favicon.svg`、`static/apple-touch-icon.png`
- 想切回 Stack：把 `hugo.toml` 的 `theme` 改回 `"Stack"`（子模块仍保留）

## 自定义域名

在 `static/CNAME` 写入域名（例如 `blog.example.com`），并在 DNS 里配置：

- 根域名：A 记录指向 GitHub Pages 当前提供的 IP（见 GitHub 官方文档）
- `www`：CNAME 指向 `5carecrow.github.io`

然后在仓库 Settings → Pages 勾选 Enforce HTTPS。
