---
name: ingest
description: 自動掃描 raw/ 下尚未進入 wiki 的 markdown 檔，依照 ingest@v4（Karpathy LLM Wiki 方法）寫入 wiki 頁面，並同步 Coverage State / Gap 生命週期。使用時機：說「ingest 未處理的 raw」、「更新 wiki」、或明確呼叫 /ingest。
---

# ingest — 將未處理的 raw 檔寫入 wiki 知識庫

## 用途

自動掃描 `raw/` 下所有子資料夾中的 `.md` 檔，比對 `wiki/log.md` 找出尚未 ingest 的檔案，依照 `ingest@v4` 規範逐一寫入 wiki，並同步 `raw/coverage-gaps/` 與 `wiki/coverage/topics/` 的 gap 狀態。

**這是兩步驟流程的第二步**：

```
步驟 1（前處理）                         步驟 2（本 skill）
────────────────────────────             ──────────────────
/ingest-isms  → raw/isms/{feature}/*.md  →  /ingest → wiki/
/ingest-drawio → raw/drawio/{proj}/*.md  →  /ingest → wiki/
直接放入 raw/ 的 .md 檔                  →  /ingest → wiki/
```

## 輸入

無需參數。直接執行 `/ingest` 即可。

- `MODE`（選填，預設 `commit`）：
  - `commit` — 完整執行，更新 wiki 頁面、`index.md`、`log.md`、`coverage/topics/`
  - `dry-run` — 只產出 wiki 頁面草稿，不更新 index/log/coverage

## 執行步驟

### Step 0：找出待 ingest 的 raw 檔

**方法：比對 log.md 記錄**

讀取 `wiki/log.md`，從中找出所有 `inputs:` 欄位記錄過的 raw 檔路徑，建立「已處理清單」。

接著掃描以下目錄的 `.md` 檔（排除各目錄自身的 `README.md`）：
- `raw/isms/*/`（子資料夾內的 MD，即 `/ingest-isms` 產出的結構化文件）
- `raw/drawio/*/`（子資料夾內的 MD，即 `/ingest-drawio` 產出的 Mermaid 文件）
- `raw/daily/**/*.md`（每日工作紀錄，**選擇性 ingest**，見下方規則）
- `raw/**/*.md`（其他 raw 子目錄；請依產品實際 raw 結構於本清單新增項目）

比對後，不在「已處理清單」中的檔案 = **待 ingest 清單**。

#### `raw/coverage-gaps/*.md` 不適用「待 ingest 清單」

`raw/coverage-gaps/{topic}.md` 是 gap 的事實來源，**每次 ingest 都要重新同步**（事實可能變動），不適用「處理一次後永久略過」的機制。**統一由 Step 8b/8c 處理**，不進待 ingest 清單。

#### `raw/daily/` 選擇性 ingest 規則

每日工作紀錄（`/daily-log` 產出）包含多筆條目，大部分是流水帳，但部分條目含有值得沉澱到 wiki 的系統知識。

**處理方式**：逐筆掃描條目，只擷取與系統知識有關的內容，用來**更新既有 wiki 頁面**或**新建頁面**。

**值得擷取的條目**（符合任一即可）：
- bug fix 的根因分析與解法（→ troubleshooting）
- 發現的系統行為、隱含邏輯、欄位對應關係（→ tech-note / entity）
- 操作流程的新步驟或注意事項（→ procedure）
- 經驗/教訓中提到的 pattern 或 gotcha（→ 更新既有相關頁面）

**應跳過的條目**：
- 純 config 變更（如「merge into main」、「註解掉按鈕」）且無經驗教訓
- 知識庫更新本身（如「新建 wiki 頁面」）— 已經在 wiki 裡了
- 沒有技術深度的摘要（如「產出 DOCX」）

**輸出**：不為 daily log 單獨建 wiki 頁，而是將擷取的知識**合併進既有相關頁面**。若無對應頁面且內容值得獨立成頁，才新建。

若待 ingest 清單為空，跳到 Step 8（仍要執行 Gap Lifecycle Sync）。

若有多個待處理檔案，逐一執行 Step 1–7，最後彙總後跑 Step 8。

### Step 1：載入規範

