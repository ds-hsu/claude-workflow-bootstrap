# Coverage State 規格 — `wiki/coverage/`

> **這個目錄是什麼**：`{{PRODUCT_DISPLAY_NAME}}` 的「機器層知識索引」。每個主題一份 topic 檔，記錄該主題的覆蓋深度（coverage level）、涵蓋的 wiki 頁清單、最後 ingest 日期。
> **誰寫入**：**只有 `/ingest`**（依 CLAUDE.md 核心原則第 6 條「禁止直接寫入 wiki/」鐵律）。
> **誰讀取**：`/wiki-query`（讀 topic 找入口、讀 coverage level 與 wiki_pages）。
> **與 gap 的關係**：本目錄**不存 gap entry**。gap 的事實來源在 `raw/coverage-gaps/{topic}.md`（見 [gap-source-spec.md](../../raw/coverage-gaps/gap-source-spec.md)）。每個 topic 檔結尾以一行 pointer 指向對應的 raw 端 gap 檔。
> **與 `wiki/index.md` 的關係**：`index.md` 是人類層的目錄；`coverage/` 是機器層的索引。兩者互補，不重複。

## 結構

```
wiki/coverage/
├── coverage-state-spec.md     ← 本檔（規格說明）
└── topics/
    ├── {topic-id-1}.md
    ├── {topic-id-2}.md
    └── ...
```

每個主題一個 `.md` 檔。檔名（去除 `.md`）= topic id（kebab-case）。

## Topic 檔案格式

```yaml
---
id: example-topic
title: 範例主題
category: procedures             # systems / procedures / troubleshooting / tech-notes / entities / concepts
coverage: partial                # none | stub | partial | comprehensive | authoritative
wiki_pages:
  - procedures/某流程.md
  - troubleshooting/某問題.md
last_ingest: 2026-05-13
---

## 已覆蓋面向

> 由 /ingest 自動填寫；本段 LLM 從 wiki_pages 內容綜合產出。

- 主流程描述（comprehensive）
- 例外狀況處理（partial）

> **Gaps**：見 [`raw/coverage-gaps/example-topic.md`](../../../raw/coverage-gaps/example-topic.md)（事實來源；本檔不鏡像 gap entry）。
```

## Front-matter 欄位

| 欄位 | 必填 | 規則 |
|------|------|------|
| `id` | ✅ | kebab-case；與檔名一致 |
| `title` | ✅ | 主題顯示名稱（繁中為主） |
| `category` | ✅ | 對應 wiki 頁面 type 之一：systems / procedures / troubleshooting / tech-notes / entities / concepts |
| `coverage` | ✅ | 5 級：見下方「Coverage 等級」 |
| `wiki_pages` | ✅ | 陣列，列出本主題涵蓋的 wiki 頁（相對 `wiki/` 路徑） |
| `last_ingest` | ✅ | YYYY-MM-DD；最後一次有 ingest 觸及本主題的日期 |

## Coverage 等級

| 等級 | 含義 | 觸發條件 |
|------|------|----------|
| `none` | 主題存在於認知裡但無內容 | stub topic（由 `/ingest` 因 `raw/coverage-gaps/{topic}.md` 已存在但對應 wiki 頁尚未建立時自動建立） |
| `stub` | 僅有骨架（front-matter + 一兩段空模板） | 對應 wiki 頁面僅有 front-matter |
| `partial` | 涵蓋主要面向但有明顯空白 | 至少 3 個段落填寫，但仍有 open gap |
| `comprehensive` | 主題已被深度涵蓋 | 主要 aspect 全有出處，無 high severity gap |
| `authoritative` | 與 raw 100% 同步且無爭議 | comprehensive + 連續多次 query 無新 gap |

升降原則：
- `/ingest` 完成後若新增大量內容 → 自動評估升級
- `/wiki-query` 觸發 `RAW_ALSO_MISSING` 的 high gap → 不升級或降級

## `/wiki-query` 對本目錄的使用方式

1. **找入口**：掃 `topics/`，找出與問題主題相關的 topic 檔；命中後讀 frontmatter 取得 `wiki_pages` 加入候選頁面
2. **取 coverage level**：答案末尾標註「coverage: partial」，提示讀者可靠度
3. **取 raw 端 gap 清單**：依 topic id 對應到 `raw/coverage-gaps/{topic}.md`，讀其中 `status: open` 或 `resolved_pending` 的 gap entry（**不讀本目錄的 ## Gaps 段——本目錄不鏡像 gap**）

## `/ingest` 對本目錄的維護動作（Step 8c — Coverage Metadata Sync）

每次 `/ingest` 完成內容寫入後：

1. 掃描 `raw/coverage-gaps/*.md`，取得所有 topic id 清單
2. 對每個 topic：
   - 若 `topics/{topic}.md` 不存在 → 建立 stub topic（`coverage: none`、`wiki_pages: []`）
   - 若本次 ingest 觸及該 topic 對應的 wiki 頁 → 更新 frontmatter 的 `wiki_pages`、`coverage`（依升降原則）、`last_ingest`
   - **不修改 `## 已覆蓋面向` 與 pointer 行**（pointer 是 idempotent 的固定格式）

**注意**：本步驟**不再覆寫 `## Gaps` 段**（已改為 raw-only 設計；gap 不鏡像）。

## 設計哲學

- **產品自治**：本目錄結構只服務本產品 wiki 內部，不為跨產品聯邦預留欄位
- **與 `index.md` 並存**：人類目錄 vs 機器索引，不強迫對齊
- **gap 不鏡像**：避免「raw 動過、wiki 還沒重編譯」的中間狀態與字串覆寫風險；`/wiki-query` 一律去 raw 讀
