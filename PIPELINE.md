# AICover 2.0 热梗 Meme 贴纸流水线说明

本文档面向接手维护的研发同学，说明从热梗采集到前端展示的完整自动化链路。目标是让你看完后可以独立跑通、排查和扩展这条流水线。

## 1. 项目概述

AICover 2.0 的热梗 Meme 流水线用于把互联网上高传播度、适合聊天场景的 Meme 素材，自动转换成 TikTok 风格的 **2.5D emoji 贴纸**。

整体思路是：先从 Giphy、Reddit 等来源抓取候选 Meme，下载媒体并截取关键帧；再用 AI 按 SOP 对候选素材进行筛选评分；评分通过的条目进入生图队列；最后调用 Crate 工作流生成 2.5D emoji 风格贴纸，并将结果写回 JSON，供前端读取展示。

## 2. 整体流程图

```text
┌──────────────┐
│  scrape 抓取 │
│ Giphy/Reddit │
└──────┬───────┘
       │ 写入 scraped 候选 + 下载媒体/截帧
       v
┌──────────────┐
│ AI 筛选评分  │
│ enrich_memes │
└──────┬───────┘
       │ pending / rejected / needs_review
       v
┌──────────────┐
│ Crate 生图   │
│ generate     │
└──────┬───────┘
       │ generated + generated_at + 图片 URL
       v
┌──────────────┐
│   git push   │
│ 提交 JSON/图 │
└──────┬───────┘
       │ GitHub / 静态资源
       v
┌──────────────┐
│  前端展示    │
│ fetch JSON   │
└──────────────┘
```

## 3. 脚本说明

### 3.1 `scripts/scrape_memes.py`

**功能描述**

从指定平台抓取 Meme 候选素材，标准化元数据，下载媒体文件，并在需要时截取帧图。输出会写入 `public/data/meme/meme_candidates.json`，新增候选默认进入 `scraped` 状态，等待后续 AI 筛选。

**CLI 参数**

```bash
python3 scripts/scrape_memes.py   --platforms giphy,reddit   --limit 20   --dry-run   --skip-media   --headed
```

- `--platforms`：逗号分隔的平台列表，默认使用脚本内配置；当前主要支持 `giphy`、`reddit`。
- `--limit`：每个平台抓取数量。
- `--dry-run`：只打印抓取结果，不写入 JSON。
- `--skip-media`：跳过媒体下载和截帧，只处理元数据。
- `--headed`：以可视浏览器模式运行，适合调试 Playwright 抓取过程。

**输入**

- 平台页面数据，例如 Giphy、Reddit 的趋势或搜索结果。
- 本地配置和 scraper 模块：`scripts/meme_scrapers/`。

**输出**

- 主数据：`public/data/meme/meme_candidates.json`
- 候选媒体/调试数据：`public/data/meme/candidates/`、`public/data/meme/debug/`
- 截帧图片：`public/images/meme/frames/`
- 运行日志：`public/data/meme/scrape_memes_run.log`

### 3.2 `scripts/enrich_memes.py`

**功能描述**

读取 `meme_candidates.json` 中未评分的候选，调用 Crate / LLM 节点按 SOP 进行 6 维评分和硬过滤判断。脚本会把通过筛选的条目标记为 `pending`，把不适合生图的条目标记为 `rejected`，把需要人工确认的条目标记为 `needs_review`。

**CLI 参数**

```bash
python3 scripts/enrich_memes.py --limit 30
python3 scripts/enrich_memes.py --dry-run --limit 5
```

- `--dry-run`：只打印评分结果，不写入 JSON。
- `--limit`：最多处理多少条；`0` 表示不限制。

**输入**

- `public/data/meme/meme_candidates.json`
- 候选条目里的本地帧图路径或远程图片 URL。
- ByteCloud SSO 登录态，用于获取 JWT 并调用 Crate。

**输出**

- 回写后的 `public/data/meme/meme_candidates.json`
- 运行日志：`public/data/meme/enrich_memes_run.log`
- 每条候选新增或更新 AI 评分字段、决策字段、状态字段。

### 3.3 `scripts/generate_stickers.py`

**功能描述**

