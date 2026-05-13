> snapshot: {SNAPSHOT_DATE}
> source: {ORIGINAL_FILE_PATH}
> converted_by: markitdown (text layer) + manual transcription of embedded screenshots (if any)
> form_template: ISMS-L4-69 {TEMPLATE_VERSION}
> project_code: {PROJECT_CODE_IF_ANY}

# 軟體變更申請與處理紀錄單 — {標題}

## 基本資料

| 欄位 | 值 |
|---|---|
| 公司 | {COMPANY_NAME} |
| 文件編號（表單類別）| ISMS-L4-69 |
| 紀錄編號 | {RECORD_NUMBER} |
| 申請日 | {民國年} 年 {月} 月 {日} 日（{WESTERN_DATE}）|
| 表單版本 | {TEMPLATE_VERSION} |

## 一、變更申請

### 申請變更項目
**{ITEM_TITLE}**

### 變更等級（單選）
{LEVEL_CHECKBOXES}

### 變更種類（複選）
{TYPE_CHECKBOXES}

### 變更項目類別（複選）
{CATEGORY_CHECKBOXES}

### 變更需求 — 變更原因及內容說明
{REQUIREMENT_DESCRIPTION}

### 資訊安全評估（申請階段）
{SECURITY_EVAL_APPLICATION}

### 申請簽章
- **申請人員**：{APPLICANT_NAME}（{TIMESTAMP}）
- **權責主管**：{APPLICANT_MANAGER}（{TIMESTAMP}）

---

## 二、開發評估與執行

### 變更項目類別
{DEV_CATEGORY_CHECKBOXES}

### 是否需公告停止服務
{SERVICE_STOP}

### 風險評估（若為 v1.x 範本）
{RISK_ASSESSMENT}

### 資訊安全評估（開發階段）
{SECURITY_EVAL_DEV}

### 所需測試
{TEST_TYPES}

### 變更評估
{EVALUATION_TEXT}

#### 具體 SQL 範例（from 截圖，若有）
```sql
{SQL_FROM_SCREENSHOT}
```

#### UI 畫面（from 截圖，若有）
{UI_TABLE}

### 評估簽章
- **評估人員**：{EVALUATOR}（{TIMESTAMP}）
- **權責主管**：{EVALUATOR_MANAGER}（{TIMESTAMP}）

---

## 變更處理（Backlog 樹）

```
{BACKLOG_TREE}
```

### 執行簽章
- **執行人員**：{EXECUTOR}（{TIMESTAMP}）
- **權責主管**：{EXECUTOR_MANAGER}（{TIMESTAMP}）

---

## 測試結果

{TEST_RESULT}

### 測試佐證截圖（若有）
{TEST_EVIDENCE}

### 測試簽章
- **測試人員**：{TESTER}（{TIMESTAMP}）
- **權責主管**：{TESTER_MANAGER}（{TIMESTAMP}）

---

## 程式版更紀錄（Release Notes，若有）

**所屬 Release**：{RELEASE_NAME}

**Product**：{PRODUCT_NAME}

{RELEASE_NOTES_TABLE}

### 版控簽章
- **版控人員**：{VERSION_CONTROLLER}（{TIMESTAMP}）
- **權責主管**：{VC_MANAGER}（{TIMESTAMP}）

---

## 三、驗收及確認

### 驗收及確認紀錄
{ACCEPTANCE_RECORD}

### 確認簽章
- **確認人員**：{CONFIRMER}（{TIMESTAMP}）
- **權責主管**：{CONFIRMER_MANAGER}（{TIMESTAMP}）

---

## 教育訓練

{TRAINING_NEEDED}

---

## 流程時間線（從簽名時間戳整理）

| 日期 | 動作 | 人員 |
|---|---|---|
{TIMELINE_ROWS}

**從申請到結案歷時約 {DURATION_DAYS} 天**
