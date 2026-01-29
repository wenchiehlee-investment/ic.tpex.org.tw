---
source: https://raw.githubusercontent.com/wenchiehlee-investment/ic.tpex.org.tw/refs/heads/main/raw_column_definition.md
destination: https://raw.githubusercontent.com/wenchiehlee-investment/Python-Actions.GoodInfo.Analyzer/refs/heads/main/raw_column_definition.md
---

# Raw CSV Column Definitions - ic.tpex.org.tw v1.0.0
## Based on ic.tpex.org.tw Supply Chain Data

### Version History:
- **v1.0.0** (2026-01-27): Initial definitions for supply chain data files

---

## raw_SupplyChain_{code}.csv (Industry Chain Company List)
**No:** 1-21
**Source:** `https://ic.tpex.org.tw/introduce.php?ic={chain_code}`
**Extraction Strategy:** Scrape company lists from each industry chain page, including Taiwan stocks and foreign companies.

### Available Chain Codes:
| Code | Name |
|------|------|
| F000 | 電腦及週邊設備 |
| I000 | 通信網路 |
| 5300 | 人工智慧 |
| 5800 | 運動科技 |
| D000 | 半導體 |
| U000 | 金融 |
| T000 | 交通運輸及航運 |
| B000 | 休閒娛樂 |
| R000 | 軟體服務 |
| C100 | 製藥 |
| 5500 | 資通訊安全 |
| V000 | 貿易百貨 |
| R300 | 電子商務 |
| 5200 | 金融科技 |
| L000 | 印刷電路板 |
| C200 | 醫療器材 |
| M000 | 食品 |
| X000 | 其他 |
| 6000 | 自動化 |
| G000 | 平面顯示器 |
| P000 | 電機機械 |

### Columns

| Column | Position | Type | Description | Example |
|--------|----------|------|-------------|---------|
| `位置` | **Column 1** | string | Supply chain position | `上游`, `中游`, `下游` |
| `子分類` | **Column 2** | string | Subcategory name | `IP設計`, `晶圓代工` |
| `代號` | **Column 3** | string | Stock code (Taiwan or foreign) | `2330`, `ARM`, `` (empty for private) |
| `名稱` | **Column 4** | string | Company name | `台積電`, `安謀` |

### Notes:
- Taiwan stocks have numeric codes (e.g., `2330`)
- Foreign companies use stock symbols from `raw_SupplyChain-non-TWSE-TPEX.csv` (e.g., `ARM`, `NVDA`)
- Private or unlisted companies have empty `代號`

---

## raw_SupplyChainMap.csv (Watchlist Company Supply Chain Map)
**No:** 22
**Source:** Derived from `raw_SupplyChain_{code}.csv` files
**Extraction Strategy:** Map watchlist companies to their industry chains with upstream/downstream relationships.

### Columns

| Column | Position | Type | Description | Example |
|--------|----------|------|-------------|---------|
| `代號` | **Column 1** | string | Taiwan stock code | `2330` |
| `名稱` | **Column 2** | string | Company name | `台積電` |
| `產業鏈代碼` | **Column 3** | string | Industry chain code | `D000` |
| `產業鏈名稱` | **Column 4** | string | Industry chain name | `半導體` |
| `位置` | **Column 5** | string | Position(s) in chain | `上游`, `中游/下游` |
| `子分類` | **Column 6** | string | Subcategory(ies) | `晶圓代工;先進封裝` |
| `上游公司` | **Column 7** | string | Upstream companies | `2454\|聯發科;3034\|聯詠` |
| `下游公司` | **Column 8** | string | Downstream companies | `2317\|鴻海;2382\|廣達` |

### Notes:
- Multiple positions separated by `/`
- Multiple subcategories separated by `;`
- Upstream/downstream companies formatted as `代號|名稱` pairs, separated by `;`
- Limited to 20 companies per direction

---

## raw_SupplyChain-non-TWSE-TPEX.csv (Foreign Company Stock Symbol Mapping)
**No:** 23
**Source:** Manual mapping + `KNOWN_MAPPINGS` in `UpdateNonTWSE.py`
**Extraction Strategy:** Extract foreign company names from supply chain data, map to stock symbols.

### Columns

| Column | Position | Type | Description | Example |
|--------|----------|------|-------------|---------|
| `名稱` | **Column 1** | string | Company name (Chinese or English) | `安謀`, `NVIDIA` |
| `股票代號` | **Column 2** | string | Stock symbol | `ARM`, `NVDA`, `` (empty if private) |
| `交易所` | **Column 3** | string | Exchange code | `NASDAQ`, `NYSE`, `TSE`, `KRX`, `Private` |

### Exchange Codes:
| Code | Description |
|------|-------------|
| NASDAQ | US NASDAQ |
| NYSE | US New York Stock Exchange |
| OTC | US Over-the-Counter |
| TSE | Tokyo Stock Exchange (Japan) |
| KRX | Korea Exchange |
| HKEX | Hong Kong Stock Exchange |
| SSE | Shanghai Stock Exchange |
| SZSE | Shenzhen Stock Exchange |
| Private | Private company (not publicly traded) |
| Acquired | Company has been acquired |

### Notes:
- Empty `股票代號` indicates private or unlisted company
- Mapping maintained in `KNOWN_MAPPINGS` dictionary in `UpdateNonTWSE.py`
