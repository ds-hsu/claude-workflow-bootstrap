# ingest skill

將 `raw/` 下已結構化的 markdown 檔依照 `ingest@v3`（Karpathy LLM Wiki 方法）寫入 `wiki/` 知識庫。

## 與其他 ingest skill 的關係

| Skill | 用途 | 輸入 | 輸出 |
|---|---|---|---|
| `ingest-isms` | 前處理：解析 ISMS 變更單 | `.pdf` / `.docx` | `raw/isms/{feature}/` 資料夾 |
| `ingest-drawio` | 前處理：轉換 draw.io 流程圖 | `.drawio` | `raw/drawio/{project}/` 資料夾 |
| **`ingest`（本 skill）** | **wiki 寫入：將 raw MD 編譯成 wiki 頁面** | **raw `.md`** | **`wiki/` 頁面** |

前兩個 skill 是「原始格式 → raw MD」的前處理；本 skill 是「raw MD → wiki」的 Karpathy 編譯步驟。

## 使用方式

```
/ingest <raw_file_path> [MODE=commit|dry-run]
```

預設 MODE 為 `commit`（完整寫入 wiki、更新 index.md 與 log.md）。

## 執行規範來源

本 skill 的核心邏輯完全遵循 `CLAUDE.md` 中 `ingest@v3` prompt 的定義。若需調整 ingest 行為，修改 `CLAUDE.md` 即可，本 skill 會自動套用。