读取 `public/data/meme/meme_candidates.json`，只处理 `status == "pending"` 的条目。脚本会跳过 `rejected`、`needs_review`、`generated`、`completed` 等状态。对每个 pending 条目，使用 `frame_png_path` 找到对应帧图，并保持现有 Crate API 调用逻辑完成：上传参考图、生成中文 prompt、调用图生图、去背景。生图成功后，将条目状态回写为 `generated`，并记录 `generated_at` 时间戳。

如果某条 pending 候选缺少 `frame_png_path`，或对应文件不存在，脚本会打印 warning 并跳过，不会中断整批任务。

**CLI 参数**

当前脚本没有显式 CLI 参数，直接运行即可：

```bash
python3 scripts/generate_stickers.py
```

**输入**

- `public/data/meme/meme_candidates.json`
- `frame_png_path` 指向的本地帧图文件。
- ByteCloud SSO 登录态，用于自动获取 JWT Token。
- Crate 项目信息、Group ID、API Key，以及 Emoji 风格参考图 URL。

**输出**

- 回写后的 `public/data/meme/meme_candidates.json`
  - `status: "generated"`
  - `generated_at`
  - `generated_image_url`（如成功拿到图生图 URL）
  - `sticker_url`（如成功拿到去背景 URL）
- 运行结果：`public/data/meme/frame_generation_results.json`
- 运行日志：`public/data/meme/frame_generation_run.log`

### 3.4 `scripts/run_pipeline.sh`

**功能描述**

流水线入口脚本，用于串联抓取、AI 筛选、生图等步骤。由于不同阶段的调试频率不同，建议研发同学在改动时先分别跑单个 Python 脚本，确认无误后再用该入口串起来。

**CLI 参数**

以脚本实际实现为准。常见用法建议预留以下能力：

```bash
bash scripts/run_pipeline.sh
bash scripts/run_pipeline.sh --limit 20
bash scripts/run_pipeline.sh --dry-run
```

**输入**

- 各阶段 Python 脚本。
- `public/data/meme/meme_candidates.json`。
- 本地下载的媒体与帧图。

**输出**

- 更新后的候选 JSON。
- 生成结果 JSON 和各阶段日志。

## 4. 数据 Schema：`meme_candidates.json`

`meme_candidates.json` 顶层是一个对象，核心字段如下：

```json
{
  "last_updated": "2026-05-30T01:32:00Z",
  "candidates": [
    {
      "id": "stable-id",
      "source": "giphy",
      "source_url": "https://...",
      "title": "meme title",
      "status": "pending",
      "frame_png_path": "public/images/meme/frames/frame_001.png"
    }
  ]
}
```

### 顶层字段

- `last_updated`：JSON 最近更新时间，ISO 8601 UTC 时间戳。
- `candidates`：候选 Meme 列表。

### 候选条目字段

- `id`：候选唯一 ID。建议保持稳定，避免前端或后续流程重复识别失败。
- `source`：来源平台，例如 `giphy`、`reddit`。
- `source_url`：原始素材页面 URL。
- `media_url`：原始媒体 URL，可能是 GIF、视频或图片。
- `title`：平台侧标题或脚本生成的简短描述。
- `description`：可选，补充描述。
- `tags`：可选，平台标签或归一化标签数组。
- `local_media_path`：下载到本地的原始媒体路径。
- `frame_png_path`：截帧后的 PNG 路径。`generate_stickers.py` 依赖该字段。
- `status`：流水线状态，详见状态机章节。
- `scraped_at`：抓取时间戳。
- `enriched_at`：AI 筛选完成时间戳。
- `generated_at`：贴纸生成完成时间戳。
- `completed_at`：最终资源稳定并完成前端可用状态的时间戳。
- `emotion_clarity_score`：情绪明确度评分，1-5 分。
- `dm_usability_score`：DM 聊天可用性评分，1-5 分。
- `subject_focus_score`：主体聚焦评分，1-5 分。
- `visual_simplicity_score`：视觉简洁度评分，1-5 分。
- `recognizability_64px_score`：64px 小尺寸识别度评分，1-5 分。
- `meme_popularity_score`：传播度与文化认知度评分，1-5 分。
- `ai_decision`：AI 决策，例如 `approve`、`reject`、`review`。
- `ai_reason`：AI 决策原因，便于人工复核。
- `hard_filter_hit`：是否命中硬过滤规则，布尔值。
- `hard_filter_reason`：硬过滤原因。
- `risk_level`：风险级别，例如 `low`、`medium`、`high`。
- `visual_features`：AI 提炼的核心视觉识别特征数组。
- `generated_image_url`：Crate 图生图结果 URL。
- `sticker_url`：去背景后的贴纸 URL，前端优先使用。

