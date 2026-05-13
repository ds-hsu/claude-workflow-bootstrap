# ingest-isms Skill

自動化將 ISMS 軟體變更申請單（多來源）轉換為產品 wiki 知識庫條目的 Claude Code Skill。

## 為什麼需要這個 Skill

手動 ingest 一份 ISMS 變更單需要：
1. 盤點資料夾內所有來源檔（PDF、DOCX、截圖、Excel、TXT）
2. 用 markitdown 轉 PDF/DOCX/XLSX 為 markdown
3. 若是 PDF 再用 PyMuPDF 渲染每頁
4. 用 Claude vision 讀截圖與 PDF 頁面中的 SQL / Backlog / UI
5. 合併所有來源，處理矛盾
6. 按命名規範決定檔名
7. 依模板填入結構化 markdown
8. 產出修改建議與執行計畫
9. 追加 log

Skill 把流程固定化，確保：
- 資料夾內所有來源都被讀取，不遺漏
- 截圖內容不會漏（PNG/JPG 走 vision、PDF 走渲染 + vision）
- 不同來源的矛盾有標記
- 新增來源後可重跑，覆寫既有產出

## 檔案結構

```
.claude/skills/ingest-isms/
├── SKILL.md                         # 主 prompt（Claude 呼叫時載入）
├── README.md                        # 本檔（人類閱讀）
├── scripts/
│   ├── render-pdf.py               # PyMuPDF 渲染 PDF 頁面為 PNG
│   └── convert.sh                  # markitdown 轉換 wrapper
└── templates/
    └── isms-case-template.md       # 轉錄骨架
```

## 呼叫方式

### 方式 1：掃描所有子資料夾
```
/ingest-isms
```

### 方式 2：指定單一資料夾（只需資料夾名，自動補 `raw/isms/` 前綴）
```
/ingest-isms "ISMS-114-08-退費不跳停機"
```

### 方式 3：新增來源後重跑
```
# 先把新檔案丟進資料夾，再執行
/ingest-isms "ISMS-114-08-退費不跳停機"
```

### 方式 4：dry-run
```
/ingest-isms --mode=dry-run
```

## 支援的來源格式

| 格式 | 副檔名 | 處理方式 |
|---|---|---|
| PDF | `.pdf` | markitdown 文字層 + PyMuPDF 渲染 → vision |
| Word | `.docx` | markitdown 文字層 |
| 圖片 | `.png` `.jpg` `.jpeg` | Claude vision 直接辨識 |
| Excel | `.xlsx` | markitdown 轉表格 |
| 純文字 | `.txt` | 直接讀取 |

## 資料夾結構（處理前後）

### 處理前（使用者準備）
```
raw/isms/ISMS-114-08-退費不跳停機/
├── ISMS-L4-69-退費功能異動.pdf      ← 主表單
├── sql-screenshot.png               ← 補充截圖
├── backlog-list.xlsx                ← Backlog 匯出
└── notes.txt                        ← 補充說明
```

### 處理後（skill 產出）
```
raw/isms/ISMS-114-08-退費不跳停機/
├── ISMS-L4-69-退費功能異動.pdf      ← 原始檔（不動）
├── sql-screenshot.png               ← 原始檔（不動）
├── backlog-list.xlsx                ← 原始檔（不動）
├── notes.txt                        ← 原始檔（不動）
├── ISMS-114-08-退費不跳停機.md      ← 結構化 markdown（skill 產出）
└── ISMS-114-08-退費不跳停機-分析.md ← 修改建議（skill 產出）
```

## 重跑機制

新增來源檔後再次執行 `/ingest-isms`，skill 會：
1. 重新讀取資料夾內**所有**來源檔（包括之前已讀過的）
2. 重新合併、重新填模板
3. **覆寫**既有的結構化 .md 與分析 .md
4. log.md 記錄為「重跑」模式

## 依賴
- Python 3.10+
- markitdown ≥ 0.1.5
- PyMuPDF（僅 PDF 處理需要）

若路徑改變，修改：
- `SKILL.md` 中的 `PY=...`
- `scripts/convert.sh` 的 `PYTHON_BIN` 預設值

## 命名規範的由來

`ISMS-L4-69` 是**表單類別編號**，不是單一案件編號。所有變更案都共用這個號碼。為避免檔名碰撞，採用日期+主題命名。

範例：
| 申請日 | 主題 | 資料夾名 |
|---|---|---|
| 2025/08/20 | 退費系統不跳停機 | `ISMS-114-08-退費不跳停機` |
| 2026/02/03 | 行動客服 App 評論連結 | `ISMS-115-02-行動客服app-google評論連結` |

## 品質守則（摘錄）

- **不編造**：找不到欄位寫「未填寫」
- **截圖為準**：markitdown 與截圖矛盾時以截圖為準
- **原樣 SQL**：逐字轉錄，不改格式
- **所有來源都要讀**：不可跳過任何檔案
- **標註來源**：每段資訊標註來自哪個檔案

## 版本歷史
- v1.0 (2026-04-07): 初版，單一 PDF/DOCX 處理
- v2.0 (2026-04-09): 多來源整合，支援 PNG/JPG/XLSX/TXT，可重跑覆寫

## 關聯
- 靈感來源：本專案的 `ingest@v4` prompt（`CLAUDE.md`），但針對 ISMS 場景特化
