# Strava Photobook 🚲📖

把你的 **Strava** 骑行数据做成一本可翻页的交互式照片画册，一年一本。电脑端双页展开，
手机端自动切换单页；支持点击、拖动、方向键翻页。

响应式与阅读友好：窄屏（≤700px）自动折为单页并加宽文字栏、放大触控按钮（≥46px）、
适配刘海/底部安全区；正文用容器相对单位（cqw），无论页面大小字号都等比、清晰。

每本画册全部**直接从 Strava API 生成**，无需手动导出数据：

- **封面 + 年度数字**：骑行次数、总里程、累计爬升、在车时长、收藏（kudos）、PR、最长单骑。
- **高光介绍页**：按「收藏最高 / 赛段 PR / 同行人数」挑选的代表骑行，含标题、描述、数据、
  当天刷出的赛段 PR，以及由 GPS 轨迹（polyline）解码而成的**矢量路线图**。
- **照片画廊**：从 Strava 下载骑行照片并缩放。竖图满屏出血，横图完整显示（不裁切）。

视觉默认采用干净的**黑白橙编辑风**，并内置 18 组撞色，共 19 种主题。点击顶栏“主题”
即可即时切换，选择会自动保存，下次打开继续使用。

> 翻页运行时改编自 MIT 许可的
> [create-photo-flipbook-ui](https://github.com/HaichaoLihc/create-photo-flipbook-ui)。

## 快速开始

第一次使用建议直接照着 [从零配置与发布指南](docs/setup.md) 操作。

环境要求：Python 3.9+；Node.js 仅用于可选的运行时契约测试。

```bash
pip install -r requirements.txt

# 1. 一次性授权（会打开浏览器）。需要一个 Strava API 应用，见下方「准备 Strava 应用」。
python -m strava_photobook auth

# 2. 缓存全部活动指标（每约 200 条活动一次请求）。
python -m strava_photobook fetch

# 3. 查看有哪些年份。
python -m strava_photobook years

# 4. 生成某一年，照片直接从 Strava 下载。
python -m strava_photobook build 2026

# 5. 本地预览。
cd books/2026 && python -m http.server 4173 --bind 127.0.0.1

# 6. 一次性 GitHub 授权，然后发布并等待 Pages 真正可访问。
python3 -m strava_photobook github-auth
python3 -m strava_photobook publish 2026
```

## 命令

| 命令 | 作用 |
|---|---|
| `python -m strava_photobook auth` | 一键浏览器 OAuth 授权，把 refresh token 写入 `.env`。 |
| `python -m strava_photobook fetch` | 拉取全部活动概要到 `data/activities.json`。 |
| `strava_photobook years` | 列出年份及每年的骑行数、照片数。 |
| `strava_photobook build <年份>` | 生成 `books/<年份>/`。 |
| `python3 -m strava_photobook github-auth` | 浏览器授权 GitHub，token 安全写入 `.env`。 |
| `python3 -m strava_photobook publish <年份>` | 建仓、上传、启用 Pages，并等待公网页面可打开。 |

## 发布到 GitHub Pages

最省事的方式是安装 GitHub CLI，然后运行 `github-auth` 和 `publish`。`github-auth` 会调用 GitHub
官方浏览器授权。也可创建 GitHub OAuth App、启用 Device Flow，并配置公开的 `GITHUB_CLIENT_ID`，
此时工具使用内置 Device Flow，不依赖 `gh`。自动化环境可直接注入 `GH_TOKEN`。

默认创建公开仓库 `strava-photobook-<年份>`，只把生成后的静态画册写到 `gh-pages` 分支；
`.env`、Strava token、`data/` 和项目源码不会被上传。可以用 `--repo NAME` 自定义仓库名。
同名仓库必须带有本工具标记，否则命令会拒绝覆盖。只有 Pages 构建成功，且公网 HTML
可访问并包含画册标记，命令才会返回成功。

## 准备 Strava 应用

1. 打开 <https://www.strava.com/settings/api>，用 Strava 账号登录。
2. 创建应用：名称随意（如 `strava-photobook`），**Authorization Callback Domain 必须填 `localhost`**。
3. 记下 **Client ID** 和 **Client Secret**。
4. 运行 `python -m strava_photobook auth`：未配置时会提示粘贴 client id/secret，浏览器授权后
   refresh token 自动写入 `.env`（权限 600）。

申请的权限（只读）：`read`、`activity:read_all`、`profile:read_all`——足以读取你的活动
（含私密）、PR 与照片。

## 工作原理

```
Strava API
  ├── /athlete/activities        概要：收藏、PR、同行人、轨迹   ──► data/activities.json
  ├── /activities/{id}           赛段 PR + 描述        （仅高光骑行）
  └── /activities/{id}/photos    原图照片 URL          （入册骑行）
                                              │
                        筛选高光 ──► 生成 ──► books/<年份>/index.html
```

概要请求很省（每约 200 条一次），全量历史几秒缓存完；较贵的逐条请求（PR 赛段、照片下载）
只对真正入册的骑行发起，稳妥落在 Strava 限流内（200 次 / 15 分钟）。

## 项目结构

```
strava-photobook/
├── strava_photobook/
│   ├── cli.py / __main__.py   # 命令行入口
│   ├── config.py              # 环境变量 / .env，无硬编码路径
│   ├── model.py               # Activity 模型 + 高光筛选
│   ├── route.py               # GPS 轨迹解码为内联 SVG
│   ├── theme.py               # 介绍页布局 + 黑白主题
│   ├── book.py                # 编排单年画册
│   ├── source.py              # 从 Strava API 取数据与照片
│   └── strava/                # 自带 OAuth 客户端 + 本地授权服务
├── tools/                     # 门禁：layout_gate.py（布局校验）
├── runtime/                   # 翻页运行时（HTML/JS/CSS + StPageFlip）
├── books/                     # 产出，一年一本（已 gitignore）
└── data/                      # API 缓存 + token（已 gitignore）
```

## 配置

密钥放 `.env`（从 `.env.example` 复制）；其余调优项用环境变量覆盖，均有默认值：

| 环境变量 | 作用 | 默认 |
|---|---|---|
| `STRAVA_CLIENT_ID` / `_SECRET` / `_REFRESH_TOKEN` | Strava 凭证 | — |
| `PHOTOBOOK_ROOT` | 项目根目录 | 当前目录 |
| `PHOTOBOOK_DATA_DIR` / `PHOTOBOOK_BOOKS_DIR` / `PHOTOBOOK_RUNTIME_DIR` | 数据/产出/运行时目录 | `data` / `books` / `runtime` |
| `PHOTOBOOK_PHOTOS_PER_BOOK` | 单本照片上限 | `40` |
| `PHOTOBOOK_FEATURE_RIDES` | 高光介绍页数量 | `6` |
| `PHOTOBOOK_MAX_PHOTO_EDGE` | 照片最长边（像素） | `1600` |
| `GITHUB_CLIENT_ID` | 可选；启用 Device Flow 的 GitHub OAuth App Client ID | — |
| `GITHUB_TOKEN` | `github-auth` 保存的 GitHub token | — |
| `GH_TOKEN` | 自动化 token，优先于 `GITHUB_TOKEN` | — |

### 换主题

打开画册后点击顶栏“主题”，从双色色板中选择。默认是“黑白橙（默认）”；选择不会改变
当前页，并会自动保存到浏览器的 `strava-photobook.theme`。要恢复默认，重新选择“黑白橙
（默认）”，也可以在浏览器开发者工具中清除这个 localStorage 键。

## 门禁检测

两道校验，改样式或生成后跑一遍：

```bash
# 1) 布局门禁（静态、秒级）：断言高光页「文字左栏 / 轨迹右下角」分栏不重叠、
#    轨迹颜色足够浅、关键文字类都有样式。改 theme.py 后必跑。
python -m tools.layout_gate

# 2) 运行时契约（生成后）：校验翻页书结构、封面密度、页尺寸、资源就位。
cd books/<年份> && node --test html-contract.test.mjs
```

布局门禁把「文字栏右边界不得越过轨迹栏左边界」这条几何不变量固化下来——只要成立，
文字再长也不会和轨迹图案堆积遮挡。需要逐页像素级核对时，可本地起服务后在浏览器对每个
高光页测元素矩形碰撞（`?page=N`）。

## 隐私

全程在本机运行。照片、活动数据、凭证都不会离开你的电脑。`.env`、`data/`、`books/`
均已 gitignore，不会提交任何个人数据。

## 许可

MIT，见 [LICENSE](LICENSE)。内置的翻页运行时组件 StPageFlip 保留其自身许可（见 `runtime/vendor/`）。

## 商标声明

本项目为非官方的第三方工具，与 Strava, Inc. 无任何隶属、赞助或背书关系。
「Strava」是 Strava, Inc. 的注册商标，此处仅用于说明本工具处理的数据来源。
