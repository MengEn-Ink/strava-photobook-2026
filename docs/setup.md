# 从零生成并发布骑行画册

这份指南面向第一次使用命令行的用户。完成后，你会得到一本本地画册和一个任何人都能打开的 GitHub Pages 链接。

## 1. 准备环境

需要 Python 3.9 或更高版本。运行 `python3 --version` 检查，再进入项目目录执行 `python3 -m pip install -r requirements.txt`。预期命令正常结束，没有红色错误。

## 2. 创建 Strava API 应用

1. 登录 https://www.strava.com/settings/api 。
2. 创建一个 Strava API 应用，名称可填 Strava Photobook。
3. `Authorization Callback Domain` 填 `localhost`。
4. 记下 Client ID 和 Client Secret。它们只保存在本机 `.env`。

## 3. 授权并获取活动

依次运行 `python3 -m strava_photobook auth`、`python3 -m strava_photobook fetch`、`python3 -m strava_photobook years`。浏览器会要求确认 Strava 只读权限。预期 fetch 显示缓存条数，years 列出可生成的年份。

## 4. 生成并预览

运行 `python3 -m strava_photobook build 2026`，再进入 `books/2026` 并执行 `python3 -m http.server 4173 --bind 127.0.0.1`。打开 http://127.0.0.1:4173 。预期封面出现，点击、拖动或方向键可以翻页；高光活动与照片连续出现，照片页显示活动标题和数据。按 Ctrl+C 停止预览。

顶栏“主题”中有默认黑白橙和 18 组撞色，共 19 种主题。点击色板立即切换，不会跳页；选择会自动保存，下次打开仍然生效。要恢复默认，重新选择“黑白橙（默认）”。如果需要彻底清除偏好，可在浏览器开发者工具的 Local Storage 中删除 `strava-photobook.theme`。

## 5. 授权 GitHub

运行 `python3 -m strava_photobook github-auth`。若已安装 GitHub CLI，终端会显示一次性验证码并打开浏览器。若没有，可创建 GitHub OAuth App、启用 Device Flow，并在 `.env` 设置 `GITHUB_CLIENT_ID`。预期终端显示授权成功并保存 `GITHUB_TOKEN`；不要复制或提交 token。

## 6. 公开发布

运行 `python3 -m strava_photobook publish 2026`。它会创建公开仓库、上传到 gh-pages 分支、开启 Pages，并等待公网 HTML 可访问。预期输出包含仓库地址和 Pages 地址。

公开页面包含照片、活动标题、日期、路线与统计。执行前请确认允许公开。以后重新生成后运行同一条 publish 命令即可更新。

## 常见问题

- 没有活动缓存：先运行 fetch。
- 没有该年份：运行 years 查看年份。
- GitHub 验证码过期：重跑 github-auth，只使用最新验证码。
- 拒绝覆盖同名仓库：用 `--repo 新名字` 发布。
- Pages 未完成：稍后重跑 publish，流程会安全复用已有仓库。
- LibreSSL 警告：建议使用 Homebrew Python 3.11+；警告本身不代表生成失败。

## 隐私与文件位置

- `.env` 保存凭据，已被 Git 忽略。
- `data/` 保存原始活动缓存，已被 Git 忽略。
- `books/` 保存生成画册，已被 Git 忽略；publish 只公开指定年份的静态成品。
