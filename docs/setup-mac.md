# macOS 安裝指引

> 這是整個 bootstrap 流程**唯一需要你手動敲指令的部分**。裝完 Git 與 Claude Code 後，其他設定（`~/.claude/`、產品 wiki、demo walkthrough）都會在 Claude Code 裡用自然語言完成。

## 前置需求

- macOS（建議 Ventura 13 以上）
- [Homebrew](https://brew.sh)（若未裝，到 brew.sh 看官方一行安裝指令）
- 網路連線

## Step 1：開 Terminal，裝 Git 與 Claude Code

```bash
brew install git
brew install anthropic/anthropic/claude-code
```

驗證：

```bash
git --version          # 應回傳 git version 2.x.x
claude --version       # 應回傳 Claude Code 版本
```

兩個指令都有版本回應即成功。

## Step 2：Clone bootstrap repo，進入並啟動 Claude

挑一個你慣用的工作目錄（例：`~/Work/`），執行：

```bash
mkdir -p ~/Work && cd ~/Work
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

```bash
brew install node
brew install python@3.12

pip3 install markitdown pymupdf
```

VS Code 編輯器（**選擇性**，Claude Code 也可獨立用）：

```bash
brew install --cask visual-studio-code
```

## 疑難排解

- **brew 指令找不到**：先到 https://brew.sh 跑官方安裝指令；若已裝但 shell 不認得，把 `eval "$(/opt/homebrew/bin/brew shellenv)"` 加進 `~/.zshrc`（Apple Silicon）或 `eval "$(/usr/local/bin/brew shellenv)"`（Intel Mac）
- **`claude` 找不到**：開新 Terminal 視窗（PATH 需重新載入）。仍找不到的話，跑 `which claude` 看路徑、確認 brew 已正確安裝 `anthropic/anthropic/claude-code`
- **既有 ~/.claude/settings.json 怕被破壞**：`/setup-claude` 一定會先備份；merge 規則是「只補缺漏 key、保留你的原值、陣列取聯集」，不會覆寫你的設定
- **公司管控環境**：若 brew 被擋，洽 IT 或用內部鏡像；Claude Code 也提供 npm 安裝方式（`npm install -g @anthropic-ai/claude-code`），但需要先有 Node.js