讀取以下檔案：
1. `CLAUDE.md` — 找到 `## ingest@v4` 區塊，完整閱讀作為執行規範；同時讀「Coverage State 與 Gap Lifecycle」章節
2. `wiki/index.md` — 確認既有頁面，避免重複建立
3. `wiki/coverage/coverage-state-spec.md` — Coverage State 規格（wiki 端 metadata）
4. `raw/coverage-gaps/gap-source-spec.md` — Gap 事實來源規格（raw 端，唯一來源）
5. `wiki/coverage/topics/`（若存在）— 找出本次 ingest 可能對應的 topic

### Step 2-7：執行 ingest@v4 步驟 1-7

嚴格依照 CLAUDE.md 中 `ingest@v4` prompt 定義的流程執行：

1. **讀** RAW_FILE（超過 500 行時先讀目錄與前 100 行，再按需讀取）
2. **分類**內容涵蓋的 type（system / procedure / troubleshooting / tech-note / entity / concept）
3. **對齊既有**：Glob 檢查目標頁是否存在，存在則更新，不存在則用模板新建
4. **處理依賴的 stub**：引用到的 `[[X]]` 若不存在，建立 stub 頁
5. **寫入 front-matter**（`generated_by: ingest@v4`，`sources` 用相對路徑）
6. **建立雙向 wikilink**
7. 若 MODE=commit：更新 index.md、追加 log.md（**`inputs:` 欄位必須寫入 raw 檔相對路徑**，供下次比對）

### Step 8：Gap Lifecycle Sync

本步驟做三件事：(8a) 收割 raw 端 gap-candidate 寫入 `raw/coverage-gaps/`；(8b) 切換覆蓋的 gap 為 resolved_pending（改寫 `raw/coverage-gaps/`）；(8c) Coverage Metadata Sync — 維護 `wiki/coverage/topics/{topic}.md` 的 metadata（frontmatter + 已覆蓋面向 + pointer）。

> **核心原則**：依 CLAUDE.md 核心原則第 6 條「禁止直接寫入 wiki/」，gap 的事實來源在 `raw/coverage-gaps/`。**raw-only gaps 設計**：wiki 端只存 coverage metadata（**不鏡像 gap entry**）。8a/8b 寫 raw 端、8c 只同步 wiki 端的 metadata。

#### Step 8a：Gap Promotion Scan — 收割 raw 端 candidate

**來源**：本次 ingest 觸及的 raw 檔，特別是 `raw/isms/{folder}/{folder}-分析.md` 的 `## 知識盲點` 段落。

**動作**：

1. 讀分析文件 `## 知識盲點` 段落
2. 對每個 `### gap-candidate-NNN` 區塊，執行下列轉換：
   - 決定目標 topic：
     - `topic_hint` 有值 → 直接用該 topic
     - `topic_hint` 留空 → 依 `aspect` + 影響系統判斷對應 category；wiki 端 stub topic 由本次 8c 建立（若不存在）
   - 產生正式 gap entry，必填欄位：
     - `aspect`：直接複製
     - `status`：`open`
     - `severity`：直接複製
     - `created`：今天
     - `query_text`：填 candidate 的 `needed_for`（前綴「(由 ingest-isms 分析發現) 」）
     - `search_trail`：直接複製，前綴加 `INGEST_ISMS_DETECT:{folder}→discovered`
     - `resolved_by`：null
   - **寫入 `raw/coverage-gaps/{topic}.md`**（事實來源；不寫 wiki/coverage/topics/）：
     - 檔不存在 → 建檔，含 frontmatter（`topic` + `wiki_topic`）
     - 檔存在 → 末尾追加 entry
     - gap id 為 `gap-{today}-{NNN}`（NNN 為當日序號 +1，讀 `raw/coverage-gaps/{topic}.md` 既有 gap 找最大值）

3. **不刪除**分析文件原段落（raw 不可變原則），但日後 lint 可比對「已收割 vs 仍存在」。

**MODE=dry-run**：印出「將收割 N 條 gap-candidate，目標 topic 清單」，不寫檔。

#### Step 8b：Gap Resolution Scan — 切換 raw 端 status

掃描 `raw/coverage-gaps/*.md` 中所有 `status: open` 的 gap（**包含本次 8a 剛寫入的**），判斷本次 ingest 是否覆蓋其 aspect：

對每個 open gap：

