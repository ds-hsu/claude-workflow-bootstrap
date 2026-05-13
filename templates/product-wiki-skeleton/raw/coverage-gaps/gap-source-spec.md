# Gap 事實來源規格 — `raw/coverage-gaps/`

> **這個目錄是什麼**：`{{PRODUCT_DISPLAY_NAME}}` 知識缺口（gap）的**唯一事實來源**。每個檔案對應 `wiki/coverage/topics/{topic}.md` 一個 topic，列出該 topic 上的所有 gap entry。
>
> **誰寫入**：`/wiki-query` Step Gap、`/ingest` Step 8a（從 `raw/isms/{folder}/{folder}-分析.md` 收割的 gap-candidate 提升為正式 gap）、`/ingest` Step 8b（切換覆蓋的 gap 為 `resolved_pending`）、`/wiki-query` Step Verify（切換 `resolved_pending` → `resolved` / `reopened`）。
>
> **誰讀取**：`/wiki-query` Step 1b 與 Step Verify、`/ingest` Step 8b。
>
> **wiki 端是否有鏡像？** **否**。本設計採 raw-only：`wiki/coverage/topics/{topic}.md` 只存 coverage metadata，**不鏡像 gap entry**。gap 永遠只有 raw 端這一份。
>
> **為何 gap 不直接寫 wiki？** 依 CLAUDE.md 核心原則第 6 條「禁止直接寫入 wiki/」，`/wiki-query` 等查詢 skill 不得直接寫 `wiki/`；gap 是查詢過程的產出，必須先寫 raw。即使日後想讓人類在 Obsidian 看 gap，也是「點 pointer 跳檔」，不開鏡像。

## 結構

```
raw/coverage-gaps/
├── gap-source-spec.md               ← 本檔
├── {topic-id}.md                    ← 對應 wiki/coverage/topics/{topic-id}.md
└── ...
```

每個 topic 一個 `.md` 檔。檔名（去除 `.md`）= topic id（kebab-case）= 對應的 `wiki/coverage/topics/{topic}.md` 檔名。

## 檔案格式

```yaml
---
topic: example-topic
wiki_topic: wiki/coverage/topics/example-topic.md
---

# Coverage Gaps — example-topic

### gap-2026-05-13-001
- aspect: 某面向尚未沉澱
- status: open
- severity: high
- created: 2026-05-13
- query_text: "<使用者原問題>"
- search_trail: [INDEX_LOOKUP:Procedures→hit, COVERAGE_LOOKUP:example-topic→partial, PAGE_READ:procedures/某流程.md→partial, RAW_FALLBACK:raw/.../某筆記.md→none]
- resolved_by: null

### gap-2026-05-13-002
- aspect: ...
...
```

## Front-matter 欄位

| 欄位 | 必填 | 規則 |
|------|------|------|
| `topic` | ✅ | topic id（kebab-case），與檔名一致 |
| `wiki_topic` | ✅ | 對應的 wiki 端 topic 路徑（相對於專案根目錄） |

## Gap entry 必填欄位

| 欄位 | 必填 | 規則 |
|------|------|------|
| `aspect` | ✅ | 一句話描述缺失內容 |
| `status` | ✅ | enum：open / acknowledged / resolved_pending / resolved / closed / reopened |
| `severity` | ✅ | enum：low / medium / high |
| `created` | ✅ | YYYY-MM-DD |
| `query_text` | ✅ | 觸發此 gap 的原始問題（或匯入時的標記） |
| `search_trail` | ✅ | 陣列，結構化格式 `[STEP_TYPE:target→result]` |
| `resolved_by` | ✅ | null 或 wiki 頁面路徑（`resolved_pending` 起填寫） |

## search_trail 結構化格式

每個元素：`STEP_TYPE:target→result`

