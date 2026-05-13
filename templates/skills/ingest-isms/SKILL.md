---
name: ingest-isms
description: 自動掃描 raw/isms/ 下的子資料夾，將資料夾內所有來源檔（PDF/DOCX/PNG/JPG/XLSX/XLS/TXT）整合為結構化 markdown、分析文件，並透過 spec-by-example skill 產出測試規格文件（Given/When/Then + 測試骨架對應）。支援重跑——新增來源後再次執行即可合併更新。使用時機：說「ingest isms」、「處理 isms 變更單」、或明確呼叫 /ingest-isms。
---

# ingest-isms — ISMS 變更單多來源整合 Skill

## 用途
掃描 `raw/isms/` 下的**子資料夾**，將每個資料夾內的所有來源檔整合為一份結構化 markdown + 一份分析文件。

**支援來源格式**：`.pdf`、`.docx`、`.png`、`.jpg`、`.xls`、`.xlsx`、`.txt`

**可重跑**：即使資料夾內已有產出的結構化 `.md`，執行時會重新讀取所有來源，重新產出（覆寫既有 .md）。這樣新增來源後只需再跑一次即可。

## 核心原則
1. **準確 > 快速**：不編造、不推測；找不到的欄位明確標示「未填寫」
2. **多來源合併**：所有來源檔都要讀取，合併為一份完整的結構化文件
3. **來源矛盾時標記**：不同檔案說法不一致時，以截圖/PDF 為準，但兩者都保留並標記
4. **沿用 wiki 命名規範**：資料夾名用 `ISMS-{民國年月}-{主題簡述}`
5. **追加 raw 端 log**：每次 ingest 後必須追加 `raw/isms/log.md`（**不得寫入 `wiki/log.md`**）
6. **raw 與 wiki 階段分離**：本 skill 只處理 raw 端（raw/isms/ 內的檔案），**嚴禁觸碰 `wiki/` 下任何檔案，包含 `wiki/log.md`**。wiki 寫入階段由 `/ingest` 負責，`wiki/log.md` 是 `/ingest` 的已處理清單追蹤依據，若 raw 階段誤寫會造成 `/ingest` 判定檔案「已 ingest」而跳過，導致 wiki 無法更新

## 輸入
無需參數。直接執行 `/ingest-isms` 即可掃描所有子資料夾。

- 也可指定單一資料夾名稱：`/ingest-isms "ISMS-114-08-退費不跳停機"`（自動加上 `raw/isms/` 前綴）
- `MODE`（選填，預設 `commit`）：
  - `commit` — 完整流程（寫檔 + 追加 `raw/isms/log.md`）
  - `dry-run` — 只產出 markdown，不追加 log

## 前置工具檢查
執行前確認以下工具可用：
```bash
# Python + markitdown
python -m markitdown --version  # 應為 0.1.5+

# 若有 PDF，還需 PyMuPDF
python -c "import pymupdf; print(pymupdf.__version__)"
```

## 執行步驟

### Step 0: 掃描待處理資料夾
```bash
ISMS_ROOT="raw/isms"

# 列出所有子資料夾（排除隱藏資料夾）
ls -d "$ISMS_ROOT"/*/
```

判斷邏輯：
- 若指定了資料夾名稱（如 `ISMS-114-08-退費不跳停機`），自動補上 `$ISMS_ROOT/` 前綴，只處理該資料夾
- 若未指定，掃描所有子資料夾，逐一處理
- 空資料夾或只含 `.md` 檔的資料夾跳過（沒有新來源可處理）
- **已有結構化 .md 的資料夾仍會處理**（重跑模式）

### Step 1: 盤點資料夾內所有來源檔
```bash
FEATURE_DIR="$ISMS_ROOT/{folder_name}"

# 列出所有來源檔（排除本 skill 產出的 .md）
ls "$FEATURE_DIR" | grep -E '\.(pdf|docx|png|jpg|jpeg|xls|xlsx|txt)$'
```

將來源檔依類型分組：
| 類型 | 副檔名 | 處理方式 |
|---|---|---|
| PDF | `.pdf` | markitdown 抽文字 + PyMuPDF 渲染每頁 PNG → vision 讀取 |
| DOCX | `.docx` | markitdown 抽文字 |
| 圖片 | `.png` `.jpg` `.jpeg` | 直接用 Read 工具 vision 讀取 |
| Excel | `.xls` `.xlsx` | markitdown 轉為 markdown 表格 + **獨立產出 .md 檔** |
| 純文字 | `.txt` | 直接讀取內容 |

