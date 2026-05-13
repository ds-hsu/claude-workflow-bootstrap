---
name: run-example
description: 建立拋棄式 demo-wiki/ 並帶學員走完整工作流程：ingest 一般需求文件、ingest ISMS 變更單、用 wiki-query 查詢、根據 wiki 做需求分析、產出測試規格。使用時機：學員說「跑電商範例」「demo walkthrough」、或明確呼叫 /run-example。
---

# run-example — 電商範例 walkthrough

## 用途

建立一個拋棄式 `demo-wiki/`，把 `fixtures/` 的電商假資料投放進去，然後**引導學員於另一個 Claude Code 視窗依序執行各 skill**，親眼看完整工作流程從原始文件到結構化知識的轉換。

這是新人學完 setup-claude 與 init-product-wiki 之後的「真實感受」步驟——學員不會在自己的產品 wiki 上練手（怕弄壞），改用拋棄式 demo 練。

## 觸發條件

- 學員說「跑電商範例」「demo walkthrough」「我想看看工作流程長什麼樣」
- 明確呼叫 `/run-example`

## 必讀

1. `fixtures/README.md`（電商假資料說明）
2. `templates/product-wiki-skeleton/` 結構
3. `templates/skills/` 四個起手 skill

## 執行步驟

### Step 0：環境檢查

1. 確認在 bootstrap repo 根目錄（看得到 `templates/`、`fixtures/`）
2. 設定固定產品代號 = `ShopDemo`、顯示名稱 = `ShopDemo 示範 Wiki`
3. 目標路徑 = `<bootstrap repo>/demo-wiki/`

### Step 1：處理既有 demo-wiki/

若 `demo-wiki/` 已存在：
```
demo-wiki/ 已存在（可能是上次 walkthrough 的殘留）。是否刪除後重建？[y/N]
```
- 學員回 y → `rm -rf demo-wiki`（用 Bash 工具），繼續
- 學員回 n 或非 y → 中止，告知「若要重跑請先手動刪除 demo-wiki/」

### Step 2：建立骨架

執行 `/init-product-wiki` 同等邏輯（**不用呼叫該 skill，直接內聯做**，因為產品代號固定、路徑固定、不需互動）：

1. 建立 `demo-wiki/` 目錄
2. 從 `templates/product-wiki-skeleton/` 遞迴複製到 `demo-wiki/`，做佔位符替換：
   - `{{PRODUCT_NAME}}` → `ShopDemo`
   - `{{PRODUCT_DISPLAY_NAME}}` → `ShopDemo 示範 Wiki`
3. 從 `templates/skills/` 複製四個 skill 到 `demo-wiki/.claude/skills/`
4. **不執行 `git init`**（demo 是拋棄式，不需版控）

### Step 3：投放電商假資料

從 `fixtures/` 複製到 `demo-wiki/raw/` 對應位置：

| 來源 | 目的地 |
|---|---|
| `fixtures/requirements/*.md` | `demo-wiki/raw/shopdemo-requirements/` |
| `fixtures/isms/*/` | `demo-wiki/raw/isms/<同名子資料夾>/` |
| `fixtures/diagrams/*.drawio` | `demo-wiki/raw/drawio/` |

用 Bash 工具 `cp -r` 即可。

### Step 4：印 walkthrough 指引

顯示如下（依序、清晰分段）：

