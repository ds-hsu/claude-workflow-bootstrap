# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> ⚠️ 本檔由 claude-workflow-bootstrap 產生，依據 Karpathy LLM Wiki 模式設計。
> 內文的 `<your-architecture>`、`<your-notes>`、`<Product1>`、`<ExampleSystemA>` 等
> 佔位符需要依你的產品實際情況調整。建議初次啟用前走一遍全文並替換所有佔位符。

# {{PRODUCT_DISPLAY_NAME}} — LLM 維護式知識庫 Schema

> 本檔案是 {{PRODUCT_NAME}} 產品 wiki 的 schema 與工作流程定義。依據 Andrej Karpathy 的 LLM Wiki 模式
> (https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) 設計。

## 常用指令

本專案不是程式碼，沒有 build/test 流程。所有操作透過 Claude Code Skills（slash commands）執行：

| 指令 | 用途 |
|---|---|
| `/ingest` | 掃描 `raw/` 下尚未進入 wiki 的 markdown，寫入 wiki 頁面，並同步 Coverage State / Gap |
| `/ingest-isms` | 掃描 `raw/isms/` 子資料夾，將 PDF/DOCX/PNG 等整合為結構化 markdown + 分析文件（含 `## 知識盲點` gap-candidate） |
| `/ingest-drawio` | 將 `.drawio` 流程圖轉 Mermaid markdown 存入 `raw/drawio/` |
| `/wiki-query` | 從 wiki 回答使用者問題；查不到時寫入 `raw/coverage-gaps/` |
| `/daily-log` | 將本次工作摘要 append 到 `raw/daily/{userName}/{yyyyMMdd}.md` |

**健康檢查**（PowerShell）：
```powershell
.\scripts\lint.ps1
```

**圖片補檔**（Git Bash）：
```bash
bash scripts/restore-attachments.sh
```

**Release Notes 產生**（Git Bash）：
```bash
bash scripts/generate-release-notes.sh
```
產出位置：`release_note/`

### 工具前置需求

PDF/DOCX 轉換需要 Python + markitdown：
```bash
python -m markitdown --version   # 需 0.1.5+
python -c "import pymupdf"       # PDF 渲染需要 PyMuPDF
```

## Karpathy LLM Wiki 方法的核心觀念

本專案的設計哲學源自 Karpathy 的 gist。以下 6 點是這套方法的核心，後續所有規範都是它在 {{PRODUCT_NAME}}-wiki 的具體落地：

1. **持久編譯，而非重複檢索（Persistent Compilation Over Retrieval）** — 知識寫下一次後就持續維護。LLM 把新來源整合進既有頁面，而不是每次提問都從原始檔重新尋找答案。Wiki 是一個會「複利成長」的持久產物。
2. **三層架構（Raw / Wiki / Schema）** — Raw 是不可變的事實來源；Wiki 是 LLM 維護的 markdown 編譯產物；Schema（本檔）是結構與品質的規範。三層職責清楚分離。
3. **人機分工（Human-LLM Division of Labor）** — 人類負責策展原始來源、提出問題、做最終判斷；LLM 負責簿記、跨頁交叉參考、矛盾偵測、結構一致性等大量重複勞動。
4. **Write-back 複利（Knowledge grows through use）** — Query 過程產生的綜合、比對、新洞見要回寫進 wiki，知識庫透過「被使用」而非只靠「被 ingest」成長。
5. **自動化維護（Automated Lint）** — 定期偵測矛盾、過時頁、孤立頁、broken link、未 ingest 的 raw，讓知識庫規模化後仍能保持健康。
6. **為何可行** — 人類過去因維護成本太高而放棄 wiki；LLM 不會疲倦，使知識保存的邊際成本趨近於零。這是「LLM 維護式知識庫」相對於傳統 wiki 與 RAG 的根本優勢。

## 三層架構

```
./
├── raw/                       # 第 1 層：原始資料（不可變快照，唯一事實來源）
│   ├── <your-notes>/           # 既有系統維運筆記（每個產品線依情況建立）
│   ├── <your-architecture>/    # ARCHITECTURE.md + 各子專案 README 快照
│   ├── drawio/                 # draw.io 流程圖轉換的 Mermaid markdown
│   ├── isms/                   # ISMS 變更單快照
│   └── coverage-gaps/          # Gap 事實來源（單一寫入入口；/wiki-query 與 /ingest 8a 寫入）
├── wiki/                      # 第 2 層：由 LLM 維護的 markdown 知識庫
│   ├── index.md               # 內容導向目錄
│   ├── log.md                 # Ingest/lint 日誌（append-only）
│   ├── _templates/            # 六種頁面模板
│   ├── coverage/              # 機器層知識覆蓋地圖（coverage level + 指向 raw gap 的 pointer）
│   │   └── topics/            # 每個主題一個 .md 檔
│   ├── systems/               # 系統頁（<Product1>、<Product2>、<ExampleSystemA>…）
│   ├── procedures/            # 操作流程
│   ├── troubleshooting/       # 故障排除
│   ├── tech-notes/            # 技術筆記
│   ├── entities/              # 實體頁（資料表、API、主機）
│   └── concepts/              # 概念頁（CICD、OLTP、TLS…）
├── release_note/              # generate-release-notes.sh 產出位置
├── scripts/                   # 維護工具腳本（lint.ps1、restore-attachments.sh、generate-release-notes.sh）
├── .claude/skills/            # Claude Code Skills（ingest、ingest-isms、ingest-drawio）
└── CLAUDE.md                  # 本檔：schema 與工作流程
```

