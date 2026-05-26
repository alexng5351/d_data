# D_DATA 热梗词条展示区 — JSON Schema 定义 & 接入建议

## 一、项目前端现状分析

| 维度 | 现状 |
|------|------|
| 技术栈 | Vite 5 + React 18（纯 JSX，无 TypeScript） |
| 数据加载方式 | **全部硬编码**在组件 `.jsx` 内（`MemeDetailPage.jsx`、`TrendingDetailPage.jsx`、`EmojiPage.jsx`） |
| 静态资源路径 | `public/assets/` 目录，通过 `getAssetPath(path)` 构建最终 URL |
| 部署方式 | GitHub Pages via `gh-pages`，base 路径 `/d_data/` |
| 现有数据文件 | 无独立 JSON 数据文件 |

---

## 二、JSON Schema 完整定义

### 文件路径：`public/data/meme_candidates.json`

### 顶层结构

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `version` | `string` | ✅ | 数据格式版本号，遵循 SemVer（如 `"1.0.0"`） |
| `updated_at` | `string` (ISO 8601) | ✅ | 该文件最后一次被 Agent 写入的时间戳 |
| `candidates` | `array<MemeCandidate>` | ✅ | 热梗词条列表 |

### MemeCandidate 对象字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | `string` | ✅ | 唯一标识，建议格式 `meme_YYYYMMDD_NNN` |
| `name` | `string` | ✅ | 英文梗名称 |
| `emotion` | `string` | ✅ | 核心情绪 / 使用场景描述 |
| `visual_features` | `string` | ✅ | 核心视觉特征描述 |
| `risk_level` | `string` (enum) | ✅ | 风险评级：`"✅"` 可直接执行 / `"⚠️"` 需处理后执行 / `"❌"` 建议跳过 |
| `risk_note` | `string` | ✅ | 风险说明 |
| `source_url` | `string` (URL) | ✅ | 参考来源链接（KYM 词条页） |
| `reference_image_url` | `string` (URL) | ❌ | 外部参考图链接（原始来源） |
| `reference_image` | `string` | ✅ | 本地参考图路径（相对 `public/`），供 `getAssetPath()` 使用 |
| `fetched_at` | `string` (ISO 8601) | ✅ | Agent 抓取该条目的时间戳 |
| `status` | `string` (enum) | ✅ | 当前状态：`"candidate"` 候选中 / `"reviewed"` 已审核 / `"produced"` 已生产 / `"skipped"` 已跳过 |

### JSON Schema（标准 Draft-07）

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "MemeCandidates",
  "type": "object",
  "required": ["version", "updated_at", "candidates"],
  "properties": {
    "version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+\\.\\d+$"
    },
    "updated_at": {
      "type": "string",
      "format": "date-time"
    },
    "candidates": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "name", "emotion", "visual_features", "risk_level", "risk_note", "source_url", "reference_image", "fetched_at", "status"],
        "properties": {
          "id": {
            "type": "string",
            "pattern": "^meme_\\d{8}_\\d{3}$"
          },
          "name": { "type": "string" },
          "emotion": { "type": "string" },
          "visual_features": { "type": "string" },
          "risk_level": {
            "type": "string",
            "enum": ["✅", "⚠️", "❌"]
          },
          "risk_note": { "type": "string" },
          "source_url": {
            "type": "string",
            "format": "uri"
          },
          "reference_image_url": {
            "type": "string",
            "format": "uri"
          },
          "reference_image": {
            "type": "string",
            "description": "相对 public/ 的路径，如 assets/meme_candidates/xxx.png"
          },
          "fetched_at": {
            "type": "string",
            "format": "date-time"
          },
          "status": {
            "type": "string",
            "enum": ["candidate", "reviewed", "produced", "skipped"]
          }
        }
      }
    }
  }
}
```

---

## 三、示例数据

```json
{
  "version": "1.0.0",
  "updated_at": "2026-05-25T12:00:00Z",
  "candidates": [
    {
      "id": "meme_20260525_001",
      "name": "Realistic Troll Face",
      "emotion": "Smug satisfaction / trolling someone after a prank",
      "visual_features": "Hyper-realistic 3D rendering of the classic Troll Face meme; exaggerated wrinkles, translucent skin texture, uncanny valley smile with visible gums",
      "risk_level": "⚠️",
      "risk_note": "Original Troll Face has complex IP history (Carlos Ramirez). Realistic renditions are derivative enough but avoid exact silhouette match.",
      "source_url": "https://knowyourmeme.com/memes/trollface",
      "reference_image_url": "https://i.kym-cdn.com/entries/icons/original/000/000/091/TrollFace.jpg",
      "reference_image": "assets/meme_candidates/realistic_troll_face.png",
      "fetched_at": "2026-05-25T10:30:00Z",
      "status": "candidate"
    }
  ]
}
```

---

## 四、前端接入建议

### 4.1 数据加载方式：fetch 静态 JSON

由于项目当前**没有后端 API**、所有内容通过 GitHub Pages 静态托管，推荐使用 `fetch` 加载 `public/data/` 下的 JSON 文件：

```jsx
// src/hooks/useMemeCandidates.js
import { useState, useEffect } from 'react'
import { getAssetPath } from '../utils'

