---
name: wiki-query
description: 從 wiki 回答使用者問題，先查 Coverage State 找入口、再讀 wiki 頁面、必要時回溯 raw，以結構化 search_trail 紀錄；查不到時依三種失敗分類動作建立/更新 raw/coverage-gaps/ 的 gap entry。使用時機：使用者提出系統相關問題、或明確呼叫 /wiki-query。
---

# wiki-query — 知識庫查詢與沉澱

## 用途

回答使用者問題，並在 Coverage State 中留下軌跡（search_trail）。查不到的內容會分類為三種 gap，自動建立或升級 gap entry（寫入 `raw/coverage-gaps/`，由下次 `/ingest` 編譯到 `wiki/coverage/topics/`），避免「靜默失敗」。

## 引用的規範

| 規範 | 路徑 | 用途 |
|------|------|------|
| CLAUDE.md「核心原則」第 6 條 | `CLAUDE.md` | 禁止直接寫入 wiki/；本 skill 是純 raw 階段 skill |
| CLAUDE.md「Coverage State 與 Gap Lifecycle」 | `CLAUDE.md` | Gap 兩條來源路徑與 status 兩階段驗證 |
| CLAUDE.md「query@v2」prompt | `CLAUDE.md` | 本 skill 的執行規範 |
| Coverage State 規格 | `wiki/coverage/coverage-state-spec.md` | wiki 端 topic 結構與 coverage 等級（只存 metadata） |
| Gap 事實來源 | `raw/coverage-gaps/gap-source-spec.md` | gap 寫入規格與生命週期（raw-only，wiki 端不鏡像） |

## 輸入

- `QUESTION`：使用者問題（自然語言）

## 執行步驟

### Step 1a：從 index.md 找候選頁面

讀 `wiki/index.md`，依問題關鍵字對應類別（Systems / Procedures / Troubleshooting / Tech Notes / Entities / Concepts），列出候選 wiki 頁。

### Step 1b：查 Coverage State

掃 `wiki/coverage/topics/`，找出與問題主題相關的 topic 檔。對每個命中的 topic：

1. 讀其 front-matter：`coverage` 等級、`wiki_pages` 清單
2. 把 `wiki_pages` 加入候選頁面（補強 Step 1a 可能漏掉的頁）
3. **讀對應的 `raw/coverage-gaps/{topic}.md`**（gap 唯一事實來源；wiki 端不存 gap entry）。若該檔存在：記下任何 `status: open` 或 `resolved_pending` 的 gap，其中 `aspect` 與本次問題相關的需特別留意（Step Verify 用）。若不存在：表示此 topic 目前無 gap

若無命中 topic：標記為「TOPIC_MISSING 候選」（Step Gap 處理）。

### Step 2：讀候選頁面 + 沿 wikilinks 擴展

讀候選 wiki 頁，沿 `[[wikilinks]]` 擴展（**最多 2 跳**，避免過度展開）。

把每次讀取記入 search_trail：
- `INDEX_LOOKUP:Procedures→hit`（從 index.md 命中分類）
- `COVERAGE_LOOKUP:example-topic→partial`（從 coverage 命中 topic）
- `PAGE_READ:procedures/某流程.md→partial`（讀了某頁，內容部分相關）
- `WIKILINK_FOLLOW:[[entities/某表]]→hit`（沿 wikilink 擴展）

### Step 3a：判斷是否需回溯 raw

若 wiki 資訊不足或有疑義，讀對應頁面 front-matter 中的 `sources`，回到 raw 層補全。

把每次 raw 讀取記入 search_trail：
- `RAW_FALLBACK:raw/<your-notes>/xxx.md→hit`
- `RAW_FALLBACK:raw/.../某筆記.md→none`

### Step 3b：量化「資訊不足」

不要憑感覺判斷。**量化定義**：

> **資訊不足** = 讀完所有候選 wiki 頁 + 1 跳 wikilink 後，對使用者問題的核心斷言仍**找不到出處**或**沒有對應段落**。

達到此條件即觸發 Step 3a 的 raw 回溯。raw 回溯後若仍無法回答 → 觸發 Step Gap。

### Step Gap：三種失敗分類動作

> **核心原則**：所有 gap 寫入都對 `raw/coverage-gaps/{topic}.md`，**絕不寫 `wiki/`**（含 `wiki/coverage/topics/`）。依 CLAUDE.md 核心原則第 6 條鐵律。wiki 端的 `## Gaps` 段由下次 `/ingest` 從 raw 編譯。

依 search_trail 結果分類：

| 等級 | 條件 | 動作 |
|------|------|------|
| `TOPIC_MISSING` | Step 1b 找不到任何相關 topic | 在 `raw/coverage-gaps/{topic}.md` 建立檔案（含 frontmatter `topic` + `wiki_topic`）並寫入一條 gap entry。**不在 wiki/coverage/topics/ 建 stub topic**——由下次 `/ingest` 處理該 raw 時建立對應的 wiki 端 stub topic |
| `DETAIL_MISSING` | topic 存在但缺特定 aspect | 開啟對應的 `raw/coverage-gaps/{topic}.md`（不存在則建檔），在末尾追加 gap entry |
| `RAW_ALSO_MISSING` | wiki + raw 都查過皆無 | 同 DETAIL_MISSING，但 `severity: high`；告知使用者「需要人類補資料」 |

