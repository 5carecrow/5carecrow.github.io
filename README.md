# 5carecrow 的博客

基于 Hugo + Stack 的 GitHub Pages 博客。推送到 `main` 后，GitHub Actions 会自动构建并发布到 <https://5carecrow.github.io/>。

## 本地开发

需要安装 Hugo Extended（版本与 `.github/workflows/deploy.yml` 中的 `HUGO_VERSION` 保持一致）。

```bash
# 克隆时要带上主题子模块
git clone --recurse-submodules https://github.com/5carecrow/5carecrow.github.io.git
cd 5carecrow.github.io

# 本地预览，草稿也会显示
hugo server -D
```

打开 <http://localhost:1313> 查看效果。

## 写文章

```bash
hugo new posts/2026-11-24-my-post.md
```

编辑 `content/posts/` 里生成的 Markdown 文件，把 `draft` 改成 `false` 就会在正式站点显示。本仓库用 `posts` 作为文章 section（对应 `hugo.toml` 里的 `mainSections = ["posts"]`），不是 Stack 文档默认的 `post`。

发布：

```bash
git add .
git commit -m "new post"
git push
```

## 自定义

- 站点标题、语言、侧栏、菜单、社交链接：编辑 `hugo.toml`
- 侧栏副标题：`[params.sidebar].subtitle`
- 样式微调：`assets/scss/custom.scss`
- 浏览器标签图标：替换 `static/favicon.ico`、`static/favicon.svg`、`static/apple-touch-icon.png`
- 主题版本：子模块 `themes/Stack` 固定在 v3.34.2；要升级先 `git -C themes/Stack fetch --tags`，再 `git -C themes/Stack checkout <新 tag>`，最后提交父仓库的指针变化

## 自定义域名

在 `static/CNAME` 写入域名（例如 `blog.example.com`），并在 DNS 里配置：

- 根域名：A 记录指向 GitHub Pages 当前提供的 IP（见 GitHub 官方文档）
- `www`：CNAME 指向 `5carecrow.github.io`

然后在仓库 Settings → Pages 勾选 Enforce HTTPS。