1. 比對本次 ingest 觸及的 wiki 頁面與 gap 所屬 topic 的 `wiki_pages`（讀自 `wiki/coverage/topics/{topic}.md` frontmatter）
2. 若 ingest 寫入了 gap.aspect 描述的內容：
   - **改寫 `raw/coverage-gaps/{topic}.md` 中該 gap 的 status 為 `resolved_pending`**（不直接 `closed`）
   - `resolved_by` 記錄頁面路徑
   - **不變**的欄位：`created`、`severity`、`query_text`、`search_trail`
3. 若該 topic 的 `coverage` 等級因本次 ingest 提升（如 `partial → comprehensive`），由 8c 更新 wiki 端 topic frontmatter 的 `coverage` 與 `last_ingest`

**為何不直接 closed？** 避免 LLM 主觀判斷誤關。下次實際 `/wiki-query` 觸到此 topic 時才驗證 → 答得出 → 切 `resolved` → 數次驗證後 `closed`。

> **特例**：剛在 Step 8a 寫入的 gap，本次 ingest 多半就是它的「對應 raw」——很容易自我滿足。準則是：**只有當 ingest 寫入的 wiki 頁面內容明確覆蓋 aspect 時才切 resolved_pending**，純粹 candidate 來源 raw 被 ingest 不算。

#### Step 8c：Coverage Metadata Sync — 維護 wiki 端 topic metadata

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

#### 摘要追加 log.md

本次 ingest 條目末尾加一行：
```
- Gap lifecycle: 3 promoted to raw/coverage-gaps, 2 pending-resolved (gap-2026-05-13-001, gap-2026-05-10-003), 5 still open, 12 topics metadata-synced
```

若 MODE=dry-run：跳過所有寫入，只回報「會收割的 candidate 清單 + 會切換的 gap 清單 + 會編譯的 topic 清單」。

### Step 9：自檢

每個檔案完成後執行：
- [ ] front-matter 完整（title / type / system / tags / sources / generated_by / updated）
- [ ] sources 路徑實際存在
- [ ] wikilinks 目標存在或為本次 stub
- [ ] 無編造；不確定皆標為 TODO
- [ ] 衝突已用 CONFLICT 區塊標記
- [ ] MODE=commit 時 index.md 與 log.md 已更新（含 inputs 路徑）
- [ ] Gap Lifecycle Sync（8a/8b/8c）已執行；raw/coverage-gaps/ 的每個 topic 在 wiki/coverage/topics/ 都有對應 metadata 檔（含 pointer 行）

### Step 10：輸出回報

所有檔案處理完後，統一回報：
- 處理檔案數
- 新建 wiki 頁面（路徑清單）
- 更新 wiki 頁面（路徑清單）
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

## 使用範例

```
# 掃描所有未處理的 raw 檔並 ingest
/ingest

# dry-run 預覽（不更新 index/log/coverage）
/ingest MODE=dry-run

# 自然語言觸發
更新 wiki
把還沒進 wiki 的 raw 都 ingest
```

## 注意事項

- `.drawio` 原始檔請先用 `/ingest-drawio`；PDF/DOCX 變更單請先用 `/ingest-isms`
- ISMS 文件經本 skill 後，wiki 不寫 ISMS 編號或需求背景，但**功能描述本身必須寫**：
  - 已上線部分 → 直接寫入 wiki 系統頁
  - 未上線部分 → 寫入並標 `> 計畫中（as of YYYY-MM-DD）`，上線後由下次 ingest 移除標記
- log.md 是追蹤機制的唯一依據；若 log.md 損壞，可用 `dry-run` 確認重跑範圍
- 任何 prompt/skill 版本升級後，首次 ingest 必須走 CLAUDE.md「Pilot Ingest 協定」

## 版本

- **v2.0** (2026-05-13)：升級 ingest@v3 → ingest@v4。新增 Step 8 Gap Lifecycle Sync（8a 收割 candidate、8b 切 resolved_pending、8c Coverage Metadata Sync — raw-only gaps 設計，wiki 端只存 metadata + pointer，不鏡像 gap entry）。Step 0 補充 `raw/coverage-gaps/` 不適用待 ingest 清單機制。Step 1 補充讀 coverage-state-spec.md 與 gap-source-spec.md
- v1.1 (2026-04-15)：新增 `raw/daily/` 選擇性 ingest 規則 — 掃描每日工作紀錄，只擷取與系統知識相關的條目合併進 wiki
- v1.0 (2026-04-09)：初版，自動掃描模式，以 log.md inputs 追蹤已處理清單
