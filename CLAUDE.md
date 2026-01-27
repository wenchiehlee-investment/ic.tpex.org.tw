# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 專案概述

台灣股市觀察名單下載工具 - 從 GoPublic GitHub 儲存庫下載股票觀察清單並轉換為 CSV 格式。

## 執行指令

```bash
# 下載觀察名單與專注名單
python3 Get觀察名單.py

# 下載產業鏈資料（21 個產業鏈）
python3 GetSupplyChain.py

# 更新外國企業股票代號對照表
python3 UpdateNonTWSE.py

# 安裝相依套件
pip install requests beautifulsoup4 yfinance
```

## 架構說明

### Get觀察名單.py - 下載股票清單
- `download_file()` - HTTP 下載、UTF-8 編碼、TAIEX 注入
- 來源: `https://raw.githubusercontent.com/wenchiehlee/GoPublic/refs/heads/main`
- 輸出: `StockID_TWSE_TPEX.csv`, `StockID_TWSE_TPEX_focus.csv`

### GetSupplyChain.py - 產業鏈資料爬取
- `get_chain_data()` - 爬取產業鏈的子分類與公司清單
- `build_supply_chain_map()` - 建立觀察名單公司的產業鏈地圖
- 來源: `https://ic.tpex.org.tw/introduce.php?ic={chain_code}`
- 涵蓋 21 個產業鏈：F000(電腦及週邊設備)、I000(通信網路)、5300(人工智慧)、5800(運動科技)、D000(半導體)、U000(金融)、T000(交通運輸及航運)、B000(休閒娛樂)、R000(軟體服務)、C100(製藥)、5500(資通訊安全)、V000(貿易百貨)、R300(電子商務)、5200(金融科技)、L000(印刷電路板)、C200(醫療器材)、M000(食品)、X000(其他)、6000(自動化)、G000(平面顯示器)、P000(電機機械)
- 輸出至 `data/` 資料夾:
  - `raw_SupplyChain_{code}.csv` - 各產業鏈資料，格式: `位置,子分類,代號,名稱`
  - `raw_SupplyChainMap.csv` - 觀察名單公司的產業鏈地圖
    - 格式: `代號,名稱,產業鏈代碼,產業鏈名稱,位置,子分類,上游公司,下游公司`

### UpdateNonTWSE.py - 外國企業股票代號對照表
- `extract_foreign_companies()` - 從產業鏈 CSV 擷取外國企業名稱
- `KNOWN_MAPPINGS` - 手動維護的常見外國企業對照表（約 130 家）
- 輸出: `data/raw_non-TWSE-TPEX.csv` - 格式: `名稱,股票代號,交易所`
- GetSupplyChain.py 會自動載入此對照表填入外國企業股票代號

### .github/workflows/update-supply-chain.yml - GitHub Actions 自動更新
- 每週日 00:00 UTC (台灣時間 08:00) 自動執行
- 支援手動觸發 (workflow_dispatch)
- 自動提交並推送更新的資料

## 技術細節

- Python 3 搭配 `requests` 及 `beautifulsoup4`
- UTF-8 編碼處理繁體中文
- HTTP 逾時：30 秒，請求間隔 1 秒
- 冪等操作 - 可安全重複執行