### Step 2: 依類型逐一讀取來源

#### 2a. PDF 處理
```bash
PAGES_DIR="/tmp/isms-pages-$(date +%s)"
mkdir -p "$PAGES_DIR"
# 用 render-pdf.py 渲染每頁
"$PY" .claude/skills/ingest-isms/scripts/render-pdf.py "$PDF_FILE" "$PAGES_DIR" 200
```
1. 先用 markitdown 抽文字層，取得結構骨幹
2. 再用 Read 工具讀取每頁 PNG（vision），擷取：
   - UI 截圖內的欄位與資料
   - SQL 範例（完整轉錄，不可漏字）
   - Backlog 列表（編號 + 標題）
   - Release Notes 表格
   - 簽名欄的姓名與時間戳

#### 2b. DOCX 處理
```bash
TEMP_MD="/tmp/isms-docx-$(date +%s).md"
"$PY" -m markitdown "$DOCX_FILE" -o "$TEMP_MD"
```
讀取轉換後的 markdown，抽取結構化欄位。

#### 2c. 圖片處理（PNG/JPG）
直接用 `Read` 工具讀取圖片，以 vision 模式辨識內容：
- 截圖中的 UI 欄位、表格、SQL
- 手寫或列印的補充說明
- 測試佐證截圖

每張圖片在產出中標註來源檔名。

#### 2d. Excel 處理（XLS/XLSX）
```bash
# 轉換為獨立 .md 檔（存放在同資料夾內）
EXCEL_MD="${EXCEL_FILE%.*}.md"
"$PY" -m markitdown "$EXCEL_FILE" -o "$EXCEL_MD"
```
1. 用 markitdown 將 xls/xlsx 轉為 markdown 表格
2. **產出獨立的 .md 檔**，存放在同資料夾內（檔名同原始檔，副檔名改為 `.md`）
3. 讀取轉換後的 markdown 表格，整合進結構化文件

#### 2e. 純文字處理（TXT）
直接用 `Read` 工具讀取，將內容納入對應段落。

### Step 3: 合併所有來源
以 PDF/DOCX 的 ISMS 表單為**主骨幹**（若有多份取最完整的），其他來源為補充：

1. **主骨幹**：從 PDF/DOCX 抽取的 ISMS 表單結構（三大段：申請/評估/驗收）
2. **圖片補充**：截圖內容填入對應段落（如 SQL 範例、UI 畫面、測試佐證）
3. **Excel 補充**：表格資料填入對應區塊（如 Backlog 列表、Release Notes）
4. **TXT 補充**：文字說明填入對應段落或作為附註

**矛盾處理**：
- 不同來源說法不一致時，用以下格式標記：
  ```
  > ⚠️ 來源差異
  > - {來源A檔名}：{說法 A}
  > - {來源B檔名}：{說法 B}
  > 暫以截圖/PDF 為準。
  ```
- markitdown 文字與截圖 vision 矛盾時，**以截圖為準**（markitdown 偶有 layout 錯亂）

### Step 4: 決定檔名（僅新建時）
若資料夾已有命名（如 `ISMS-114-08-退費不跳停機`），沿用。
若為新建，從文件欄位推導：
- **民國年月**：從「申請日期」欄位取年月
- **主題簡述**：從「項目」或「申請變更項目」取標題，去贅詞，空格換 `-`

### Step 5: 填入模板
使用 `templates/isms-case-template.md` 作為骨架，填入合併後的結果。

檔頭註記需列出**所有來源檔**：
```markdown
> snapshot: {YYYY-MM-DD}
> sources:
>   - {來源檔1}
>   - {來源檔2}
>   - ...
> converted_by: ingest-isms v2.0 (multi-source)
> form_template: ISMS-L4-69 {TEMPLATE_VERSION}
```