## 架構大局觀（Big Picture）

理解本專案需要先理解 **「兩階段 ingest」** 與 **「三類 raw 來源」** 的對應關係：

**兩階段 ingest 流程**：
1. **第一階段（前處理）**：原始檔（PDF/DOCX/.drawio）→ `/ingest-isms` 或 `/ingest-drawio` → 結構化 markdown + 分析文件，存回 `raw/`
2. **第二階段（寫入 wiki）**：`raw/*.md` → `/ingest` → wiki 頁面（systems/procedures/...）

**三類 raw 來源** 對應不同的權威階層（見「來源權威階層」章節）：
- `raw/<your-architecture>/` — L1/L2，跨系統權威，是 wiki 的骨幹
- `raw/drawio/` — L2，結構化流程圖
- `raw/<your-notes>/`、`raw/isms/` — L3，個人筆記與 ISMS 變更單

**為什麼有 `raw/isms/{資料夾}/{資料夾}-分析.md`？** ISMS 變更單比一般 raw 多一個產出：分析文件交叉比對既有 wiki 系統頁，輸出修改建議與工作項目拆解，供開發者直接建 ticket。

**為什麼 wiki 頁面用 `[[wikilink]]` 而非 markdown link？** 為了相容 Obsidian（本專案有 `.obsidian/` 目錄），讓人類可以直接用 Obsidian 瀏覽 wiki。

## 核心原則