export function useMemeCandidates() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetch(getAssetPath('data/meme_candidates.json'))
      .then(res => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        return res.json()
      })
      .then(json => setData(json))
      .catch(err => setError(err))
      .finally(() => setLoading(false))
  }, [])

  return { data, loading, error }
}
```

### 4.2 为什么不 import JSON？

Vite 支持 `import data from './data.json'`，但这会把数据打入 JS bundle。对于 Agent 定期更新的热梗数据：
- **放 `public/data/`** → Agent 只需 push JSON 文件，无需重新 build
- **用 `fetch` 加载** → 前端部署后，数据可独立热更新

### 4.3 图片文件存放路径

```
public/
├── assets/
│   └── meme_candidates/          ← 新建目录
│       ├── realistic_troll_face.png
│       ├── distracted_boyfriend.png
│       └── ...
└── data/
    └── meme_candidates.json      ← 数据文件
```

图片建议：
- **路径格式**：`assets/meme_candidates/{snake_case_name}.{ext}`
- **尺寸规范**：建议宽度 ≤ 800px，格式 PNG/WebP，单张 ≤ 500KB
- **命名规则**：与 `id` 对应的英文蛇形命名（如 `realistic_troll_face.png`）

### 4.4 组件改造方向

现有 `EmojiPage.jsx` 中"实时热梗字条展示区"目前是硬编码的 `trendingMemes` 数组。建议改造为：

```jsx
// 改造前（硬编码）
const trendingMemes = ['Fruitcore Meme Culture', ...]

// 改造后（读取 JSON）
import { useMemeCandidates } from '../hooks/useMemeCandidates'

function EmojiPage() {
  const { data, loading } = useMemeCandidates()
  const trendingMemes = data?.candidates
    ?.filter(c => c.status === 'candidate' || c.status === 'reviewed')
    ?.slice(0, 5) || []
  // ...
}
```

### 4.5 Agent 自动化写入流程

```
Agent 定期抓取 TikTok/KYM
    ↓
生成 meme_candidates.json + 图片文件
    ↓
git push 到 main 分支
    ↓
GitHub Actions 自动 deploy → 前端数据更新
```

现有 `.github/workflows/deploy.yml` 已配置自动部署，Agent 只需 push 到 `main` 分支即可触发更新。

---

## 五、总结

| 项目 | 建议 |
|------|------|
| 数据文件 | `public/data/meme_candidates.json` |
| 图片目录 | `public/assets/meme_candidates/` |
| 加载方式 | `fetch(getAssetPath('data/meme_candidates.json'))` |
| 更新机制 | Agent push JSON + 图片 → GitHub Actions 自动部署 |
| 无需改动 | Vite 配置、部署流程、`getAssetPath` 工具函数 |
| 需新增 | `useMemeCandidates` hook、改造展示组件读取外部数据 |