### 字段取值范围

- 所有评分字段统一为整数 `1` 到 `5`。
- `status` 必须使用约定枚举，避免脚本漏处理。
- 时间戳建议统一为 UTC ISO 8601 格式，例如 `2026-05-30T01:32:00Z`。
- 本地路径建议使用相对项目根目录的路径，例如 `public/images/meme/frames/xxx.png`，便于跨机器运行。

## 5. Status 状态机

```text
scraped
  │
  ├── pending       # AI 评分通过，等待生图
  │     │
  │     v
  │   generated     # 已完成 Crate 生图，已有生成 URL
  │     │
  │     v
  │   completed     # 图片已稳定入库或前端确认可展示
  │
  ├── rejected      # AI 或硬过滤判定不适合进入生图
  │
  └── needs_review  # 需要人工复核，例如真实人物/版权角色/风险不确定
```

状态说明：

- `scraped`：刚抓取，尚未进行 AI 评分。
- `pending`：AI 评分通过，等待 `generate_stickers.py` 生图。
- `rejected`：不符合贴纸标准，不进入生图。
- `needs_review`：存在不确定风险，需要人工判断。
- `generated`：Crate 已生成贴纸结果，JSON 中应有 `generated_at` 和图片 URL。
- `completed`：资源已稳定沉淀，前端可以长期展示。

`generate_stickers.py` 只处理 `pending`。这能避免重复消耗 Crate 额度，也能避免把 rejected 或 needs_review 的素材误送进生图。

## 6. 筛选标准摘要

AI 筛选基于 6 个维度评分，每个维度 1-5 分：

1. **emotion_clarity_score**：情绪是否一眼明确，是否能被快速理解。
2. **dm_usability_score**：是否适合 DM 聊天场景，能否表达常见反应。
3. **subject_focus_score**：主体是否单一突出，是否避免多人或复杂主体。
4. **visual_simplicity_score**：背景是否干净，是否避免大量文字和复杂噪声。
5. **recognizability_64px_score**：缩小到 64px 后是否仍能识别核心情绪。
6. **meme_popularity_score**：传播度和文化认知度，是否具备 Meme 共识。

硬过滤规则：

- 纯风景、纯品牌、纯物品且缺少情绪表达。
- 多人群体，主体不清晰或互动关系复杂。
- 大量文字叠加，必须依赖文字才能理解。
- 强政治、宗教争议人物或敏感公共人物。
- 依赖音频、上下文或长视频剧情才能理解。
- 明显不适合转成 2.5D emoji 贴纸的低清晰度素材。

## 7. 环境依赖

### Python 依赖

建议使用 Python 3.10+。核心依赖包括：

```bash
pip3 install requests playwright
python3 -m playwright install chromium
```

如 scraper 或媒体处理模块使用到额外包，请根据报错补充安装。常见可能依赖包括：

```bash
pip3 install pillow imageio opencv-python
```

### 账号与登录态

- 需要 ByteCloud SSO 登录态。
- JWT Token 已由脚本自动化获取，命令为：

```bash
bytedcli --json --site i18n-tt auth get-bytecloud-jwt-token
```

如果 token 获取失败，请先确认本机已完成 ByteCloud / bytedcli 登录。

### Crate 配置

`generate_stickers.py` 内维护 Crate 项目信息、Group ID、API Key、节点 ID 和 Emoji 风格参考图 URL。修改这些配置前，请先确认 Crate 工作流节点结构没有变化。

## 8. 如何运行

### 8.1 进入项目目录

```bash
cd /Users/bytedance/AICover_2.0
```

