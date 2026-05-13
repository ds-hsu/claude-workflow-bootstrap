# Claude Workflow Bootstrap — 使用手冊

讓團隊同仁用最少步驟建立起「llm-wiki → 需求分析 → 設計規劃 → 測試腳本 → 開發 → 部署 → E2E 測試」的 AI 協作工作流程。

> **核心觀念**：你只需要手動裝兩個工具（Git + Claude Code），其他設定全部跟 Claude Code 用自然語言對話完成。從第一分鐘就在用 Claude，沒有「教學模式 vs 實戰模式」斷層。

---

## 目錄

1. [概觀（5 分鐘掌握整套流程）](#概觀5-分鐘掌握整套流程)
2. [系統需求](#系統需求)
3. [Step 1 — 裝 Git 與 Claude Code](#step-1--裝-git-與-claude-code)
4. [Step 2 — 設定 ~/.claude/ 共用環境](#step-2--設定-claude-共用環境)
5. [Step 3 — 建立你的產品 wiki](#step-3--建立你的產品-wiki)
6. [Step 4（選擇性）— 跑電商範例 walkthrough](#step-4選擇性--跑電商範例-walkthrough)
7. [日常工作流：用產品 wiki 做事](#日常工作流用產品-wiki-做事)
8. [進階：Coverage State 與 Gap Lifecycle](#進階coverage-state-與-gap-lifecycle)
9. [本 Repo 結構](#本-repo-結構)
10. [產出的產品 wiki 結構](#產出的產品-wiki-結構)
11. [兩層 skill 結構](#兩層-skill-結構)
12. [設計理念](#設計理念)
13. [疑難排解](#疑難排解)
14. [授權](#授權)

---

## 概觀（5 分鐘掌握整套流程）

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  Step 1（手動）       Step 2-4（跟 Claude 對話）   日常工作（對話）     │
│  ─────────────       ─────────────────────────   ─────────────────  │
│                                                                     │
│  裝 Git + Claude  →  設定 ~/.claude/         →   /ingest 把文件        │
│  Code                /setup-claude               結構化進 wiki         │
│                                                                     │
│                      建立產品 wiki            →   /wiki-query 查詢       │
│                      /init-product-wiki          並沉澱 gap            │
│                                                                     │
│                      (選) 跑電商範例          →   /spec-by-example     │
│                      /run-example                產出 BDD 測試規格      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**全程只有 Step 1 需要敲指令；Step 2 之後全部跟 Claude 講話即可。**

---

## 系統需求

| 項目 | 需求 |
|---|---|
| 作業系統 | Windows 10/11 或 macOS Ventura 13+ |
| 套件管理器 | Windows：winget（10 1809+ 內建）／macOS：[Homebrew](https://brew.sh) |
| 網路 | 能存取 GitHub、npm registry、Anthropic API endpoint |
| Claude Code 帳號 | Pro 或 Team plan（學員設定階段會用到較多 token） |
| 磁碟空間 | < 200 MB（Git + Claude Code 本體；plugin 為選擇性，視日後安裝決定） |

---

## Step 1 — 裝 Git 與 Claude Code

**這是整個流程唯一需要手動敲指令的部分。**

### Windows

打開 PowerShell（一般權限即可）：

```powershell
winget install --id Git.Git --exact --silent `
  --accept-package-agreements --accept-source-agreements

winget install --id Anthropic.ClaudeCode --exact --silent `
  --accept-package-agreements --accept-source-agreements
```

裝完**關閉 PowerShell 視窗、重新開啟**（讓新的 PATH 生效）。

驗證：

```powershell
git --version          # 應回傳 git version 2.x.x
claude --version       # 應回傳 Claude Code 版本
```

詳細 troubleshoot 見 [docs/setup-windows.md](docs/setup-windows.md)。

### macOS

打開 Terminal：

```bash
brew install git
brew install anthropic/anthropic/claude-code
```

驗證：

```bash
git --version          # 應回傳 git version 2.x.x
claude --version       # 應回傳 Claude Code 版本
```

詳細 troubleshoot 見 [docs/setup-mac.md](docs/setup-mac.md)。

### Clone 本 repo

任挑一個工作目錄（例：Windows `C:\Work\`、macOS `~/Work/`）：

```bash
# 兩個平台共用（在 PowerShell 或 Terminal 都可以）
cd <你的工作目錄>
git clone <bootstrap-repo-url> claude-workflow-bootstrap
cd claude-workflow-bootstrap
claude
```

最後一行 `claude` 會啟動 Claude Code，從現在開始**所有設定都用自然語言對話**。

---

## Step 2 — 設定 `~/.claude/` 共用環境

在 Claude Code 視窗裡輸入任一句即可：

```
幫我設定 ~/.claude/
```

或：

```
/setup-claude
```

### Claude 會做什麼

1. **備份**你既有的 `~/.claude/settings.json`（如果有的話），命名為 `settings.json.bak.{timestamp}`
2. 把團隊共用範本 `templates/claude-settings/settings.json.template` deep merge 進你的設定。**目前範本最小化，只含核心安全規則**：
   - `permissions.deny`：9 條破壞性指令黑名單（rm -rf、force push、reset --hard…）
   - `permissions.ask`：8 條須二次確認指令（rm、git checkout --、docker rm…）
3. **保留你原有的設定**——只補缺漏 key，不覆寫你已設的值；陣列取聯集去重
4. 列出所有變動讓你過目

### 為何不裝 plugin？

第一次體驗保持最小化。任何 plugin（superpowers、commit-commands、skill-creator、claude-mem 等）都**不會自動安裝**，避免被 plugin 初始化（特別是 claude-mem 的 API key 設定）卡住。

熟悉工作流後想加 plugin，直接跟 Claude 說即可：

```
幫我裝 superpowers plugin
幫我裝 claude-mem plugin 並完成初始化
```

---

## Step 3 — 建立你的產品 wiki

回到 bootstrap repo 目錄（`cd claude-workflow-bootstrap`），再次啟動 `claude`，輸入任一句：

```
幫我建立產品 wiki，產品代號叫 MyApp
```

或：

```
/init-product-wiki
```

### Claude 會互動問三個問題

1. **產品代號**（英文，例 `MyApp`、`ShopX`）— 需符合 `^[A-Za-z][A-Za-z0-9_-]*$`
2. **Wiki 目標路徑**（預設 `<bootstrap 上一層>/<產品代號>-wiki`）
3. **Wiki 顯示名稱**（中文，預設 `<產品代號> Wiki`）

### Claude 會幫你做的事

- 複製 `templates/product-wiki-skeleton/` 整個骨架到目標路徑
- 替換所有 `{{PRODUCT_NAME}}` 與 `{{PRODUCT_DISPLAY_NAME}}` 佔位符
- 複製 4 個起手 skill 到 `<目標路徑>/.claude/skills/`
- 跑 `git init -b main`

### 跑完之後

Claude 會告訴你：

```
後續步驟：
  1. cd <目標路徑>
  2. 開啟 CLAUDE.md，依產品實際情況調整 <your-architecture>、<your-notes>、
     <Product1>、<ExampleSystemA> 等佔位符
  3. 把你的原始文件（PDF、Word、drawio、筆記等）放進 raw/ 對應子目錄
  4. 在新 wiki 目錄裡開 Claude Code，執行 /ingest 開始把原始文件結構化進 wiki/
```

**強烈建議**：首次啟用前完整走過一次 CLAUDE.md，理解 ingest@v4 規範、Coverage State / Gap Lifecycle 設計、以及三層架構原則。

---

## Step 4（選擇性）— 跑電商範例 walkthrough

如果你想先在拋棄式環境裡看完整工作流程怎麼跑、再開始用真實文件，**在 bootstrap repo 內**跟 Claude 說：

```
跑一次電商範例 walkthrough
```

或：

```
/run-example
```

### Claude 會做什麼

1. 在 bootstrap repo 根目錄建 `demo-wiki/`（拋棄式，跑完可刪）
2. 從 `templates/product-wiki-skeleton/` 複製骨架，固定產品代號 `ShopDemo`
3. 投放 `fixtures/` 假資料到 `demo-wiki/raw/`：
   - 4 份電商需求文件 → `raw/shopdemo-requirements/`
   - 1 份 ISMS 變更單 → `raw/isms/ISMS-115-04-購物車金額計算修正/`
   - 1 張 drawio 流程圖 → `raw/drawio/`
4. 印出 5 步驟 walkthrough 指引

### 接著你開新 Claude Code 視窗，cd 到 demo-wiki/，依序跑：

| Step | 指令 | 觀察重點 |
|---|---|---|
| 4.1 | `/ingest` | 4 份需求文件被拆解到 `wiki/systems/`、`procedures/`、`entities/`；index.md 與 log.md 自動更新 |
| 4.2 | `/ingest-isms` | ISMS 申請單轉成結構化 markdown + 分析文件；含 `## 知識盲點` 段 |
| 4.3 | `/wiki-query "ShopDemo 的退款流程涉及哪些系統？"` | 走 INDEX_LOOKUP → COVERAGE_LOOKUP → PAGE_READ 軌跡；若資訊不足會寫 gap 到 `raw/coverage-gaps/` |
| 4.4 | （自然語言）「根據現有 wiki 規劃紅利點數折抵功能」 | Claude 引用既有頁面做影響分析、資料模型變更建議 |
| 4.5 | `/spec-by-example 紅利點數折抵` | 產出 Given-When-Then BDD 測試規格 |

走完這 5 步，你就體驗了從原始文件 → 結構化知識 → 查詢與沉澱 → 需求分析 → 測試規格的完整循環。

---

## 日常工作流：用產品 wiki 做事

設定完之後，每次要用：

```bash
cd <你的產品-wiki>
claude
```

### 常用對話／指令

| 場景 | 跟 Claude 說 |
|---|---|
| 投放新文件後寫進 wiki | 「ingest 未處理的 raw」 或 `/ingest` |
| 處理 ISMS 變更單 | `/ingest-isms` |
| 把 drawio 流程圖轉 Mermaid | `/ingest-drawio <path>` |
| 查某個系統怎麼運作 | `/wiki-query "問題..."` 或直接自然語言問 |
| 規劃新功能 | 「根據現有 wiki 規劃一個 XXX 功能」 |
| 產出 BDD 測試規格 | `/spec-by-example <功能名>` |
| 記錄當日工作 | `/daily-log` |

### 工作流的長期效益

每次跑 `/ingest` 或 `/wiki-query`，wiki 都會**複利成長**：
- 新 raw 進來自動更新 10-15 個相關頁面
- 查詢過程發現的盲點自動成為 gap，下次 ingest 時被處理
- ISMS 變更影響範圍自動交叉比對，產出可直接建 ticket 的工作項目

---

## 進階：Coverage State 與 Gap Lifecycle

新建立的產品 wiki 內建**知識斷層追蹤系統**，避免「Claude 答不出來但你不知道」的靜默失敗。

### Gap 兩條來源路徑

1. **Query-time discovery**：`/wiki-query` 查不到 → 自動寫 `raw/coverage-gaps/{topic}.md`
2. **Analysis-time discovery**：`/ingest-isms` 分析變更單時偵測 wiki 盲點 → 寫 gap-candidate → 下次 `/ingest` Step 8a 收割為正式 gap

### Gap 兩階段驗證

```
open → resolved_pending → resolved → closed
              ↑              ↓
              └── reopened ──┘（若 query 答不出）
```

`/ingest` 寫入相關內容後**只能切 `resolved_pending`**，不直接 `closed`。必須等下次 `/wiki-query` 觸到此 topic、實際驗證可回答，才切 `resolved`；連續 N 次後才能 `closed`。**避免 LLM 主觀判斷誤關**。

### Raw-only 設計

**gap entry 只存於 `raw/coverage-gaps/`**，wiki 端 `wiki/coverage/topics/{topic}.md` 只存 coverage metadata（level、wiki_pages、last_ingest），不鏡像 gap 內容。`/wiki-query` 一律去 raw 讀 gap。

### 完整規格

產品 wiki 內：
- `CLAUDE.md` → 「Coverage State 與 Gap Lifecycle」章節
- `wiki/coverage/coverage-state-spec.md` → wiki 端 metadata 規格
- `raw/coverage-gaps/gap-source-spec.md` → gap 事實來源規格

---

## 本 Repo 結構

```
claude-workflow-bootstrap/
├── README.md                       # 本檔（使用手冊）
├── docs/
│   ├── setup-windows.md            # Step 1（Win）安裝詳細指引與 troubleshoot
│   └── setup-mac.md                # Step 1（Mac）安裝詳細指引與 troubleshoot
├── .claude/skills/                 # 3 個 bootstrap-only skill（替學員設定環境）
│   ├── setup-claude/               # Step 2 邏輯
│   ├── init-product-wiki/          # Step 3 邏輯
│   └── run-example/                # Step 4 邏輯
├── templates/
│   ├── claude-settings/            # ~/.claude/ 範本（settings.json.template）
│   ├── product-wiki-skeleton/      # 產品 wiki 目錄骨架
│   │   ├── CLAUDE.md               # wiki schema（含 ingest@v4、query@v2、Coverage/Gap）
│   │   ├── raw/                    # 三層架構第 1 層：原始資料
│   │   │   └── coverage-gaps/      # Gap 唯一事實來源
│   │   ├── wiki/                   # 三層架構第 2 層：LLM 維護的結構化知識
│   │   │   ├── coverage/           # 機器層索引（coverage level + pointer）
│   │   │   ├── _templates/         # 六種頁面模板
│   │   │   └── (concepts/systems/procedures/...)
│   │   └── specs/sbe/              # spec-by-example BDD 規格產出
│   └── skills/                     # 4 個起手 skill（會被 /init-product-wiki 複製進產品 wiki）
│       ├── ingest/
│       ├── ingest-isms/
│       ├── wiki-query/
│       └── spec-by-example/
└── fixtures/                       # 電商假資料（給 /run-example 用）
    ├── requirements/
    ├── isms/
    └── diagrams/
```

---

## 產出的產品 wiki 結構

跑 `/init-product-wiki` 後，目標路徑會長這樣（以 `MyApp` 為產品代號為例）：

### 初始狀態（剛建立完）

```
MyApp-wiki/
├── CLAUDE.md                          # wiki schema、ingest@v4、query@v2、Coverage/Gap 規範
├── README.md                          # 產品 wiki 入口文件（含 {{PRODUCT_DISPLAY_NAME}})
├── .git/                              # git init 完成（main 分支）
├── .claude/
│   └── skills/                        # 4 個起手 skill（從 bootstrap 複製）
│       ├── ingest/
│       ├── ingest-isms/
│       ├── wiki-query/
│       └── spec-by-example/
├── raw/                               # 第 1 層：原始資料（事實來源，唯一可變寫入點）
│   ├── drawio/                        # /ingest-drawio 產出的 Mermaid markdown
│   ├── isms/                          # ISMS 變更案資料夾（每案一個子目錄）
│   └── coverage-gaps/                 # Gap 唯一事實來源
│       └── gap-source-spec.md         # 規格說明（learners 必讀）
├── wiki/                              # 第 2 層：LLM 維護的結構化知識（編譯產物）
│   ├── index.md                       # 知識庫目錄（按類別組織）
│   ├── log.md                         # /ingest 處理日誌（append-only）
│   ├── _templates/                    # 六種頁面模板（給 /ingest 套用）
│   │   ├── concept.md
│   │   ├── entity.md
│   │   ├── procedure.md
│   │   ├── system.md
│   │   ├── tech-note.md
│   │   └── troubleshooting.md
│   ├── coverage/                      # 機器層知識覆蓋地圖
│   │   ├── coverage-state-spec.md     # 規格說明
│   │   └── topics/                    # 每個主題一個 .md 檔（metadata + pointer）
│   ├── concepts/                      # 概念頁（CICD、OLTP、TLS…）
│   ├── entities/                      # 實體頁（資料表、API、主機）
│   ├── procedures/                    # 操作流程
│   ├── systems/                       # 系統頁
│   ├── tech-notes/                    # 技術筆記
│   └── troubleshooting/               # 故障排除
└── specs/
    └── sbe/                           # /spec-by-example 產出的 BDD 規格
```

### 演化後狀態（跑過幾次 /ingest、/wiki-query 之後）

```
MyApp-wiki/
├── ...
├── raw/
│   ├── <your-architecture>/           # 你自己投放的架構快照（ARCHITECTURE.md 等）
│   ├── <your-notes>/                  # 你自己投放的維運筆記
│   ├── daily/                         # /daily-log 自動產出
│   │   └── {username}/{yyyyMMdd}.md
│   ├── drawio/                        # /ingest-drawio 產出
│   │   └── {project}/
│   │       ├── README.md
│   │       └── {page}.md              # Mermaid 視覺化 markdown
│   ├── isms/                          # /ingest-isms 產出
│   │   └── {ISMS-XXX-變更主題}/
│   │       ├── 申請單.md               # 結構化變更單
│   │       ├── {ISMS-XXX-變更主題}-分析.md   # 含 ## 知識盲點 段（gap-candidate）
│   │       └── {ISMS-XXX-變更主題}-測試規格.md  # spec-by-example 產出
│   └── coverage-gaps/                 # /wiki-query 與 /ingest 寫入的 gap entry
│       ├── gap-source-spec.md
│       ├── {topic-id-1}.md            # 對應 wiki/coverage/topics/{topic-id-1}.md
│       └── {topic-id-2}.md
├── wiki/
│   ├── log.md                         # 每次 /ingest 都會 append 一筆
│   ├── coverage/topics/
│   │   ├── {topic-id-1}.md            # frontmatter（coverage level、wiki_pages）+ 已覆蓋面向 + pointer
│   │   └── {topic-id-2}.md
│   ├── systems/
│   │   ├── {Product1}.md              # /ingest 從 raw 編譯出來
│   │   └── {ExampleSystemA}.md
│   ├── procedures/
│   │   └── {某 SOP}.md
│   └── ...
└── specs/sbe/
    └── 2026-05-13-紅利點數折抵.md      # /spec-by-example 產出
```

### 三層架構回顧

| 層 | 位置 | 角色 | 寫入規則 |
|---|---|---|---|
| **第 1 層：Raw** | `raw/` | 事實來源（不可變快照）| 你/`/ingest-isms`/`/ingest-drawio`/`/wiki-query`/`/daily-log` 可寫；**寫了不再修改** |
| **第 2 層：Wiki** | `wiki/` | LLM 維護的編譯產物 | **唯一寫入入口是 `/ingest`**；其他 skill 禁止直接寫 wiki/ |
| **第 3 層：Schema** | `CLAUDE.md` + spec 檔 | 結構與品質規範 | 由你或 maintainer 手動演化 |

衝突時以 raw 為準。wiki 是 raw 經 ingest@v4 prompt 規範編譯後的產物，可隨時刪掉重編。

---

## 兩層 skill 結構

本 repo 有**兩層**完全獨立的 skill，理解這個區別後就不會混淆：

| 層級 | 位置 | 用途 | 壽命 | 啟動方式 |
|---|---|---|---|---|
| Bootstrap skills | `.claude/skills/` | 替學員設定環境（setup-claude / init-product-wiki / run-example） | 用完即丟。**不複製到產品 wiki** | 在 bootstrap repo 內啟動 `claude` |
| 起手 skills | `templates/skills/` | 產品 wiki 內持續使用（ingest / ingest-isms / wiki-query / spec-by-example） | 跟著產品 wiki 一輩子 | 在產品 wiki 內啟動 `claude` |

**Claude Code 是 per-directory 載入 skill 的**——所以你在 bootstrap repo 啟動 `claude` 跟在產品 wiki 啟動 `claude`，看到的是兩套不同的 skill。

---

## 設計理念

- **學員從第 1 分鐘就在用 Claude Code**：避免「先學 PowerShell 腳本、之後又要學 AI 對話」的雙重認知負擔
- **跨平台天生支援**：Claude Code 自己處理 Win/Mac 路徑、JSON merge、檔案複製，不必維護 `.ps1` + `.sh` 雙寫
- **單一事實來源**：每個 bootstrap 步驟的邏輯都是一份 markdown SKILL，可讀、可審、可改
- **失敗可恢復**：跑壞了就跟 Claude 說「我剛剛狀態壞了，幫我看一下」，比 debug 腳本快多了
- **教學流 = 工作流**：你後續用真實 wiki 時也是這樣對 Claude 對話，沒有斷層
- **知識複利**：產品 wiki 透過 ingest 與 query 持續成長，新人接手時看完 wiki 就能上工
- **gap 不沉默**：查不到答案會自動記錄為 gap，避免「Claude 不會但你不知道」

---

## 疑難排解

### 安裝相關
- **`claude` 指令找不到**：重開 PowerShell / Terminal（PATH 需重新載入）。仍找不到時看 `docs/setup-{windows,mac}.md` 對應段落
- **winget 找不到**：Windows 1809+ 才內建；從 Microsoft Store 安裝「App Installer」
- **brew 指令找不到**：到 https://brew.sh 跑官方安裝指令；裝完 `eval "$(/opt/homebrew/bin/brew shellenv)"`（Apple Silicon）

### Skill 跑到一半失敗
- 跟 Claude 說「剛剛 `/xxx` 跑到一半噴錯，幫我看一下狀態並繼續」
- Claude 會用 Bash 工具掃目錄當前狀態，判斷該回退或繼續

### `~/.claude/settings.json` 壞掉
- `/setup-claude` 一定會先備份。找 `~/.claude/settings.json.bak.{timestamp}` 還原即可
- 還原後重新跑 `/setup-claude`

### 想完全重來
- 產品 wiki：直接刪掉目錄，重跑 `/init-product-wiki`
- demo-wiki：直接刪掉，重跑 `/run-example`
- `~/.claude/`：還原備份，重跑 `/setup-claude`

### Claude 不認得 bootstrap skill（/setup-claude 等）
- 確認你**在 bootstrap repo 根目錄**啟動 `claude`（不是在上層或下層目錄）
- 確認 `<bootstrap repo>/.claude/skills/` 下有 3 個目錄（setup-claude、init-product-wiki、run-example）

### Claude 不認得起手 skill（/ingest 等）
- 確認你**在產品 wiki 根目錄**啟動 `claude`（不是 bootstrap repo）
- 確認 `<產品 wiki>/.claude/skills/` 下有 4 個目錄

---

## 授權

（依公司政策填寫）
