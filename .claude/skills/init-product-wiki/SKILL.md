---
name: init-product-wiki
description: 替學員建立一個產品 wiki repo。互動式問產品代號、目標路徑、顯示名稱，然後從 templates/product-wiki-skeleton/ 複製骨架、做佔位符替換、複製四個起手 skill、git init。使用時機：學員說「幫我建立產品 wiki」「建立 XXX-wiki」、或明確呼叫 /init-product-wiki。
---

# init-product-wiki — 互動式建立產品 wiki

## 用途

為學員負責的產品線建立一個符合團隊契約的 wiki repo，內含：
- 完整目錄骨架（含 `wiki/coverage/`、`raw/coverage-gaps/`、六種頁面類別）
- 客製化前的 CLAUDE.md schema 範本
- 四個起手 skill（ingest、ingest-isms、wiki-query、spec-by-example）
- 已 `git init` 的本地 repo

學員之後可以馬上開始投放文件與做需求分析。

## 觸發條件

- 學員說「幫我建立產品 wiki」「建立 MyApp-wiki」「初始化 ShopX-wiki」
- 明確呼叫 `/init-product-wiki`

## 必讀

1. `templates/product-wiki-skeleton/` 的整體結構（用 Glob 看一遍）
2. `templates/skills/` 下四個起手 skill 的目錄結構

## 執行步驟

### Step 0：環境檢查

1. **確認在 bootstrap repo 根目錄**：應該能看到 `templates/product-wiki-skeleton/` 與 `templates/skills/`。若不存在 → 告訴學員「請先 `cd` 到 claude-workflow-bootstrap repo 根目錄再執行」並中止
2. **確認 git 已安裝**：跑 `git --version`。失敗則告訴學員裝 git 後重試

### Step 1：互動式提問

依序問三個問題。每題給合理預設值；學員可直接 Enter 接受預設。

#### Q1：產品代號（英文，必填）

```
產品代號（英文，例 MyApp、ShopX）：
```

驗證規則：必須符合正規表達式 `^[A-Za-z][A-Za-z0-9_-]*$`（英文字母開頭、僅含英數/底線/連字號）。不符合時重問。

#### Q2：Wiki 目標路徑

```
Wiki 目標路徑 [預設：<bootstrap repo 的上一層>/<產品代號>-wiki]：
```

預設值計算：取 bootstrap repo 的 parent 目錄（用 Bash `pwd`、`dirname` 推導）+ `/<產品代號>-wiki`。

#### Q3：Wiki 顯示名稱（中文）

```
Wiki 顯示名稱（中文）[預設：<產品代號> Wiki]：
```

### Step 2：確認

顯示彙整：

```
=== 將以下列設定建立產品 wiki ===
  產品代號    : MyApp
  目標路徑    : /c/Work/MyApp-wiki
  顯示名稱    : MyApp 內部系統知識庫
```

問「確認建立？[Y/n]」。學員若回 n 或非 Y → 中止；若回 Y 或直接 Enter → 繼續。

### Step 3：檢查目標路徑

| 狀況 | 動作 |
|---|---|
| 目錄不存在 | 建立目錄（`mkdir -p`） |
| 目錄存在且為空 | 繼續 |
| 目錄存在但非空（除 .git 外） | 中止並告知學員「目標路徑非空。請清空或選擇其他路徑」 |
| 目錄存在且僅含 .git | 視為「沿用既有 git repo」，繼續 |

### Step 4：複製 skeleton 並做佔位符替換

從 `templates/product-wiki-skeleton/` 遞迴複製所有檔案到目標路徑。

**佔位符替換規則**：
- 對下列副檔名的檔案做文字替換：`.md`、`.txt`、`.yaml`、`.yml`、`.json`、`.ps1`、`.sh`、`.py`
- 替換 `{{PRODUCT_NAME}}` → 學員輸入的產品代號
- 替換 `{{PRODUCT_DISPLAY_NAME}}` → 學員輸入的顯示名稱
- 其他副檔名（如 `.drawio`、`.png`）原樣複製，不做替換
- `.gitkeep` 保留複製，讓空目錄能被 git 追蹤

**實作建議**：用 Glob 列出所有檔案，逐一處理。文字檔用 Read + 字串替換 + Write；二進位檔用 Bash `cp`。

### Step 5：複製起手 skills

把 `templates/skills/` 下四個 skill 目錄（`ingest/`、`ingest-isms/`、`wiki-query/`、`spec-by-example/`）整個複製到 `<目標路徑>/.claude/skills/`。

skill 內部檔案**不做佔位符替換**（skill 是通用的，無需客製）。

### Step 6：git init

於目標路徑執行 `git init -b main`（若該路徑已是 git repo 則略過）。

### Step 7：總結與後續步驟

顯示：

```
=== 完成 ===

後續步驟：
  1. cd <目標路徑>
  2. 開啟 CLAUDE.md，依你的產品實際情況調整 <your-architecture>、<your-notes>、
     <Product1>、<ExampleSystemA> 等佔位符
  3. 把你的原始文件（PDF、Word、drawio、筆記等）放進 raw/ 對應子目錄
  4. 在新 wiki 目錄裡開 Claude Code，執行 /ingest 開始把原始文件結構化進 wiki/
  5. 若欲連接遠端 git repo：
     git remote add origin <url>
     git push -u origin main

首次啟用前強烈建議：完整走過一次 CLAUDE.md，理解 ingest@v4 規範、Coverage State 與
Gap Lifecycle 設計、以及三層架構原則。
```

## 自檢

- [ ] 目標路徑下有 `CLAUDE.md`、`README.md`、`raw/`、`wiki/`、`specs/`、`.claude/`
- [ ] `wiki/coverage/coverage-state-spec.md` 存在
- [ ] `raw/coverage-gaps/gap-source-spec.md` 存在
- [ ] `.claude/skills/` 下有 4 個 skill 目錄
- [ ] `CLAUDE.md` 中 `{{PRODUCT_NAME}}` 已全數替換（grep 應找不到任何 `{{PRODUCT_NAME}}` 或 `{{PRODUCT_DISPLAY_NAME}}`）
- [ ] 目標路徑為 git repo（`<目標路徑>/.git/` 存在）

## 品質守則

- **冪等**：學員若重跑（先清空目標路徑後），結果完全一致
- **不覆寫**：目標路徑非空時直接中止，不嘗試混合複製
- **保留 .git**：若沿用既有 git repo，不刪 `.git`
- **明確失敗訊息**：任何步驟出錯都清楚告訴學員出在哪一步、如何修復

## 版本

- **v1.0** (2026-05-13)：初版。取代 `scripts/3-init-product-wiki.ps1`。改由 Claude 用 Glob/Read/Write/Bash 工具完成複製與替換，跨平台一致
