---
name: setup-claude
description: 替學員建立個人層級 ~/.claude/ 共用環境。讀本 repo 的 templates/claude-settings/settings.json.template，與既有 ~/.claude/settings.json 做 deep merge（保留使用者原值、補上缺漏 key、陣列取聯集）。目前範本最小化——只含核心安全規則，不裝 plugin。使用時機：學員 clone bootstrap repo 後第一次跟 Claude 對話、或明確說「幫我設定 ~/.claude/」。
---

# setup-claude — 建立個人層級 `~/.claude/` 共用環境

## 用途

把團隊共用的核心安全規則（`permissions.deny` / `permissions.ask`）安裝到學員的個人環境，**不覆蓋學員原有設定**。

這是 bootstrap 流程的第二步（第一步是裝 Git + Claude Code，由 [`docs/setup-windows.md`](../../../docs/setup-windows.md) / [`docs/setup-mac.md`](../../../docs/setup-mac.md) 指引完成）。

**範本最小化原則**：本 skill 只 merge 核心安全規則，**不裝任何 plugin**。學員想用 plugin（superpowers、commit-commands、skill-creator、claude-mem 等）可在熟悉工作流後自行決定何時安裝，避免「第一次體驗就被 plugin 初始化（如 claude-mem 的 API key 設定）卡住」。

## 觸發條件

- 學員說「幫我設定 ~/.claude/」「設定 Claude 共用環境」「跑 setup-claude」
- 明確呼叫 `/setup-claude`

## 範本來源

讀本 repo 的 `templates/claude-settings/settings.json.template`，內含：

| 區塊 | 內容 |
|---|---|
| `permissions.deny` | 9 條破壞性指令（rm -rf、force push、reset --hard…） |
| `permissions.ask` | 8 條須確認指令（rm、git checkout --、docker rm…） |

## 執行步驟

### Step 0：前置檢查

1. **確認 claude CLI 已安裝**：跑 `claude --version`。若失敗 → 告訴學員「請先依 `docs/setup-windows.md` 或 `docs/setup-mac.md` 裝 Git 與 Claude Code CLI 後重試」並中止
2. **確認 `~/.claude/` 目錄存在**：不存在則建立（用 Bash 工具，跨平台都用 `mkdir -p`）
3. **找到範本路徑**：`templates/claude-settings/settings.json.template`（相對本 bootstrap repo 根目錄）

### Step 1：備份既有 settings.json

若 `~/.claude/settings.json` 已存在：
1. 用 timestamp 命名備份：`settings.json.bak.YYYYMMDD-HHmmss`
2. `cp` 過去（用 Bash 工具）
3. 告知學員備份位置

若不存在：略過此步，後續直接建立全新檔案。

### Step 2：讀兩份 JSON

1. 讀 `templates/claude-settings/settings.json.template`（用 Read 工具）→ 範本 JSON
2. 讀 `~/.claude/settings.json`（若存在）→ 現有 JSON。**若解析失敗**：告訴學員「現有 settings.json 格式錯誤」並列印錯誤訊息，要求學員手動修復或還原備份後重試，中止 skill

### Step 3：Deep Merge

依以下規則 merge 範本進現有設定：

| 情況 | 動作 |
|---|---|
| 現有 JSON 沒有該 key | **新增** key 與範本值 |
| 雙方都是 object | **遞迴 merge** 子節點 |
| 雙方都是 array | **取聯集去重**（以字串形式比對） |
| 雙方都存在且為 primitive（字串/數字/布林） | **保留現有值**，不覆寫 |

實作要點：
- **絕不覆寫學員原有設定**——這是核心規則
- 在心智裡列出所有變動（新增了哪些 key、哪個 array 多了幾筆），最後給學員看
- 用 Edit 或 Write 工具寫回 `~/.claude/settings.json`，JSON 格式化（縮排 2 空格、UTF-8 無 BOM）

### Step 4：顯示變動摘要

格式範例：
```
=== Merge 結果 ===
- 新增 key: permissions
  permissions -> 新增 key: deny
  permissions -> 新增 key: ask
- 陣列 permissions.deny 新增 9 筆
- 陣列 permissions.ask 新增 8 筆
```

若無異動（學員設定已涵蓋範本）：明確說明「無異動，你的設定已涵蓋範本所需所有 key」。

### Step 5：完成提示

告訴學員：

```
=== 完成 ===

~/.claude/settings.json 已 merge 完成。
危險指令（rm -rf、force push、reset --hard…）現在會被阻擋；
需確認的指令（rm、git checkout --、docker rm…）會先問你。

下一步：跟我說「幫我建立產品 wiki」或執行 /init-product-wiki。
```

**注意**：本 skill **不安裝任何 plugin**（保持第一次體驗最小化）。若日後想加 plugin（superpowers、commit-commands、skill-creator、claude-mem 等），可直接跟 Claude 說「幫我裝 XXX plugin」由 Claude 引導。

## 自檢

- [ ] `~/.claude/settings.json` 存在且為合法 JSON
- [ ] `permissions.deny` 含本範本 9 條規則
- [ ] `permissions.ask` 含本範本 8 條規則
- [ ] 學員原有 key 沒被覆寫（若 Step 1 有備份，可在備份留存的前提下放心執行）

## 品質守則

- **不覆寫使用者原值**：這是鐵律。merge 演算法的設計就是為了 idempotent + 安全
- **備份優先**：即使學員說「不用備份」，仍要備份（破壞性操作不可逆）
- **明確列出變動**：學員看完應該能講出「我這次新增了哪幾個 key」
- **失敗即停**：JSON 解析失敗、寫檔失敗都要中止，不嘗試半套修補

## 跨平台注意

- Windows：`~` 對應 `$env:USERPROFILE`；用 Bash 工具時 Git Bash 提供 `~` 展開，可直接寫 `~/.claude/settings.json`
- Mac/Linux：`~` 是 `$HOME`，無需特殊處理
- 使用 Read / Write / Edit 工具讀寫 settings.json 時，傳入絕對路徑（讓 Bash 工具回報 `echo $HOME` 取得實際路徑後組裝）

## 版本

- **v1.1** (2026-05-13)：範本最小化——移除 plugin 與 marketplace 條目，只 merge 核心安全規則（permissions.deny / permissions.ask）。理由：plugin 安裝（特別是 claude-mem 的 API key 與 DB 初始化）會把學員第一次體驗變複雜；學員熟悉工作流後可自行決定何時加 plugin
- v1.0 (2026-05-13)：初版。取代 `scripts/2-setup-claude.ps1`。改由 Claude 用 Read/Write/Bash 工具完成 deep merge，跨平台一致
