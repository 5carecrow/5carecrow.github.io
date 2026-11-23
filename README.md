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

注意：本机若设置了 `HTTP_PROXY` / `HTTPS_PROXY`，`git push` 可能报 `CONNECT tunnel failed 502`；推送前清掉这些变量即可，桌面菜单已自动处理。

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
