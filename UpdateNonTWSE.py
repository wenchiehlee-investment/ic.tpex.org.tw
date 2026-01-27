#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UpdateNonTWSE.py
Version: 1.0
Description: Updates non-TWSE-TPEX.csv with stock symbols from Yahoo Finance API
"""

import csv
import os
import sys
import time
import re
from datetime import datetime

try:
    import yfinance as yf
except ImportError:
    print("請先安裝 yfinance: pip install yfinance")
    sys.exit(1)

# Known company mappings (name -> (symbol, exchange))
# This is a manually maintained list for common companies
KNOWN_MAPPINGS = {
    # US Tech Giants
    'Google': ('GOOGL', 'NASDAQ'),
    '微軟': ('MSFT', 'NASDAQ'),
    '蘋果': ('AAPL', 'NASDAQ'),
    '亞馬遜': ('AMZN', 'NASDAQ'),
    '亞馬遜網路服務公司': ('AMZN', 'NASDAQ'),
    'Meta': ('META', 'NASDAQ'),
    '輝達': ('NVDA', 'NASDAQ'),
    'OpenAI': ('', 'Private'),
    'Anthropic': ('', 'Private'),

    # Semiconductors
    '安謀': ('ARM', 'NASDAQ'),
    '益華': ('CDNS', 'NASDAQ'),
    '新思科技': ('SNPS', 'NASDAQ'),
    'Imagination': ('', 'Private'),
    '英特爾': ('INTC', 'NASDAQ'),
    '超微半導體': ('AMD', 'NASDAQ'),
    '高通': ('QCOM', 'NASDAQ'),
    '德州儀器': ('TXN', 'NASDAQ'),
    '博通': ('AVGO', 'NASDAQ'),
    '恩智浦半導體': ('NXPI', 'NASDAQ'),
    '意法半導體': ('STM', 'NYSE'),
    '美光': ('MU', 'NASDAQ'),
    '應用材料': ('AMAT', 'NASDAQ'),
    '科林研發': ('LRCX', 'NASDAQ'),
    '科磊': ('KLAC', 'NASDAQ'),
    '艾司摩爾': ('ASML', 'NASDAQ'),
    '格羅方德': ('GFS', 'NASDAQ'),
    '安華高科技': ('AVGO', 'NASDAQ'),
    '亞德諾半導體': ('ADI', 'NASDAQ'),
    '邁威爾': ('MRVL', 'NASDAQ'),
    '慧榮科技股份有限公司': ('SIMO', 'NASDAQ'),

    # Japanese Companies
    '三星電子': ('005930.KS', 'KRX'),
    '三星半導體': ('005930.KS', 'KRX'),
    '三星SDI': ('006400.KS', 'KRX'),
    '三星顯示': ('005930.KS', 'KRX'),
    'SK海力士': ('000660.KS', 'KRX'),
    'LG化學': ('051910.KS', 'KRX'),
    'LG顯示': ('034220.KS', 'KRX'),
    'LG': ('066570.KS', 'KRX'),
    '京瓷': ('6971.T', 'TSE'),
    '村田製作所': ('6981.T', 'TSE'),
    '日立': ('6501.T', 'TSE'),
    '松下電器': ('6752.T', 'TSE'),
    '索尼': ('6758.T', 'TSE'),
    '東京電力': ('9501.T', 'TSE'),
    '信越化學': ('4063.T', 'TSE'),
    '瑞薩電子': ('6723.T', 'TSE'),
    '太陽誘電': ('6976.T', 'TSE'),
    'TDK Electronics': ('6762.T', 'TSE'),
    '日亞化': ('', 'Private'),
    'Canon': ('7751.T', 'TSE'),
    '尼康株式會社': ('7731.T', 'TSE'),
    '歐姆龍': ('6645.T', 'TSE'),
    'Advantest': ('6857.T', 'TSE'),
    '小松製作所': ('6301.T', 'TSE'),
    '三菱電機': ('6503.T', 'TSE'),
    '三菱重工': ('7011.T', 'TSE'),
    '富士電機': ('6504.T', 'TSE'),
    '精工愛普生': ('6724.T', 'TSE'),
    '大金': ('6367.T', 'TSE'),
    '牧田日本': ('6586.T', 'TSE'),

    # Chinese Companies
    '阿里巴巴集團': ('BABA', 'NYSE'),
    '華為': ('', 'Private'),
    '中芯國際': ('0981.HK', 'HKEX'),
    '京東方': ('000725.SZ', 'SZSE'),
    '海康威視': ('002415.SZ', 'SZSE'),
    '海思半導體': ('', 'Private'),
    '比亞迪': ('1211.HK', 'HKEX'),
    '聯想': ('0992.HK', 'HKEX'),
    '中興': ('0763.HK', 'HKEX'),
    '匯頂科技': ('603160.SS', 'SSE'),
    '幣安': ('', 'Private'),
    '支付寶': ('', 'Private'),
    '眾安': ('6060.HK', 'HKEX'),

    # US Tech & Others
    'Paypal': ('PYPL', 'NASDAQ'),
    'Stripe': ('', 'Private'),
    'Coinbase': ('COIN', 'NASDAQ'),
    'Robinhood': ('HOOD', 'NASDAQ'),
    'Airbnb': ('ABNB', 'NASDAQ'),
    '網飛': ('NFLX', 'NASDAQ'),
    'Dropbox': ('DBX', 'NASDAQ'),
    'VMware': ('VMW', 'NYSE'),
    'Splunk': ('', 'Acquired'),
    '思科系統': ('CSCO', 'NASDAQ'),
    '甲骨文': ('ORCL', 'NYSE'),
    '思愛普': ('SAP', 'NYSE'),
    '戴爾': ('DELL', 'NYSE'),
    '惠普': ('HPQ', 'NYSE'),
    'HPE': ('HPE', 'NYSE'),

    # Security
    'CrowdStrike': ('CRWD', 'NASDAQ'),
    'Fortinet': ('FTNT', 'NASDAQ'),
    'Palo Alto Networks': ('PANW', 'NASDAQ'),
    'Zscaler': ('ZS', 'NASDAQ'),
    'Okta': ('OKTA', 'NASDAQ'),
    '趨勢科技': ('4704.T', 'TSE'),

    # Industrial
    'ABB': ('ABB', 'NYSE'),
    '西門子': ('SIEGY', 'OTC'),
    'Honeywell': ('HON', 'NASDAQ'),
    '艾默生電氣公司': ('EMR', 'NYSE'),
    'Eaton Corporation Plc': ('ETN', 'NYSE'),
    'TE Connectivity': ('TEL', 'NYSE'),
    '洛克威爾自動化': ('ROK', 'NYSE'),

    # Healthcare & Pharma
    '輝瑞大藥廠': ('PFE', 'NYSE'),
    '羅氏大藥廠': ('RHHBY', 'OTC'),
    '諾華': ('NVS', 'NYSE'),
    '嬌生': ('JNJ', 'NYSE'),
    '默克集團': ('MRK', 'NYSE'),
    '拜耳': ('BAYRY', 'OTC'),
    '美國安進': ('AMGN', 'NASDAQ'),
    'Thermo Fisher Scientific': ('TMO', 'NYSE'),
    '安捷倫科技': ('A', 'NYSE'),
    '史賽克': ('SYK', 'NYSE'),

    # Consumer
    'Nike': ('NKE', 'NYSE'),
    '耐克森': ('NKE', 'NYSE'),
    'Adidas': ('ADDYY', 'OTC'),
    'Puma': ('PUMSY', 'OTC'),
    '迪卡儂': ('', 'Private'),
    '可口可樂': ('KO', 'NYSE'),
    '百事公司': ('PEP', 'NASDAQ'),
    '雀巢': ('NSRGY', 'OTC'),
    '達能集團': ('DANOY', 'OTC'),
    'Walmart': ('WMT', 'NYSE'),
    '麥當勞': ('MCD', 'NYSE'),
    'Subway': ('', 'Private'),

    # Telecom
    'AT&T': ('T', 'NYSE'),
    '威訊通訊': ('VZ', 'NYSE'),
    'Ericsson': ('ERIC', 'NASDAQ'),
    'Nokia Network': ('NOK', 'NYSE'),

    # Logistics
    '聯邦快遞': ('FDX', 'NYSE'),
    '優比速公司': ('UPS', 'NYSE'),
    '德迅': ('DSDVY', 'OTC'),

    # Automotive
    '特斯拉': ('TSLA', 'NASDAQ'),
    'Mobileye': ('MBLY', 'NASDAQ'),

    # Others
    'Palantir': ('PLTR', 'NYSE'),
    'Teradata': ('TDC', 'NYSE'),
    'SAS': ('', 'Private'),
    'Nasdaq': ('NDAQ', 'NASDAQ'),
    'ANSYS': ('ANSS', 'NASDAQ'),
    'PTC': ('PTC', 'NASDAQ'),
    '歐特克': ('ADSK', 'NASDAQ'),
    '達梭系統': ('DASTY', 'OTC'),
}


def extract_foreign_companies():
    """從 raw_SupplyChain_*.csv 擷取所有外國企業"""
    companies = set()

    for filename in os.listdir('data'):
        if filename.startswith('raw_SupplyChain_') and filename.endswith('.csv') and filename != 'raw_SupplyChainMap.csv':
            filepath = f'data/{filename}'
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if not row['代號']:  # Empty code = foreign company
                        companies.add(row['名稱'])

    return sorted(companies)


def load_existing_mappings():
    """載入現有的對照表"""
    mappings = {}
    filepath = 'data/raw_non-TWSE-TPEX.csv'

    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['名稱']:
                    mappings[row['名稱']] = {
                        'symbol': row.get('股票代號', ''),
                        'exchange': row.get('交易所', '')
                    }

    return mappings


def search_yahoo_finance(company_name):
    """使用 Yahoo Finance 搜尋股票代號"""
    try:
        # Try direct search
        ticker = yf.Ticker(company_name)
        info = ticker.info
        if info and 'symbol' in info:
            return info['symbol'], info.get('exchange', '')
    except Exception:
        pass

    return '', ''


def update_csv(companies, mappings):
    """更新 non-TWSE-TPEX.csv"""
    filepath = 'data/raw_non-TWSE-TPEX.csv'

    results = []
    for name in companies:
        # Check known mappings first
        if name in KNOWN_MAPPINGS:
            symbol, exchange = KNOWN_MAPPINGS[name]
        elif name in mappings and mappings[name]['symbol']:
            symbol = mappings[name]['symbol']
            exchange = mappings[name]['exchange']
        else:
            symbol = ''
            exchange = ''

        results.append({
            '名稱': name,
            '股票代號': symbol,
            '交易所': exchange
        })

    # Write CSV
    with open(filepath, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['名稱', '股票代號', '交易所'])
        writer.writeheader()
        writer.writerows(results)

    return results


def main():
    sys.stdout.reconfigure(encoding='utf-8')

    print("=" * 60)
    print("外國企業股票代號更新程式 v1.0")
    print(f"執行時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Extract foreign companies
    print("\n擷取外國企業名稱...")
    companies = extract_foreign_companies()
    print(f"  找到 {len(companies)} 家外國企業")

    # Load existing mappings
    print("\n載入現有對照表...")
    mappings = load_existing_mappings()
    print(f"  已有 {len(mappings)} 筆對照記錄")

    # Update CSV with known mappings
    print("\n更新對照表...")
    results = update_csv(companies, mappings)

    # Statistics
    with_symbol = sum(1 for r in results if r['股票代號'])
    private = sum(1 for r in results if r['交易所'] == 'Private')
    acquired = sum(1 for r in results if r['交易所'] == 'Acquired')

    print(f"\n統計:")
    print(f"  總計: {len(results)} 家外國企業")
    print(f"  已有代號: {with_symbol} 家")
    print(f"  私有公司: {private} 家")
    print(f"  已被收購: {acquired} 家")
    print(f"  待查詢: {len(results) - with_symbol} 家")

    print(f"\n📄 已匯出至 data/raw_non-TWSE-TPEX.csv")
    print("\n" + "=" * 60)
    print("處理完成!")


if __name__ == "__main__":
    main()