| STEP_TYPE | target | result |
|-----------|--------|--------|
| `INDEX_LOOKUP` | 類別名（如 `Procedures`） | `hit` / `miss` |
| `COVERAGE_LOOKUP` | topic id | coverage 等級或 `miss` |
| `PAGE_READ` | wiki 頁路徑 | `hit` / `partial` / `miss` |
| `WIKILINK_FOLLOW` | `[[目標頁]]` | `hit` / `miss` |
| `RAW_FALLBACK` | raw 檔路徑 | `hit` / `partial` / `none` |
| `INGEST_ISMS_DETECT` | ISMS 資料夾名 | `discovered` |

## Gap 生命週期（兩階段驗證）

```
OPEN ──→ ACKNOWLEDGED ──→ RESOLVED_PENDING ──→ RESOLVED ──→ CLOSED
 │              │                  │ (ingest 寫入       │
 │              │                  │  時自動切換)        │
 │              │                  ↓                    ↓
 │              │              下次 query        驗證通過數次後
 │              │              觸到此 topic
 │              │                  │
 │              │                  ├─ 答得出 → RESOLVED → CLOSED
 │              │                  └─ 答不出 → REOPENED（severity 升級）
 └──────────────┴───── REOPENED ←──┘
```

| status | 含義 | 切換者 |
|--------|------|--------|
| `open` | 新發現的缺口 | `/wiki-query` Step Gap |
| `acknowledged` | 人類已確認此為缺口（非誤判）| 手動編輯 |
| `resolved_pending` | `/ingest` 認為已寫入但**未驗證** | `/ingest` Step 8b |
| `resolved` | `/wiki-query` 實際驗證可回答 | `/wiki-query` Step Verify |
| `closed` | 連續 N 次（建議 N=2）驗證通過 | `/wiki-query` Step Verify |
| `reopened` | 驗證失敗或重新發現缺口 | `/wiki-query` Step Verify |

**關鍵：兩階段驗證**——`/ingest` 不直接 `closed`，必須由實際 query 驗證通過才能切。避免 LLM 主觀判斷誤關。

## 寫入規則

1. **`/wiki-query` Step Gap**：找不到答案時，依失敗分類（TOPIC_MISSING / DETAIL_MISSING / RAW_ALSO_MISSING）建立或追加 gap entry
   - 檔不存在 → 新建（含 frontmatter）
   - 檔存在 → 在末尾追加 entry，不刪改現有 entry
2. **`/ingest` Step 8a**：從 `raw/isms/*/分析.md` 收割 gap-candidate 後寫入此處
3. **`/ingest` Step 8b**：本次 ingest 寫入內容覆蓋了某 gap 的 aspect → 改其 status 為 `resolved_pending`，填入 `resolved_by`
4. **`/wiki-query` Step Verify**：觸到 `resolved_pending` 的 gap，答得出 → `resolved`（連續 N 次後 `closed`）；答不出 → 回 `open` + 升 severity
5. **絕對不得手動編輯歷史 gap entry** 的 status / severity — 一律由結構化路徑切換

## Gap 兩條來源路徑

```
路徑 A：即時建立（query-time discovery）
─────────────────────────────────────
使用者提問 → /wiki-query 查不到 → 寫 raw/coverage-gaps/{topic}.md

路徑 B：分析中偵測（analysis-time discovery）
─────────────────────────────────────
ISMS 變更單 → /ingest-isms Step 7 讀 wiki 做分析
            → Step 7b 發現盲點
            → 寫 gap-candidate 到 raw/isms/{folder}/{folder}-分析.md ## 知識盲點
            → 下次 /ingest Step 8a 收割 → 寫 raw/coverage-gaps/{topic}.md（提升為正式 gap）
```

兩條路徑都先寫 raw — 這是「禁止直接寫入 wiki/」鐵律的延伸：`/wiki-query` 與 `/ingest-isms` 都是 raw 階段 skill。

## 設計原則

- **單一事實來源**：本目錄是 gap 的唯一寫入位置（且 wiki 端不鏡像）
- **append-only**：gap entry 寫入後**不可手動編輯**；status 切換經結構化路徑（query / ingest）
- **kebab-case 檔名**：與 `wiki/coverage/topics/` 嚴格對應