```
================================================================
                   準備完成 — 以下是 walkthrough
================================================================

demo-wiki 已準備好。現在請開啟一個新的 Claude Code 視窗，
切換到 demo-wiki 後啟動 claude：

  cd demo-wiki
  claude

然後依序執行下列步驟（每一步觀察 Claude 如何操作檔案系統）：

【4.1 一般知識 ingest】
  在 Claude Code 中輸入：
    /ingest
  預期觀察：
    - Claude 會掃描 raw/shopdemo-requirements/ 的 4 份需求文件
    - wiki/ 下 systems/、procedures/、entities/ 等類別目錄會被填入結構化 MD
    - wiki/index.md 會加入新頁面的連結
    - wiki/log.md 會 append 本次 ingest 條目
    - wiki/coverage/topics/ 會根據掃描結果建立 stub topic
    - 若 raw 有 gap-candidate（本範例無），會自動寫入 raw/coverage-gaps/

【4.2 ISMS ingest】
  在 Claude Code 中輸入：
    /ingest-isms
  預期觀察：
    - Claude 會掃描 raw/isms/ISMS-115-04-購物車金額計算修正/ 資料夾
    - 產出結構化 ISMS MD（含欄位完整度檢核）與變更範圍分析文件
    - 分析文件含 ## 知識盲點 段，列出與既有 wiki 比對發現的 gap-candidate
    - 下次 /ingest 會收割這些 candidate 寫入 raw/coverage-gaps/

【4.3 查詢與 gap 發現】
  在 Claude Code 中輸入：
    /wiki-query "ShopDemo 的退款流程涉及哪些系統？"
  預期觀察：
    - Claude 會走 INDEX_LOOKUP → COVERAGE_LOOKUP → PAGE_READ search_trail
    - 若 wiki 內已涵蓋：附上 coverage level 標註的答案
    - 若資訊不足：在 raw/coverage-gaps/{topic}.md 寫一條 gap entry，
      告知「已建立 gap entry，需要人類補資料」

【4.4 需求分析／設計規劃】
  在 Claude Code 中直接問它（不需要 slash command）：
    根據現有 wiki，幫我規劃一個新功能：
    「在結帳頁加入紅利點數折抵（與折扣碼可同時使用）」
  預期觀察：
    - Claude 會引用 wiki/systems/、wiki/procedures/ 的既有知識
    - 提出影響範圍、資料模型變更、API 增修、UI 變動等分析
    - 若發現知識缺口，會建議用 /wiki-query 釐清

【4.5 測試規格產出】
  在 Claude Code 中輸入（承接 4.4 的情境）：
    /spec-by-example 紅利點數折抵
  預期觀察：
    - Claude 產出 Given-When-Then 測試規格
    - 寫入 specs/sbe/YYYY-MM-DD-紅利點數折抵.md
    - 包含正向流程、反向流程、邊界條件多個 scenario

================================================================
                  你剛剛走的就是真實工作流程
================================================================

| demo 步驟                | 真實工作對照                            |
|--------------------------|----------------------------------------|
| 4.1 /ingest              | 把產品 PM 文件、架構筆記結構化進 wiki    |
| 4.2 /ingest-isms         | 把 ISMS 變更單轉為可交叉參考的結構化知識  |
| 4.3 /wiki-query          | 查詢知識、自動沉澱 gap                  |
| 4.4 問 Claude 規劃功能    | 做需求分析、影響評估、技術規劃           |
| 4.5 /spec-by-example     | 產出 BDD 測試規格，供開發與 QA 共用       |

走完後你可以：
  - 保留 demo-wiki/ 繼續實驗（例如試問 /wiki-query 觸發 gap 機制）
  - 或執行 rm -rf demo-wiki/ 清除（或請 Claude 幫你刪）

之後請移駕到你用 /init-product-wiki 建立的真實產品 wiki，
開始用自家文件跑一輪。
```

## 為何要學員另開 Claude Code 視窗？

`demo-wiki/` 內有它自己的 `CLAUDE.md` 與 `.claude/skills/`，**只有在 demo-wiki 目錄內啟動 Claude Code 才會載入到那些 skill**。本 bootstrap repo 是另一套 context（只有 setup-claude / init-product-wiki / run-example 這三個 bootstrap-only skill）。

讓學員親手 `cd demo-wiki && claude` 是教學重點：他們會理解「Claude Code 的 skill / CLAUDE.md 是 per-directory 的」，這對未來自己用產品 wiki 很關鍵。

## 自檢

- [ ] `demo-wiki/` 下有完整 skeleton（CLAUDE.md / raw/ / wiki/ / specs/ / .claude/skills/）
- [ ] `demo-wiki/raw/shopdemo-requirements/` 下有 4 份需求 MD
- [ ] `demo-wiki/raw/isms/ISMS-115-04-購物車金額計算修正/` 下有申請單.md
- [ ] `demo-wiki/raw/drawio/訂單狀態流程.drawio` 存在
- [ ] `demo-wiki/CLAUDE.md` 中 `{{PRODUCT_NAME}}` 已全數替換為 `ShopDemo`
- [ ] walkthrough 指引已完整印出，學員清楚下一步該開哪個視窗、跑哪個指令

## 品質守則

- **拋棄式**：強調 demo-wiki/ 是可以隨便玩、隨時刪的環境
- **真實對照**：5 個步驟結尾的對照表是教學的關鍵，必須印出
- **不執行學員端動作**：本 skill 只準備環境 + 印指引，不代學員執行 `cd demo-wiki && claude` 後的任何 slash command
- **冪等**：若學員選擇刪除重建，新建結果與第一次完全一致

## 版本

- **v1.0** (2026-05-13)：初版。取代 `scripts/4-run-example.ps1`。Step 4.3 新增 `/wiki-query` 與 gap 發現演練（呼應 Phase 8 的 Coverage State / Gap 設計）
