# {{PRODUCT_DISPLAY_NAME}}

本 wiki 為 `{{PRODUCT_NAME}}` 產品線的知識庫，以 Claude Code 為中心建立「文件 → 結構化知識 → 需求分析 → 測試規格」的工作流程。

## 目錄結構

| 目錄 / 檔案 | 用途 | 誰寫入 |
|---|---|---|
| `CLAUDE.md` | wiki schema、ingest@v3 規範、工作流程定義 | 人（初次需客製佔位符） |
| `raw/` | 原始文件投放區 | 人 |
| `raw/isms/<case>/` | ISMS 變更案資料夾；原始檔 + ingest-isms 產出的結構化 MD 共存 | 人 + `/ingest-isms` |
| `raw/isms/log.md` | ingest-isms 已處理案件追蹤（skill 自動維護） | `/ingest-isms` |
| `raw/drawio/` | drawio 流程圖原檔與轉出的 Mermaid MD | 人 + `/ingest-drawio`（若啟用） |
| `wiki/` | 從 raw ingest 後的結構化知識（Markdown） | `/ingest` |
| `wiki/_templates/` | 六種頁面模板（concept/entity/procedure/system/tech-note/troubleshooting） | 人 |
| `wiki/index.md` | 知識庫索引（依類別自動組織） | `/ingest` |
| `wiki/log.md` | ingest 已處理清單追蹤（skill 自動維護） | `/ingest` |
| `specs/sbe/` | spec-by-example 產出的 Given-When-Then 測試規格 | `/spec-by-example` |
| `.claude/skills/` | 產品專屬 skill 定義 | 人（必要時 Agent 協助） |

## 重要原則

- **raw/wiki 階段分離**：raw 階段 skill（如 `/ingest-isms`）不得修改 `wiki/log.md`，避免污染 `/ingest` 的已處理清單判斷
- `log.md` 只能由對應的 skill 寫入；人為修改會破壞追蹤機制

## 使用流程

1. 把原始文件（PDF、Word、drawio、會議紀錄等）放進 `raw/` 下對應的子目錄
2. 若文件屬於 ISMS 變更案：放進 `raw/isms/<case>/`，執行 `/ingest-isms`
3. 在 Claude Code 執行 `/ingest`，`wiki/` 會被填滿結構化知識
4. 需求分析 / 設計規劃：直接問 Claude，它會引用 `wiki/` 的內容
5. 測試規格：執行 `/spec-by-example`，結果寫入 `specs/sbe/`

## 首次使用前必做

- 閱讀 `CLAUDE.md` 全文，理解 ingest@v3 規範與三層架構原則
- 將 `CLAUDE.md` 內的 `<your-architecture>`、`<your-notes>`、`<Product1>`、`<ExampleSystemA>` 等佔位符替換為你的產品實際值