必須包含：
1. **檔頭註記**（snapshot + 所有 sources + converted_by + form_template）
2. **基本資料表**
3. **原始三大段**（申請 / 開發評估 / 驗收）每段完整複製
4. **新增區段**：
   - 「具體 SQL 範例」（若有）從截圖完整轉錄
   - 「UI 畫面」（若有）轉成表格
   - 「Backlog 樹」（若有）用樹狀結構
   - 「Release Notes 對應」（若有）完整列出
   - 「流程時間線」從簽名時間戳整理
5. **來源清單**：列出本次使用的所有來源檔及其貢獻的段落

### Step 6: 寫入結構化 markdown

```bash
DEST="$FEATURE_DIR/${FOLDER_NAME}.md"
# 寫入 DEST（覆寫既有）
```

若為重跑，覆寫既有的結構化 .md。

### Step 7: 產出修改建議與執行計畫（寫入 `{FOLDER_NAME}-分析.md`）

讀取以下 wiki 頁面，與 ISMS 需求交叉比對，產出分析文件：
1. `wiki/index.md` — 找出相關系統與概念頁
2. 沿 wikilinks 讀取相關頁面（最多 2 跳）

分析文件結構如下，**寫入 `{FEATURE_DIR}/{FOLDER_NAME}-分析.md`**：

```markdown
# {ISMS標題} — 修改建議與執行計畫

> generated: {YYYY-MM-DD}
> sources:
>   - {結構化MD路徑}
>   - {各來源檔路徑}
> generated_by: ingest-isms v2.0

## 需求摘要
{1-2 句話說明本次變更目的}

## 來源檔摘要
| 檔案 | 類型 | 貢獻內容 |
|---|---|---|
| {檔名} | PDF | ISMS 表單主體 |
| {檔名} | PNG | SQL 範例截圖 |
| ... | ... | ... |

## 影響系統

列出受影響的系統，每個系統說明影響範圍：
- [[systems/XXX]] — {影響說明}

## 修改建議

依系統分段，每個修改點說明：
- 為什麼要改（對應 ISMS 哪個需求）
- 建議的實作方向
- 注意事項或限制

### {系統名稱}
1. **{修改點}**
   - 需求來源：{ISMS 原文段落}
   - 建議：{具體修改方向}
   - 注意：{風險或依賴}

## 執行計畫

### 後端（RD）
- [ ] {工作項目}

### 前端
- [ ] {工作項目}

### DB
- [ ] {工作項目}

### MIS 介接
- [ ] {工作項目}

### 測試
- [ ] {依 ISMS 所需測試類型}

## 潛在風險
- {風險描述} — 參考 [[...]]

## 待釐清事項
1. {問題}
```

**品質要求**：
- 修改建議必須對應到 ISMS 的具體需求，不能泛泛而談
- 執行計畫的工作項目要具體到可以直接建立 ticket 的程度
- 若 wiki 中找不到對應頁面，在潛在風險中標注「wiki 尚無此系統頁，建議先 ingest 相關文件」
- DB 欄位命名若能從 wiki 推斷，給出建議名稱；若不確定，標 `> TODO: 命名待確認`

### Step 8: 呼叫 spec-by-example 產出測試規格文件

> **目的**：將 ISMS 需求轉成可驗證的 Given/When/Then 具體例子，作為開發驗收與測試依據。

**觸發時機**：Step 7 產出分析文件後、寫入 log 之前。

**執行方式**：使用 `Skill` 工具呼叫 `spec-by-example`（簡稱 SBE），將以下資訊作為需求描述傳入：

```
需求來源：ISMS {資料夾名}
ISMS 分析文件：{FEATURE_DIR}/{FOLDER_NAME}-分析.md
結構化需求：{FEATURE_DIR}/{FOLDER_NAME}.md
本次變更摘要：{從 Step 7 分析文件抽出的 1-2 句需求摘要}
影響系統：{從 Step 7 分析文件抽出的影響系統清單}
```

呼叫範例：
```
Skill(skill="spec-by-example",
      args="根據 raw/isms/{FOLDER_NAME}/{FOLDER_NAME}-分析.md 產出測試規格")
```

**SBE 流程要求**：
1. SBE 會依序執行 Step 1（需求解析）→ Step 2（假設審計 + Wiki 交叉比對）→ Step 3（Example Mapping）
2. **Step 4 人類確認 Gate 不可跳過** — 必須等使用者確認 Given/When/Then 例子後才繼續
3. 使用者確認後，由 SBE 完成 Step 5（spec 持久化）與 Step 6（測試骨架生成）

