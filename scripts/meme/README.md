# 热梗 Meme 流水线

这里存放 AICover_2.0 的热梗 Meme 自动化流水线脚本。

## 入口

```bash
cd /Users/bytedance/AICover_2.0
bash scripts/meme/run_pipeline.sh
```

## 主要脚本

- `scrape_memes.py`：抓取候选 Meme / GIF，并生成截帧。
- `enrich_memes.py`：按筛选规则对候选内容评分和标记状态。
- `generate_stickers.py`：基于通过筛选的候选内容生成贴纸。
- `meme_scrapers/`：Giphy、Reddit 等平台抓取模块。
