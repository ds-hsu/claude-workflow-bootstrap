# 起手 Skills 模板

本目錄存放四個起手 skill 的快照，`/init-product-wiki` skill 會將它們複製到新建立的產品 wiki 的 `.claude/skills/` 目錄。

## 四個起手 skill

- `ingest/`：從 `raw/` 提取一般知識進 `wiki/`，並同步 Coverage State / Gap 生命週期
- `ingest-isms/`：從 `raw/isms/` 的 ISMS 變更單資料夾提取結構化知識（含 gap-candidate 偵測）
- `wiki-query/`：從 wiki 回答使用者問題；查不到時寫入 `raw/coverage-gaps/`
- `spec-by-example/`：依 wiki 知識產生 Given-When-Then 測試規格

## 內容性質

- **機制通用**：所有檔案路徑均為相對路徑（`raw/`、`wiki/`、`isms/`），不綁定特定機器或產品
- **ISMS 表單範本**：`ingest-isms` 的 `templates/isms-case-template.md` 是以 ISMS-L4 系列變更申請單的結構設計。若你的產品線使用不同表單，需要修改此模板與相關提取規則
- **持續迭代**：skill 本身會隨需求持續優化，本處為建立當下的快照。未來若需要重新同步最新版，請手動更新

## 拿到後建議做的客製

1. **`ingest/SKILL.md`** — 檢視「掃描目錄清單」，依你的產品實際 `raw/` 子目錄補上對應項目
2. **`ingest-isms/templates/isms-case-template.md`** — 若使用不同的資安變更申請表，替換為你們的格式
3. **`wiki/CLAUDE.md`** — 客製 schema（系統名稱、來源權威階層等），這是整個 wiki 的規則定義檔

## 為什麼不做自動 placeholder 化

skill 仍在持續迭代優化，做死的 placeholder 會讓同步變得困難。改成「複製快照 + 使用者自行客製」，讓每個產品線有自己的 skill 演化路徑。
