# Windows 安裝指引

> 這是整個 bootstrap 流程**唯一需要你手動敲指令的部分**。裝完 Git 與 Claude Code 後，其他設定（`~/.claude/`、產品 wiki、demo walkthrough）都會在 Claude Code 裡用自然語言完成。

## 前置需求

- Windows 10 / 11
- PowerShell（系統內建）
- 可使用 `winget`（Windows 10 1809+ 內建。若沒有，請從 Microsoft Store 安裝「App Installer」）
- 網路連線

## Step 1：開 PowerShell，裝 Git 與 Claude Code

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

兩個指令都有版本回應即成功。

## Step 2：Clone bootstrap repo，進入並啟動 Claude

挑一個你慣用的工作目錄（例：`C:\Work\`），執行：

```powershell
cd C:\Work\
git clone <bootstrap-repo-url> claude-workflow-bootstrap
cd claude-workflow-bootstrap
claude
```

Claude Code 啟動後，輸入：

```
幫我設定 ~/.claude/ 共用環境
```

或直接呼叫：

```
/setup-claude
```

Claude 會引導你完成 `~/.claude/settings.json` 的核心安全規則 merge（目前範本最小化，不裝 plugin）。

## Step 3：建立你的產品 wiki

設定完 `~/.claude/` 後，在 bootstrap repo 內再次啟動 `claude`（若要讓設定立即生效，可關閉視窗重開），跟它說：

```
幫我建立產品 wiki，產品代號叫 <你的產品代號>
```

或：

```
/init-product-wiki
```

Claude 會互動問你產品代號、wiki 目標路徑、顯示名稱，然後幫你建好骨架 + 起手 skill + git init。

## Step 4（選擇性）：跑電商範例

若你想先看完整工作流程怎麼跑，再開始用真實文件，在 bootstrap repo 內跟 Claude 說：

```
跑一次電商範例 walkthrough
```

或：

```
/run-example
```

Claude 會建立拋棄式 `demo-wiki/`，引導你親手體驗從原始文件到結構化知識的轉換。

## 其他選擇性工具

你的產品 wiki 若需要轉 PDF/DOCX 為 markdown（`/ingest-isms` 會用到），可以裝：

```powershell
winget install --id OpenJS.NodeJS.LTS --exact --silent `
  --accept-package-agreements --accept-source-agreements
winget install --id Python.Python.3.12 --exact --silent `
  --accept-package-agreements --accept-source-agreements

# Python 套件
pip install markitdown pymupdf
```

VS Code 編輯器（**選擇性**，Claude Code 也可獨立用）：

```powershell
winget install --id Microsoft.VisualStudioCode --exact --silent `
  --accept-package-agreements --accept-source-agreements
```

## 疑難排解

- **winget 找不到**：Windows 1809+ 才內建。請從 Microsoft Store 安裝「App Installer」
- **公司網路阻擋 winget 來源**：洽 IT 開通，或改用公司內部套件鏡像
- **`claude` 找不到**：重開 PowerShell，PATH 需要重新載入
- **Git Bash vs PowerShell**：本文檔指令以 PowerShell 為主；若你習慣 Git Bash，多數指令也可直接跑（除了 winget 那段）
- **既有 ~/.claude/settings.json 怕被破壞**：`/setup-claude` 一定會先備份；merge 規則是「只補缺漏 key、保留你的原值、陣列取聯集」，不會覆寫你的設定
