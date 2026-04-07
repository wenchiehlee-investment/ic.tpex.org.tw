---
source: https://raw.githubusercontent.com/wenchiehlee-investment/ic.tpex.org.tw/refs/heads/main/raw_column_definition.md
destination: https://raw.githubusercontent.com/wenchiehlee-investment/Python-Actions.GoodInfo.Analyzer/refs/heads/main/raw_column_definition.md
---

# Raw CSV Column Definitions - ic.tpex.org.tw v1.0.0
## Based on ic.tpex.org.tw Supply Chain Data

---

## raw_SupplyChain_{code}.csv (Industry Chain Company List)
**No:** 40
**Source:** `https://ic.tpex.org.tw/introduce.php?ic={chain_code}`
**Extraction Strategy:** Scrape company lists from each industry chain page, including Taiwan stocks and foreign companies.

### Column Definitions:

| Column | Position | Type | Description | Example |
|--------|----------|------|-------------|---------|
| `位置` | **Column 1** | string | Supply chain position | `上游`, `中游`, `下游` |
| `子分類` | **Column 2** | string | Subcategory name | `IP設計`, `晶圓代工` |
| `代號` | **Column 3** | string | Stock code (Taiwan or foreign) | `2330`, `ARM`, `` (empty for private) |
| `名稱` | **Column 4** | string | Company name | `台積電`, `安謀` |

---

## raw_SupplyChainMap.csv (Watchlist Company Supply Chain Map)
**No:** 41
**Source:** Derived from `raw_SupplyChain_{code}.csv` files
**Extraction Strategy:** Map watchlist companies to their industry chains with upstream/downstream relationships.

### Column Definitions:

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

---

## raw_SupplyChain-non-TWSE-TPEX.csv (Foreign Company Stock Symbol Mapping)
**No:** 42
**Source:** Manual mapping + `KNOWN_MAPPINGS` in `UpdateNonTWSE.py`
**Extraction Strategy:** Extract foreign company names from supply chain data, map to stock symbols.

### Column Definitions:

| Column | Position | Type | Description | Example |
|--------|----------|------|-------------|---------|
| `名稱` | **Column 1** | string | Company name (Chinese or English) | `安謀`, `NVIDIA` |
| `股票代號` | **Column 2** | string | Stock symbol | `ARM`, `NVDA`, `` (empty if private) |
| `交易所` | **Column 3** | string | Exchange code | `NASDAQ`, `NYSE`, `TSE`, `KRX`, `Private` |
