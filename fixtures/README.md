# 電商範例假資料（Fixtures）

Step 4 walkthrough 會使用本目錄的假資料，帶同仁走一次完整工作流程。

## 主題：ShopDemo 線上購物平台（虛構）

- **產品名稱**：ShopDemo 購物平台
- **業務範圍**：會員註冊/登入、商品瀏覽與搜尋、購物車/結帳、退貨與客訴
- **重要聲明**：所有內容均為虛構，不對應任何真實公司或系統。公司名、人員、金流/物流細節皆為示意。

## 目錄

```
fixtures/
├── requirements/                            # 4 份功能需求文件（for /ingest）
│   ├── 01-會員註冊與登入需求.md
│   ├── 02-商品瀏覽與搜尋需求.md
│   ├── 03-購物車與結帳需求.md
│   └── 04-退貨與客訴需求.md
├── isms/                                    # 1 份 ISMS 變更案例（for /ingest-isms）
│   └── ISMS-115-04-購物車金額計算修正/
│       └── 申請單.md
└── diagrams/                                # 1 張 drawio 流程圖（for 參考 / /ingest-drawio）
    └── 訂單狀態流程.drawio
```

## `/run-example` 如何使用這些檔案

`/run-example` skill 會自動把本目錄複製到暫時的 `demo-wiki/raw/` 下：
- `requirements/` → `demo-wiki/raw/shopdemo-requirements/`
- `isms/` → `demo-wiki/raw/isms/`
- `diagrams/` → `demo-wiki/raw/drawio/`

然後引導你於 Claude Code 依序執行 `/ingest`、`/ingest-isms`、`/wiki-query`，觀察 `demo-wiki/wiki/` 從空白變成結構化知識。

## 不要修改 fixtures/ 下的檔案

如果想調整內容，請在 Step 4 建立的 `demo-wiki/` 下修改（那是你可以任意實驗的拋棄式環境）。fixtures/ 本身應保持乾淨，讓所有同仁的演練體驗一致。