### 8.2 抓取候选

```bash
python3 scripts/scrape_memes.py --platforms giphy,reddit --limit 20
```

调试时可以先 dry-run：

```bash
python3 scripts/scrape_memes.py --platforms giphy --limit 5 --dry-run
```

### 8.3 AI 筛选评分

```bash
python3 scripts/enrich_memes.py --limit 30
```

调试时：

```bash
python3 scripts/enrich_memes.py --dry-run --limit 5
```

### 8.4 生成 2.5D emoji 贴纸

```bash
python3 scripts/generate_stickers.py
```

运行前建议检查：

```bash
python3 -m json.tool public/data/meme/meme_candidates.json > /tmp/meme_candidates.check.json
```

确认 `pending` 条目都有有效的 `frame_png_path`。

### 8.5 提交到 Git

```bash
git status
git add public/data/meme/meme_candidates.json public/images/meme scripts PIPELINE.md
git commit -m "Update meme sticker pipeline"
git push
```

### 8.6 前端展示

前端读取路径：

```text
/data/meme/meme_candidates.json
```

展示时建议优先使用：

1. `sticker_url`：去背景后的贴纸图。
2. `generated_image_url`：原始图生图结果。
3. `frame_png_path`：仅用于调试或兜底预览。

## 9. 目录结构

以下是 `scripts/` 和 `public/` 下与 Meme 流水线相关的主要结构：

```text
AICover_2.0/
├── PIPELINE.md
├── scripts/
│   ├── scrape_memes.py                 # 抓取 Giphy/Reddit 候选
│   ├── enrich_memes.py                 # AI 筛选评分，回写 pending/rejected/needs_review
│   ├── generate_stickers.py            # 只处理 pending，调用 Crate 生图
│   ├── run_pipeline.sh                 # 流水线串联入口
│   ├── make_meme_overview.py           # 生成 Meme 概览/调试辅助
│   ├── translate_candidate.py          # 候选内容翻译辅助
│   ├── pinterest_batch_collect.py      # Pinterest 批量采集实验脚本
│   ├── pinterest_collect_verify.py     # Pinterest 采集校验脚本
│   ├── pinterest_scene_config.json     # Pinterest 场景配置
│   └── meme_scrapers/
│       ├── __init__.py
│       ├── base.py                     # scraper 基类/公共接口
│       ├── giphy.py                    # Giphy 抓取实现
│       ├── reddit.py                   # Reddit 抓取实现
│       ├── media.py                    # 媒体下载与截帧
│       ├── normalize.py                # 字段归一化
│       └── storage.py                  # JSON/文件存储辅助
└── public/
    ├── data/
    │   ├── meme/
    │   │   ├── meme_candidates.json            # 主数据文件，前端读取
    │   │   ├── frame_generation_results.json   # 生图运行结果
    │   │   ├── scrape_memes_run.log            # 抓取日志
    │   │   ├── enrich_memes_run.log            # AI 筛选日志
    │   │   ├── frame_generation_run.log        # 生图日志
    │   │   ├── candidates/                     # 候选原始数据/媒体缓存
    │   │   ├── debug/                          # 调试输出
    │   │   └── generation/                     # 生成阶段中间数据
    │   └── covers/
    │       └── covers_candidates.json          # AI Cover 数据，和 Meme 流水线隔离
    └── images/
        ├── meme/
        │   ├── frames/                         # Meme 截帧图，generate 依赖
        │   ├── giphy_preview.png
        │   └── meme_ref_preview.png
        └── covers/                             # AI Cover 图片资源
```

## 10. 维护建议

- 修改筛选逻辑前，先阅读 SOP 文档，确保 6 个维度和硬过滤规则一致。
- 生图脚本只处理 `pending`，不要为了调试临时改成全量扫 frames，容易重复消耗额度。
- 每次运行后检查 `meme_candidates.json` 的 `last_updated`、`status`、`generated_at` 和图片 URL。
- 如果 Crate 节点结构变更，优先确认节点 ID、model ID、输入输出字段，再改脚本。
- 前端只依赖稳定 JSON 路径：`/data/meme/meme_candidates.json`，不要把临时日志文件接入正式展示。