**測試文件落位（重要）**：
SBE 預設寫入 `specs/sbe/YYYY-MM-DD-{feature-name}.md`，但在本 skill 呼叫情境下，**額外**在 ISMS 資料夾內建立對應檔：

```
{FEATURE_DIR}/{FOLDER_NAME}-測試規格.md
```

內容需包含：
- 檔頭註記：
  ```markdown
  > generated: {YYYY-MM-DD}
  > source_isms: raw/isms/{FOLDER_NAME}/{FOLDER_NAME}.md
  > source_analysis: raw/isms/{FOLDER_NAME}/{FOLDER_NAME}-分析.md
  > sbe_spec: specs/sbe/YYYY-MM-DD-{feature-name}.md
  > generated_by: ingest-isms v2.2 → spec-by-example
  ```
- **假設審計表**（完整複製 SBE Step 2-A 產出）
- **系統邊界地圖**（完整複製 SBE Step 2-B 產出）
- **Example Mapping 全部例子**（Happy Path / Edge Cases / Error Paths / Contract Sketch）
- **使用者確認結果**（是否確認 / 修改項目 / 新增例子）
- **測試骨架對應表**：每個例子對應到哪個測試類型（單元 / 整合 / E2E）

**異常處理**：
- 若 SBE 假設審計出現 ❌（假設與 wiki 矛盾）：
  - 立即停止 Step 8，**不覆寫** `{FOLDER_NAME}-測試規格.md`
  - 在分析文件 `{FOLDER_NAME}-分析.md` 的「待釐清事項」追加一條：
    > `SBE 假設審計失敗：{假設內容} 與 {wiki 頁面} 矛盾，需釐清後重跑`
  - 直接跳至 Step 9，log 標註 `sbe_status: blocked`

- 若使用者在 SBE Step 4 回覆「修改」：
  - 依 SBE 的 Revision Gate 流程修訂
  - 直到使用者確認為止，才寫入 `{FOLDER_NAME}-測試規格.md`

**MODE=dry-run 時**：仍然執行 SBE 流程、產出測試規格文件，但不寫入 log。

### Step 9: 追加 `raw/isms/log.md`（MODE=commit 時）

⚠️ **寫入目標是 `raw/isms/log.md`，絕對不是 `wiki/log.md`。**
`wiki/log.md` 由 `/ingest`（raw→wiki 階段）獨佔維護，本 skill 若寫入會污染 `/ingest` 的已處理清單判斷。

若 `raw/isms/log.md` 不存在，首次寫入時建立（檔頭加一行說明：`> raw 端 ingest-isms 紀錄；wiki 寫入紀錄在 wiki/log.md`）。

```markdown
## {YYYY-MM-DD} ingest-isms — {資料夾名}
- skill: ingest-isms v2.3
- operator: claude-opus-4-7[1m]
- inputs:
  - {來源檔1}
  - {來源檔2}
  - ...
- 產出: raw/isms/{資料夾名}/{檔名}.md
- 分析: raw/isms/{資料夾名}/{檔名}-分析.md
- 測試規格: raw/isms/{資料夾名}/{檔名}-測試規格.md
- sbe_spec: specs/sbe/YYYY-MM-DD-{feature-name}.md
- sbe_status: {confirmed | revised | blocked}
- 模式: {新建 | 重跑}
- 變更等級: {level}
- 自檢: 欄位完整 ✓, 來源全數讀取 ✓, SBE 確認 ✓
- 備註: 共 {N} 個來源檔，待 /ingest 寫入 wiki
```

### Step 10: 產出變更範圍分析（回覆使用者）
最後在回應中附上**變更範圍分析報告**（不寫進 wiki，作為對使用者的回覆）：

1. **需求摘要**：1-2 句話
2. **來源檔統計**：各類型檔案數量
3. **wiki 知識交叉比對**：列出相關的既有 wiki 頁
4. **影響系統**：依 wiki 的 systems / code_structure 判斷
5. **工作項目拆解**：後端 / 前端 / DB / 測試分類
6. **潛在風險**：從 wiki 找出未在變更單提及但相關的點
7. **命名規範檢查**：若含 DB 欄位新增，比對 `[[tech-notes/db-命名與設計規範]]`
8. **待釐清事項**：列出需要開發者確認的問題