每個 gap entry 必填：

```yaml
### gap-{YYYY-MM-DD}-{NNN}
- aspect: <一句話描述缺失內容>
- status: open
- severity: <low | medium | high>
- created: {today}
- query_text: "<使用者原問題>"
- search_trail: [INDEX_LOOKUP:...→..., COVERAGE_LOOKUP:...→..., PAGE_READ:...→..., RAW_FALLBACK:...→...]
- resolved_by: null
```

`gap-{YYYY-MM-DD}-{NNN}` 的 NNN 是當日序號（讀 `raw/coverage-gaps/{topic}.md` 內既有 gap 找最大值 +1）。

`raw/coverage-gaps/{topic}.md` 的 frontmatter（首次建檔時寫入）：

```yaml
---
topic: {topic-id}
wiki_topic: wiki/coverage/topics/{topic-id}.md
---
```

### Step Verify：驗證 resolved_pending

若 Step 1b 命中的 topic 有對應的 `raw/coverage-gaps/{topic}.md`，其中含 `status: resolved_pending` 的 gap，且其 aspect 與本次問題相關：

1. 完成 Step 1–3 後，**評估**本次是否成功回答了該 gap 的 query_text 涵蓋範圍
2. 若答得出 → 改 `raw/coverage-gaps/{topic}.md` 中該 gap 的 status 為 `resolved`；連續 N 次（建議 N=2）後改為 `closed`
3. 若答不出 → 改 status 回 `open`，severity 升級（low→medium、medium→high），並追加 search_trail

**所有切換都對 raw 端**；wiki 端只有 metadata（coverage level / last_ingest），不存 gap entry，無同步問題。

### Step 4：合成答案

合成答案，並在引用旁附上 **coverage level**：

```markdown
根據 [[procedures/某流程]]（coverage: partial），相關流程如下：
1. ...
2. ...

> ⚠️ 本主題覆蓋深度為 `partial`，部分細節可能尚未沉澱。
```

每個關鍵斷言都要指回 wiki 頁面或 raw 檔。**承認無知**：wiki + raw 都找不到時，明確說「目前 wiki 沒有這個資訊，需要人類補充」，並告知已建立 gap entry。

### Step 5：判斷是否需要沉澱

若在解題過程中產生了新的連結、修正了某個頁面的錯誤、或發現了一個值得獨立成頁的概念/實體：

1. **不直接寫 wiki**。先在 `raw/` 對應位置建快照（如 `raw/<your-notes>/` 或主題目錄）
2. 由人類或下次 `/ingest` 把 raw 編譯入 wiki
3. 若沉澱在 raw 對應到本次的 gap aspect，於本流程中不需自行關閉 gap，留給下次 `/ingest` 的 Step 8 處理

> **本 skill 完全不寫 `wiki/`**（含 `wiki/log.md`、`wiki/coverage/topics/`、其他編譯產物）。依 CLAUDE.md 核心原則第 6 條鐵律：wiki/ 唯一寫入入口是 `/ingest`。本 skill 是純 raw 階段 skill，所有產出（gap entry、status 切換、沉澱）都寫到 `raw/`，由下次 `/ingest` 編譯入 wiki。

## 品質守則

- **答案必須有出處**：每個關鍵斷言都要指回 wiki 頁面或 raw 檔
- **承認無知**：wiki + raw 都找不到答案時，明確說「目前 wiki 沒有這個資訊，需要人類補充」，**不要猜**
- **raw 為準**：wiki 與 raw 衝突時以 raw 為準；衝突須建議使用者下次 ingest 修正 wiki
- **search_trail 必須結構化**：`[STEP_TYPE:target→result]` 格式，避免文字描述
- **絕不寫 wiki/**：所有產出（gap entry、status 切換、沉澱）寫 `raw/`，由 `/ingest` 編譯（**核心原則第 6 條**鐵律）

## 使用範例

```
/wiki-query "ERP 資產處分後系統如何確認狀態"
/wiki-query "10F 機房年度停電演練的 SOP"

# 自然語言觸發
查一下每日結算排程
客訴系統怎麼派工
```

## 與其他 skill 的關係

- **觸發前**：使用者直接提問
- **觸發 gap 後**：本 skill 寫 `raw/coverage-gaps/{topic}.md` → 下次 `/ingest` Step 8b 切換覆蓋的 gap 為 resolved_pending、Step 8c 在 wiki 端建/更新 topic metadata（**不鏡像 gap entry**）→ 下次 `/wiki-query` 觸到本 topic → 本 skill 的 Step Verify 改 raw 端 status 為 resolved
- **沉澱時**：本 skill 寫 raw（如 `raw/<your-notes>/`），不寫 wiki；由 `/ingest` 編譯

## 版本

- **v1.0** (2026-05-13)：初版。整合 CLAUDE.md query@v2 prompt 規範 + Coverage State（Step 1b、Step 3b、Step Gap、Step Verify、Step 4 coverage level 標註）。採 raw-only gaps 設計：wiki 端 `wiki/coverage/topics/{topic}.md` 只存 metadata，gap entry 永遠去 `raw/coverage-gaps/{topic}.md` 讀寫