1. **raw 不可變** — 任何衝突以 raw 為準；wiki 是編譯產物
2. **每個 wiki 頁面必須有 `sources`** — 指回 raw 檔，讓讀者能反查原文
3. **交叉連結優先** — 使用 `[[relative/path]]` wikilinks，避免孤立頁
4. **維護成本趨近於零** — 新增 raw 時由 LLM 自動更新 10-15 個相關頁面
5. **LLM 摘要會遺失細節** — 細節放在 raw，wiki 負責結構與導航
6. **禁止直接寫入 wiki/** — 所有新知識必須先寫入 `raw/` 作為事實來源，再透過 `/ingest` 寫入 wiki。即使是調查結果、bug 分析、系統行為發現，都必須先存為 raw 檔。**絕對不可跳過 raw 直接建立或更新 wiki 頁面。**

## 命名規範

- 檔名：英文小寫短名或繁中，空白以 `-` 取代
- 頁面類型對應資料夾：`systems/`、`procedures/`、`troubleshooting/`、`tech-notes/`、`entities/`、`concepts/`
- 系統名稱使用 `ARCHITECTURE.md` 的正式名稱（如 `<ExampleSystemA>`、`<ExampleSystemC>`）

## Front-matter 規格（每頁必備）

```yaml
---
title: <頁面標題>
type: system | procedure | troubleshooting | tech-note | entity | concept
system: <主要系統，如 <Product1> / <Product2>；可陣列>
tags: [標籤1, 標籤2]
sources:
  - raw/<your-notes>/xxx.md
  - raw/<your-architecture>/ARCHITECTURE.md
generated_by: ingest@v1        # prompt 名稱@版本，手動頁面寫 manual
updated: 2026-04-07
---
```

- `sources` 必須是相對於專案根目錄的路徑，且必須是實際存在的檔案
- `system` 用於交叉索引；`tags` 用於分眾檢索
- `generated_by` 用於追溯：知道這頁是哪個 prompt 版本的產出，未來改進 prompt 時可回頭重跑

## 頁面模板（見 `wiki/_templates/`）

| type | 模板檔 | 主要區塊 |
|---|---|---|
| system | `system.md` | 概述 / 架構 / 元件 / 相關頁面 / 細節來源 |
| procedure | `procedure.md` | 前置條件 / 步驟 / 驗證 / 相關故障 |
| troubleshooting | `troubleshooting.md` | 症狀 / 原因 / 解法 / 預防 / 相關概念 |
| tech-note | `tech-note.md` | 背景 / 程式碼範例 / 注意事項 |
| entity | `entity.md` | 定義 / 欄位或屬性 / 關聯 / 使用者 |
| concept | `concept.md` | 定義 / 應用場景 / 相關概念 |

## Ingest 工作流程

當新的 raw 檔加入或既有 raw 檔需要 ingest 時：

1. **讀取** raw 檔完整內容
2. **抽取** 其中的系統、實體、概念、程序、故障案例
3. **更新/新建** 相關 wiki 頁面（通常 5-15 個），使用對應模板
4. **更新交叉參考**：在現有頁面加入新的 `[[...]]` 連結
5. **更新 `index.md`**：將新頁面加入對應類別
6. **追加 `log.md`**：紀錄 ingest 日期、raw 來源、觸及的頁面清單
7. **每個 raw 檔至少出現在一個 wiki 頁面的 `sources` 欄位**

## Query 工作流程

當使用者提問時：

1. 先查 `wiki/index.md` 找入口
2. 讀相關 wiki 頁面，沿 `[[...]]` 連結擴展
3. 若 wiki 資訊不足或有疑義，讀對應的 raw 檔補全
4. 合成答案，並在回覆中附上引用的 wiki 頁面路徑
5. 若發現有價值的新洞見，沉澱為新頁面並更新 index.md 與 log.md

## Daily-log 工作流程（每日工作經驗紀錄）

**規則**：每次完成有意義的工作後，必須呼叫 `/daily-log` 將摘要 append 到 `raw/daily/{userName}/{yyyyMMdd}.md`。

**有意義的工作**包括：bug fix、feature、troubleshooting、知識庫更新（ingest/新建 wiki 頁）、程式碼修改、設定變更。

**不需要呼叫**的場景：純查詢（沒有產出）、閒聊、只讀探索、回答問題但未修改任何檔案。

## Lint 工作流程（定期健康檢查）

執行時檢查以下項目並產出報告：

- **孤立頁面**：未被任何其他頁面的 `[[...]]` 引用（根頁除外）
- **broken wikilink**：指向不存在的頁面
- **缺失反向連結**：A 引用 B 但 B 未引用 A（視情況決定是否補）
- **過時頁面**：`updated` 超過 90 天未更新
- **矛盾聲明**：同一事實在不同頁面有不同描述
- **未引用的 raw 檔**：raw 下存在但未被任何 wiki 頁面 `sources` 引用
- **broken source**：`sources` 指向的 raw 檔不存在

## Coverage State 與 Gap Lifecycle

> 完整規格見 `wiki/coverage/coverage-state-spec.md` 與 `raw/coverage-gaps/gap-source-spec.md`。本章節為摘要與整體心智模型。

**為什麼需要 Coverage State？** wiki 規模變大後，「我們對某主題的覆蓋深度如何」「哪些面向沒寫到」會逐漸無從掌握。Coverage State 是機器層的索引，記錄每個主題的覆蓋等級（5 級）與已知 gap，補足 `index.md` 這個人類層目錄。

**兩個目錄的分工（raw-only gaps）**：

| 目錄 | 角色 | 內容 | 寫入者 |
|---|---|---|---|
| `raw/coverage-gaps/{topic}.md` | **Gap 唯一事實來源** | gap entry 清單（含 status、severity、search_trail）| `/wiki-query` Step Gap、`/ingest` Step 8a/8b、`/wiki-query` Step Verify |
| `wiki/coverage/topics/{topic}.md` | **Coverage metadata 索引** | frontmatter（coverage level、wiki_pages、last_ingest）+ `## 已覆蓋面向` + 一行 pointer 指向 raw | 只有 `/ingest` Step 8c |

**重要：本設計採 raw-only gaps**——wiki 端**不鏡像** gap entry。`/wiki-query` 一律去 raw 讀 gap，避免「raw 動過、wiki 還沒重編譯」的中間狀態與字串覆寫風險。

**Gap 兩條來源路徑**：

1. **Query-time discovery**：使用者問問題 → `/wiki-query` 查不到 → 寫 `raw/coverage-gaps/{topic}.md`
2. **Analysis-time discovery**：`/ingest-isms` 分析 ISMS 變更單時，在 `raw/isms/{folder}/{folder}-分析.md` 的 `## 知識盲點` 段寫 gap-candidate → 下次 `/ingest` Step 8a 收割為正式 gap

**Gap status 與兩階段驗證**：

```
open → resolved_pending → resolved → closed
              ↑              ↓
              └── reopened ──┘（若 query 答不出）
```

`/ingest` 寫入相關內容後**只能切 `resolved_pending`**，不可直接 `closed`。必須等下次 `/wiki-query` 觸到此 topic、實際驗證可回答，才切 `resolved`；連續 N 次（建議 N=2）驗證後才能 `closed`。**避免 LLM 主觀判斷誤關**。

**核心原則第 6 條延伸**：依「禁止直接寫入 wiki/」鐵律，`/wiki-query` 與 `/ingest-isms` 都不得寫 `wiki/`（含 `wiki/coverage/topics/`）。所有 gap 在進入 wiki 前必須先以 raw 形式存在，由 `/ingest` 統一維護 `wiki/coverage/topics/` 的 coverage metadata（注意：wiki 端不存 gap entry，只存 metadata + pointer）。

## raw 快照策略

外部來源匯入 raw 時必須遵守：

1. 在檔頭加入註記：
   ```
   > snapshot: YYYY-MM-DD
   > source: <原始絕對路徑或 URL>
   ```
2. **動態資料**（如 Postgres、API）用日期資料夾版本化：
   `raw/postgres-snapshots/2026-04-07/`，不覆蓋舊快照
3. **靜態文件**（如 README）直接放置；若原檔更新，建立新副本或在檔頭加 `> updated-snapshot: YYYY-MM-DD`
4. 匯入完成後必須在該目錄建 `README.md` 說明來源、匯出指令、筆數

## index.md 結構

依類別組織，每項目一行：
```markdown
## Systems
- [[systems/<YourSystem>]] — <your primary system>
- [[systems/<ExampleSystemA>]] — .NET 8 排程系統（Quartz.NET）

## Procedures
- [[procedures/某 SOP 範例]] — <某 SOP 範例> SOP
```

## log.md 結構

append-only 時間序日誌。每次 ingest / query-sediment / lint 必須留下可追溯的條目：

```markdown
## 2026-04-07 14:30 ingest — raw/<your-architecture>/ARCHITECTURE.md
- prompt: ingest@v1
- operator: claude-opus-4-6
- inputs: raw/<your-architecture>/ARCHITECTURE.md
- 新建: systems/<ExampleSystemA>.md, systems/<ExampleSystemB>.md, systems/<ExampleSystemC>.md, ...
- 更新: index.md（新增 7 個 Systems 條目）
- 未決: TODO 3 項（見各頁面）
- 自檢: front-matter ✓, wikilinks ✓, sources ✓
```

---

# Prompts（核心）

> 以下是整個系統的品質來源。**Prompt 就是 schema 的一部分**——模板決定結構，prompt 決定內容品質。
> 每個 prompt 有版本號。任何修改都必須 bump 版本並在此處留下 changelog。
> 使用時：LLM 把對應 prompt 載入 context，依其規範執行；執行結果須在 log.md 記錄使用的 prompt 版本。

## Prompt Registry

| 名稱 | 當前版本 | 用途 |
|---|---|---|
| `ingest` | v4 | 將 raw 檔分析並寫入 wiki 頁面，並同步 Coverage State / Gap |
| `query` | v2 | 回答使用者問題、留下 search_trail、查不到時寫入 raw/coverage-gaps/ |
| `lint` | v2 | 健康檢查與報告 |

### Changelog
- **ingest@v1** (2026-04-07)：初版
- **ingest@v2** (2026-04-07)：新增衝突處理、來源權威階層、長檔分段、stub 頁、idempotency、繁中規範、as-of 日期、頁面拆分準則、dry-run 參數
- **ingest@v3** (2026-04-08)：新增「圖片感知」規則 — 保留 raw 中的圖片引用、改寫為相對路徑指向 raw/.attachments/、為無意義 alt 自動生成中文描述
- **ingest@v4** (2026-05-13)：新增 Step 8 Gap Lifecycle Sync — 8a 從 `raw/isms/*/分析.md` 收割 gap-candidate 寫入 `raw/coverage-gaps/`；8b 切換覆蓋的 gap 為 `resolved_pending`（兩階段驗證，不直接 closed）；8c Coverage Metadata Sync：維護 `wiki/coverage/topics/{topic}.md` 的 frontmatter + 已覆蓋面向 + pointer（**raw-only gaps 設計：wiki 端不鏡像 gap entry**）
- **query@v1** (2026-04-07)：初版
- **query@v2** (2026-05-13)：整合 Coverage State（raw-only gaps）— Step 1b 從 wiki 端讀 metadata（coverage level / wiki_pages）、從 raw 端讀 gap entry；Step Gap 依三種失敗分類（TOPIC_MISSING / DETAIL_MISSING / RAW_ALSO_MISSING）寫 `raw/coverage-gaps/{topic}.md`；Step Verify 對 `resolved_pending` gap 做兩階段驗證；答案附 coverage level
- **lint@v1** (2026-04-07)：初版
- **lint@v2** (2026-04-07)：新增 I. Conflict 追蹤

## 來源權威階層（Source Authority Ranking）

衝突發生時，LLM 依此階層暫定主呈現；但**各級說法都保留**，不刪除：

| Level | 來源 glob | 說明 |
|---|---|---|
| L1 | `raw/<your-architecture>/ARCHITECTURE.md` | 跨系統權威 |
| L2 | `raw/<your-architecture>/*README*`、`raw/drawio/*` | 專案或結構化權威 |
| L3 | `raw/<your-notes>/*`、`raw/isms/*` | 個人筆記或流程文件 |

---

## ingest@v4

```
你在對 {{PRODUCT_NAME}}-wiki 執行 ingest。把一份 raw 檔轉為結構化 wiki 頁面集合，並同步 Coverage State / Gap。

## 必讀
1. CLAUDE.md（本檔）— 架構、規範、權威階層、Coverage/Gap 章節
2. wiki/index.md — 避免重複創建
3. wiki/coverage/coverage-state-spec.md — Coverage State 規格（wiki 端 metadata）
4. raw/coverage-gaps/gap-source-spec.md — Gap 事實來源規格（raw 端，唯一來源）
5. wiki/_templates/<type>.md — 對應模板

## 輸入
- RAW_FILE: <絕對路徑>
- MODE: commit | dry-run（dry-run 只產檔不更新 index/log/coverage）

## 步驟 1-7（內容寫入；與 v3 相同）

1. **讀** RAW_FILE。若超過 500 行：先讀目錄與前 100 行定位章節，再按需讀取；勿跳過任何章節
2. **分類** 內容涵蓋哪幾個 type（system/procedure/troubleshooting/tech-note/entity/concept）
3. **對齊既有**：Glob 檢查目標頁是否存在。存在則更新（不覆蓋既有內容），不存在則用模板新建
4. **處理依賴的 stub**：若頁面內用到 `[[systems/X]]` 但 X 不存在，建立 stub 頁（僅 front-matter + `> TODO: pending ingest`），等下次 ingest 補完
5. **寫 front-matter**：必備 title/type/system/tags/sources/generated_by/updated。`generated_by: ingest@v4`。`sources` 用相對路徑
6. **雙向連結**：新連結的兩端都要更新
7. 若 MODE=commit：更新 index.md、追加 log.md

## 步驟 8：Gap Lifecycle Sync（v4 新增）

> **核心原則**：依 CLAUDE.md 核心原則第 6 條「禁止直接寫入 wiki/」，gap 的事實來源在 `raw/coverage-gaps/`。**raw-only gaps 設計**：wiki 端只存 coverage metadata（**不鏡像 gap entry**）。8a/8b 寫 raw 端、8c 只同步 wiki 端的 metadata。

### 8a：Gap Promotion Scan — 收割 raw 端 candidate

**來源**：本次 ingest 觸及的 raw 檔，特別是 `raw/isms/{folder}/{folder}-分析.md` 的 `## 知識盲點` 段落。

對每個 `### gap-candidate-NNN` 區塊：
1. 決定目標 topic：
   - `topic_hint` 有值 → 直接用該 topic
   - `topic_hint` 留空 → 依 `aspect` + 影響系統判斷對應 category；wiki 端 stub topic 由本次 8c 建立（若不存在）
2. 產生正式 gap entry（`gap-{today}-{NNN}`，NNN 為當日序號 +1）：
   - `aspect`：直接複製
   - `status`：`open`
   - `severity`：直接複製
   - `created`：今天
   - `query_text`：填 candidate 的 `needed_for`（前綴「(由 ingest-isms 分析發現) 」）
   - `search_trail`：直接複製，前綴加 `INGEST_ISMS_DETECT:{folder}→discovered`
   - `resolved_by`：null
3. **寫入 `raw/coverage-gaps/{topic}.md`**（事實來源；不寫 wiki/coverage/topics/）：
   - 檔不存在 → 建檔，含 frontmatter（`topic` + `wiki_topic`）
   - 檔存在 → 末尾追加 entry

**不刪除**分析文件原段落（raw 不可變原則）。

### 8b：Gap Resolution Scan — 切換 raw 端 status

掃描 `raw/coverage-gaps/*.md` 中所有 `status: open` 的 gap（**包含本次 8a 剛寫入的**），判斷本次 ingest 是否覆蓋其 aspect：

1. 比對本次 ingest 觸及的 wiki 頁面與 gap 所屬 topic 的 `wiki_pages`（讀自 `wiki/coverage/topics/{topic}.md` frontmatter）
2. 若 ingest 寫入了 gap.aspect 描述的內容：
   - **改寫 `raw/coverage-gaps/{topic}.md` 中該 gap 的 status 為 `resolved_pending`**（不直接 `closed`）
   - `resolved_by` 記錄頁面路徑
   - **不變**的欄位：`created`、`severity`、`query_text`、`search_trail`

**為何不直接 closed？** 避免 LLM 主觀判斷誤關。下次實際 `/wiki-query` 觸到此 topic 時才驗證 → 答得出 → 切 `resolved` → 數次驗證後 `closed`。

### 8c：Coverage Metadata Sync — 維護 wiki 端 topic metadata

> **注意**：本設計採 raw-only gaps，**不鏡像 gap entry 到 wiki 端**。本步驟只維護 `wiki/coverage/topics/{topic}.md` 的 metadata（frontmatter + 已覆蓋面向 + pointer），不複製 raw 端的 gap 內容。

掃描 `raw/coverage-gaps/*.md`，對每個檔案：

1. 讀 frontmatter 取得 `topic` 與 `wiki_topic` 路徑
2. 若 wiki 端 `wiki/coverage/topics/{topic}.md` 不存在 → 建立 stub topic：
   - frontmatter：`coverage: none`、`wiki_pages: []`、`last_ingest: {today}`
   - body：`## 已覆蓋面向` 空段 + 一行 pointer `> **Gaps**：見 [\`raw/coverage-gaps/{topic}.md\`](../../../raw/coverage-gaps/{topic}.md)`
3. 若本次 ingest 觸及該 topic 對應的 wiki 頁：
   - 更新 frontmatter `wiki_pages`（補上新觸及的頁）
   - 更新 frontmatter `coverage` 等級（依 `wiki/coverage/coverage-state-spec.md` 的升降原則）
   - 更新 frontmatter `last_ingest: {today}`
   - 重寫 `## 已覆蓋面向` 段為從 wiki_pages 內容綜合的條列
4. **不修改 pointer 行**（固定格式、idempotent）

**MODE=dry-run**：跳過所有寫入，只回報「會收割的 candidate 清單 + 會切換的 gap 清單 + 會建/更新的 topic metadata 清單」。

## 品質守則
- **語言**：繁中為主，專有名詞保留原樣（英文縮寫、程式碼不翻譯）
- **不編造**：raw 沒寫的不寫。不確定寫 `> TODO: <問題>`
- **原樣保留**：程式碼、SQL、表結構、命令用 code fence 原樣引用，不改寫
- **細節留給 raw**：wiki 負責結構與導航；大段內容只引用不複製
- **寧少勿錯**：模糊處寧可不寫
- **as-of 標註**：若來源是 snapshot（含日期），在相關段落標註「(as of YYYY-MM-DD)」
- **Idempotency**：同一 raw 重跑必須產生相同結果。更新時先檢查是否已有相同內容

## 圖片感知
raw 中的 `![alt](/.attachments/xxx.png)` 是段落的視覺證據，必須在 wiki 頁的對應位置保留：

1. **保留錨點**：圖片必須跟著它在 raw 原文中所屬的段落或步驟出現，不得遷移到頁尾或刪除
2. **路徑改寫**：把 raw 的 `/.attachments/xxx.png`（Azure DevOps Wiki 慣例）改寫為從 wiki 頁出發的相對路徑，指向 raw 的實際儲存位置：
   - 例：`wiki/procedures/10F某 SOP 範例.md` 引用時寫成
     `![...](../../raw/<your-notes>/.attachments/image-xxx.png)`
   - 不複製圖檔，wiki 永遠引用 raw 作為單一來源
   - 若 raw 圖檔不存在（見 raw/.../MISSING.md），改寫為文字描述 + `> TODO: missing-image: <basename>`
3. **alt 文案**：若 raw 中 alt 是 `image.png` / `image` / 空白等無意義字串，依前後文生成簡短繁中描述（例：`![ERP 備倉商品序號錯誤畫面](...)`）。raw 中已有具描述性的 alt 則原樣保留
4. **不處理非圖片附件**：`.pdf`/`.docx` 等附件不進入 wiki 圖片流，必要時在文字中以連結形式提及

## 衝突處理（不覆蓋、不靜默）
當新資訊與既有 wiki 頁面矛盾：
1. **兩者都保留**，用以下格式標記：
   ```
   > ⚠️ CONFLICT
   > - [L1] raw/<your-architecture>/ARCHITECTURE.md (2026-04-07)：<說法 A>
   > - [L3] raw/<your-notes>/xxx.md：<說法 B>
   > 暫以 L1 為主呈現，待人類裁決。
   ```
2. 主呈現依**來源權威階層**（見 CLAUDE.md）選較高 Level
3. log.md 條目加 `CONFLICT: <頁面路徑>` 標籤供 lint 追蹤

## 頁面拆分準則
- 單頁超過 ~300 行或涵蓋 3+ 個獨立子主題 → 拆為主頁 + 子頁，用 [[...]] 連接
- 同一主題就是很長 → 不拆，但在頁首加目錄

## 自檢（產出後跑一次）
- [ ] front-matter 完整
- [ ] sources 路徑存在
- [ ] wikilinks 目標存在或為本次 stub
- [ ] 無編造；不確定皆為 TODO
- [ ] 衝突已用 CONFLICT 區塊標記
- [ ] MODE=commit 時 index.md 與 log.md 已更新
- [ ] Gap Lifecycle Sync（8a/8b/8c）已執行；raw/coverage-gaps/ 的每個 topic 在 wiki/coverage/topics/ 都有對應 metadata 檔（含 pointer 行）

## 輸出回報
- 新建頁面（路徑清單）
- 更新頁面（路徑清單）
- Stub 頁清單
- TODO 清單（問題摘要）
- CONFLICT 清單（頁面 + 衝突摘要）
- **Gap lifecycle 摘要**：
  - **promoted**：本次從 raw 端 gap-candidate 收割並寫入 `raw/coverage-gaps/` 的 gap 清單（含目標 topic）
  - **pending-resolved**：本次在 raw 端切為 resolved_pending 的 gap 清單
  - **still-open**：未被本次覆蓋的 open gap 統計
  - **metadata-synced**：本次由 8c 建/更新 metadata 的 wiki topic 清單
  - **topic coverage 升級**：升級的 topic 與升降級
- 自檢結果
```

---

## query@v2

```
你正在對 {{PRODUCT_NAME}}-wiki 執行 query 任務。目標：回答使用者問題、留下 search_trail、查不到時寫入 raw/coverage-gaps/。

## 上下文必讀
1. 讀 CLAUDE.md（本檔）— 含 Coverage State / Gap Lifecycle 章節
2. 讀 wiki/index.md 找入口
3. 讀 wiki/coverage/coverage-state-spec.md — Coverage State 規格（wiki 端 metadata）
4. 讀 raw/coverage-gaps/gap-source-spec.md — Gap 事實來源規格（raw 端，唯一來源）

## 輸入
- QUESTION: <使用者問題>

## 步驟

### Step 1a：從 index.md 找候選頁面
依問題關鍵字對應類別（Systems / Procedures / Troubleshooting / Tech Notes / Entities / Concepts），列出候選 wiki 頁。

### Step 1b：查 Coverage State
掃 `wiki/coverage/topics/`，找出與問題主題相關的 topic 檔。對每個命中：
1. 讀其 front-matter：`coverage` 等級、`wiki_pages` 清單
2. 把 `wiki_pages` 加入候選頁面（補強 Step 1a 可能漏掉的頁）
3. **讀對應的 `raw/coverage-gaps/{topic}.md`**（gap 唯一事實來源；wiki 端不存 gap entry）。若該檔存在：記下任何 `status: open` 或 `resolved_pending` 的 gap，其中 `aspect` 與本次問題相關的需特別留意（Step Verify 用）。若不存在：表示此 topic 目前無 gap

若無命中 topic：標記為「TOPIC_MISSING 候選」（Step Gap 處理）。

### Step 2：讀候選頁面 + 沿 wikilinks 擴展（最多 2 跳）

把每次讀取記入 search_trail：
- `INDEX_LOOKUP:Procedures→hit`（從 index.md 命中分類）
- `COVERAGE_LOOKUP:example-topic→partial`（從 coverage 命中 topic）
- `PAGE_READ:procedures/某流程.md→partial`
- `WIKILINK_FOLLOW:[[entities/某表]]→hit`

### Step 3a：判斷是否需回溯 raw
若 wiki 資訊不足或有疑義，讀對應頁面 front-matter 中的 `sources`，回到 raw 層補全。

把每次 raw 讀取記入 search_trail：
- `RAW_FALLBACK:raw/<your-notes>/xxx.md→hit`
- `RAW_FALLBACK:raw/.../某筆記.md→none`

### Step 3b：量化「資訊不足」

> **資訊不足** = 讀完所有候選 wiki 頁 + 1 跳 wikilink 後，對使用者問題的核心斷言仍**找不到出處**或**沒有對應段落**。

達到此條件即觸發 Step 3a 的 raw 回溯。raw 回溯後若仍無法回答 → 觸發 Step Gap。

### Step Gap：三種失敗分類

> **核心原則**：所有 gap 寫入都對 `raw/coverage-gaps/{topic}.md`，**絕不寫 `wiki/`**（含 `wiki/coverage/topics/`）。

| 等級 | 條件 | 動作 |
|------|------|------|
| `TOPIC_MISSING` | Step 1b 找不到任何相關 topic | 在 `raw/coverage-gaps/{topic}.md` 建立檔案（含 frontmatter `topic` + `wiki_topic`）並寫入一條 gap entry。**不在 wiki/coverage/topics/ 建 stub topic**——由下次 `/ingest` 處理該 raw 時建立對應的 wiki 端 stub topic |
| `DETAIL_MISSING` | topic 存在但缺特定 aspect | 開啟對應的 `raw/coverage-gaps/{topic}.md`（不存在則建檔），在末尾追加 gap entry |
| `RAW_ALSO_MISSING` | wiki + raw 都查過皆無 | 同 DETAIL_MISSING，但 `severity: high`；告知使用者「需要人類補資料」 |

每個 gap entry 必填：
```yaml
### gap-{YYYY-MM-DD}-{NNN}
- aspect: <一句話描述缺失內容>
- status: open
- severity: <low | medium | high>
- created: {today}
- query_text: "<使用者原問題>"
- search_trail: [INDEX_LOOKUP:...→..., COVERAGE_LOOKUP:...→..., PAGE_READ:...→..., RAW_FALLBACK:...→...]
- resolved_by: null
```

### Step Verify：驗證 resolved_pending

若 Step 1b 命中的 topic 有對應的 `raw/coverage-gaps/{topic}.md`，其中含 `status: resolved_pending` 的 gap，且其 aspect 與本次問題相關：

1. 完成 Step 1–3 後，**評估**本次是否成功回答了該 gap 的 query_text 涵蓋範圍
2. 若答得出 → 改 `raw/coverage-gaps/{topic}.md` 中該 gap 的 status 為 `resolved`；連續 N 次（建議 N=2）後改為 `closed`
3. 若答不出 → 改 status 回 `open`，severity 升級（low→medium、medium→high），並追加 search_trail

**所有切換都對 raw 端**；wiki 端只有 metadata（coverage level / last_ingest），不存 gap entry，無同步問題。

### Step 4：合成答案
合成答案，並在引用旁附上 **coverage level**：
```markdown
根據 [[procedures/某流程]]（coverage: partial），...

> ⚠️ 本主題覆蓋深度為 `partial`，部分細節可能尚未沉澱。
```

每個關鍵斷言都要指回 wiki 頁面或 raw 檔。**承認無知**：wiki + raw 都找不到時，明確說「目前 wiki 沒有這個資訊，需要人類補充」，並告知已建立 gap entry。

### Step 5：判斷是否需要沉澱
若在解題過程中產生了新的連結、修正了某個頁面的錯誤、或發現了一個值得獨立成頁的概念/實體：

1. **不直接寫 wiki**。先在 `raw/` 對應位置建快照
2. 由人類或下次 `/ingest` 把 raw 編譯入 wiki

> **本 prompt 完全不寫 `wiki/`**（含 `wiki/log.md`、`wiki/coverage/topics/`、其他編譯產物）。所有產出（gap entry、status 切換、沉澱）都寫到 `raw/`，由下次 `/ingest` 編譯入 wiki。

## 品質守則
- **答案必須有出處**：每個關鍵斷言都要指回 wiki 頁面或 raw 檔
- **承認無知**：wiki + raw 都找不到答案時，明確說「目前 wiki 沒有這個資訊，需要人類補充」，**不要猜**
- **raw 為準**：wiki 與 raw 衝突時以 raw 為準；衝突須建議使用者下次 ingest 修正 wiki
- **search_trail 必須結構化**：`[STEP_TYPE:target→result]` 格式，避免文字描述
- **絕不寫 wiki/**：所有產出寫 `raw/`，由 `/ingest` 編譯

## 輸出
- 答案（含出處引用 + coverage level 標註）
- search_trail（結構化陣列）
- 若有沉澱：新建/更新的 raw 檔清單
- 若觸發 gap：新建/追加的 raw/coverage-gaps/ entry 清單（含 topic id 與 gap id）
```

---

## lint@v1

```
你正在對 {{PRODUCT_NAME}}-wiki 執行 lint 任務。目標：產出健康檢查報告。

## 上下文必讀
1. 讀 CLAUDE.md（本檔）

## 檢查項目

### A. Front-matter 完整性
對 wiki/ 下每個 .md 檔（排除 _templates/、index.md、log.md）：
- [ ] 有 front-matter 區塊
- [ ] title / type / sources / updated 必備欄位齊全
- [ ] type 是允許的 6 種之一
- [ ] generated_by 欄位存在

### B. Sources 有效性
- [ ] 每個 source 路徑都對應實際存在的檔案
- [ ] 報告：broken sources 清單

### C. Wikilink 有效性
- [ ] 每個 [[...]] 的目標頁面存在
- [ ] 報告：broken wikilinks 清單（檔案:行號 → 目標）

### D. 孤立頁面
- [ ] 找出未被 index.md 或其他頁面引用的 .md 檔
- [ ] 排除：index.md / log.md / CLAUDE.md / _templates/*

### E. 反向連結一致性
- [ ] 若 A 的「相關頁面」列了 B，B 也該列 A
- [ ] 報告：單向連結清單（非錯誤，僅提示）

### F. Raw 覆蓋率
- [ ] 找出 raw/ 下未被任何 wiki 頁面 sources 引用的檔案
- [ ] 報告：未 ingest 的 raw 清單

### G. 過時頁面
- [ ] updated 超過 90 天未動的頁面

### H. TODO 追蹤
- [ ] 所有 wiki 頁面中含 `TODO:` 的段落
- [ ] 報告：TODO 清單（頁面:行號 → 內容）

### I. CONFLICT 追蹤
- [ ] 所有 wiki 頁面中含 `⚠️ CONFLICT` 區塊
- [ ] 所有 log.md 中含 `CONFLICT:` 標籤但尚未解決的條目
- [ ] 報告：衝突清單（頁面 → 涉及的來源 + Level）
- [ ] 嚴重度：🟡 WARNING

## 輸出
一份 markdown 報告，分 A-H 章節。每個問題註明嚴重度：
- 🔴 CRITICAL（broken sources/wikilinks、front-matter 缺失）
- 🟡 WARNING（孤立頁、未 ingest raw、過時）
- 🔵 INFO（單向連結、TODO）

報告寫入 wiki/lint-report-YYYY-MM-DD.md，並追加 log.md 記錄。

> 註：實務上 lint 由 `scripts/lint.ps1` 執行，本 prompt 是 LLM 模式的備援。
```

---

# Pilot Ingest 協定

**首次 ingest 與任何 prompt 版本升級後的首次 ingest**，必須走 pilot 流程：

1. 選 **1 個代表性 raw 檔**（優先 ARCHITECTURE.md，因為它結構化且會被大量交叉引用）
2. 執行 ingest@vN，但**只產出、不提交 index/log**
3. 人類審查產出頁面與 TODO 清單
4. 依回饋修正 prompt → bump 版本 → 再跑一次
5. 審查通過後，才正式寫入並更新 index/log，記錄「pilot 通過，prompt@vN 正式生效」
6. 之後才能進入批次 ingest 其他 raw 檔

---

## 回覆慣例

每次執行任務結束後，回覆末尾加上「喵~」。