## 品質守則
- **不編造**：找不到的欄位寫「未填寫」，不要猜
- **保留原術語**：繁中 + 英文縮寫保留原樣，不翻譯
- **原樣 SQL**：從截圖轉錄 SQL 時逐字複製，不改寫格式
- **時間戳保留**：簽名旁的時間戳要完整保留
- **所有來源都要讀**：不可跳過任何來源檔
- **標註來源**：每段資訊標註來自哪個檔案
- **IS vs MS**：Product 名稱若疑似 typo 要保留原樣並註記
- **永遠不得修改 `wiki/` 下任何檔案**（包括 `wiki/log.md`、`wiki/index.md`、`wiki/**/*.md`）— 本 skill 是 raw 階段前處理，wiki 寫入由 `/ingest` 負責
- **MODE=dry-run 時禁止修改** `raw/isms/log.md`

## 自檢清單（產出後執行）
- [ ] 資料夾內所有來源檔都已讀取（無遺漏）
- [ ] 檔頭 sources 列出所有來源檔
- [ ] 原始三大段（申請/評估/驗收）都有轉錄
- [ ] 所有 backlog 編號已列出
- [ ] 所有 SQL 範例已完整轉錄
- [ ] 所有簽名時間戳已擷取
- [ ] 圖片來源的內容已透過 vision 辨識並整合
- [ ] 來源差異已用標記格式註明
- [ ] 已註記來源範本版本（若表單範本有版本差異）與對應公司名
- [ ] `raw/isms/log.md` 已追加（commit 模式）
- [ ] **未修改 `wiki/log.md` 或 `wiki/` 下任何檔案**（本 skill 屬 raw 階段，禁止動 wiki）
- [ ] 變更範圍分析已產出並包含 wiki 交叉引用
- [ ] 已呼叫 spec-by-example 並通過人類確認 Gate（或正確標註 blocked）
- [ ] `{FOLDER_NAME}-測試規格.md` 已建立，包含假設審計 + 邊界地圖 + Example Mapping + 測試骨架對應
- [ ] `raw/isms/log.md` 中 `sbe_status` 欄位已填寫

## 輸出回報
執行完成後回報：
1. 處理的資料夾名稱
2. 來源檔清單與類型統計
3. 模式（新建 / 重跑）
4. 擷取到的 Backlog 編號清單
5. 擷取到的 SQL 範例數量
6. 自檢結果
7. SBE 結果：假設審計狀態、Example 數量（Happy/Edge/Error）、sbe_status
8. 測試規格文件路徑
9. 變更範圍分析報告（markdown）

## 使用範例
```
# 掃描所有子資料夾
使用者: /ingest-isms

# 指定單一資料夾（只需資料夾名，自動補 raw/isms/ 前綴）
使用者: /ingest-isms "ISMS-114-08-退費不跳停機"

# 新增截圖後重跑
使用者: 我在 ISMS-114-08-退費不跳停機 資料夾加了幾張截圖，重新 ingest 一下

# dry-run 模式
使用者: /ingest-isms --mode=dry-run
```

## 版本
- v2.3 (2026-04-21): **raw 與 wiki 階段分離** — log 追加目標從 `wiki/log.md` 改為 `raw/isms/log.md`。原因：`wiki/log.md` 是 `/ingest`（raw→wiki 階段）的已處理清單追蹤依據，raw 階段若寫入會讓 `/ingest` 誤判檔案「已 ingest」而跳過，導致 wiki 無法更新。核心原則新增第 6 條明確禁止觸碰 `wiki/`
- v2.2 (2026-04-21): 整合 spec-by-example skill，Step 7 分析後自動呼叫 SBE 產出 `{FOLDER_NAME}-測試規格.md`，保留人類確認 Gate
- v2.1 (2026-04-16): 新增 `.xls` 支援；Excel（xls/xlsx）轉換時產出獨立 `.md` 檔存放在同資料夾
- v2.0 (2026-04-09): 多來源整合，支援 PNG/JPG/XLSX/TXT，可重跑覆寫
- v1.0 (2026-04-07): 初版，單一 PDF/DOCX 處理
