#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GetSupplyChain.py
Version: 2.0
Description: Downloads Taiwan stock market supply chain data from ic.tpex.org.tw
             Creates separate CSV files for each industry chain with upstream/downstream companies
"""

import requests
from bs4 import BeautifulSoup
import csv
import time
import re
import urllib3
from datetime import datetime

# Disable SSL warnings (ic.tpex.org.tw has certificate issues)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://ic.tpex.org.tw"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}
VERIFY_SSL = False

# Global mapping for foreign companies
FOREIGN_COMPANY_MAP = {}

def load_foreign_company_map():
    """載入外國企業對照表"""
    global FOREIGN_COMPANY_MAP
    import os
    filepath = 'data/raw_SupplyChain-non-TWSE-TPEX.csv'
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['名稱'] and row['股票代號']:
                    FOREIGN_COMPANY_MAP[row['名稱']] = row['股票代號']
        print(f"  載入 {len(FOREIGN_COMPANY_MAP)} 筆外國企業對照")

def get_chain_data(chain_code):
    """取得產業鏈的完整資料（子分類、位置、公司清單）"""
    url = f"{BASE_URL}/introduce.php?ic={chain_code}"
    try:
        print(f"正在下載 {chain_code} 產業鏈資料...")
        response = requests.get(url, headers=HEADERS, timeout=60, verify=VERIFY_SSL)
        response.raise_for_status()
        response.encoding = 'utf-8'
        content = response.text
        soup = BeautifulSoup(content, 'html.parser')

        # Get chain name from title
        title = soup.find('title')
        chain_name = ''
        if title:
            title_text = title.get_text(strip=True)
            if '>' in title_text:
                chain_name = title_text.split('>')[-1].strip()

        # Find positions of 上游, 中游, 下游 sections
        upstream_pos = content.find('chain-title-panel">上游')
        midstream_pos = content.find('chain-title-panel">中游')
        downstream_pos = content.find('chain-title-panel">下游')

        # Build subcategory info from ic_link elements
        subcategory_info = {}
        ic_links = re.findall(
            r'id="ic_link_([A-Z0-9]+)"[^>]*class="company-chain-panel"[^>]*>([^<]+)<',
            content
        )

        for code, name in ic_links:
            pos = content.find(f'ic_link_{code}')
            if midstream_pos > 0:
                if pos < midstream_pos:
                    position = '上游'
                elif downstream_pos > 0 and pos < downstream_pos:
                    position = '中游'
                else:
                    position = '下游'
            else:
                position = '上游' if downstream_pos < 0 or pos < downstream_pos else '下游'

            subcategory_info[code] = {
                'name': name.strip(),
                'position': position
            }

        # Extract companies from companyList divs using BeautifulSoup
        results = []
        seen_combinations = set()  # Avoid duplicate entries

        company_divs = soup.find_all('div', id=re.compile(r'^companyList_'))
        for div in company_divs:
            div_id = div.get('id', '')
            subcat_code = div_id.replace('companyList_', '')

            if subcat_code not in subcategory_info:
                continue

            subcat = subcategory_info[subcat_code]

            # Get all company links from ALL tables in this div (including foreign companies)
            company_links = div.find_all('a', href=True)
            for link in company_links:
                href = link.get('href', '')
                stock_name = link.get('title', link.get_text(strip=True))

                # Skip empty names or navigation links
                if not stock_name or stock_name in ['更多', '...']:
                    continue

                # Check if it's a Taiwan stock (has stk_code)
                match = re.search(r'stk_code=(\d+)', href)
                if match:
                    stock_code = match.group(1)
                else:
                    # Foreign company - use empty code
                    stock_code = ''

                # Create unique key to avoid duplicates (use name for foreign companies)
                key = f"{subcat_code}:{stock_code or stock_name}"
                if key in seen_combinations:
                    continue
                seen_combinations.add(key)

                results.append({
                    'chain_code': chain_code,
                    'chain_name': chain_name,
                    'position': subcat['position'],
                    'subcategory': subcat['name'],
                    'stock_code': stock_code,
                    'stock_name': stock_name
                })

        print(f"  ✅ 找到 {len(subcategory_info)} 個子分類, {len(results)} 筆公司資料")
        return results, chain_name

    except Exception as e:
        print(f"  ❌ 取得 {chain_code} 產業鏈失敗: {e}")
        import traceback
        traceback.print_exc()
        return [], ''

def export_chain_csv(data, chain_code, chain_name, output_path):
    """匯出產業鏈 CSV"""
    process_timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    fieldnames = ['位置', '子分類', '代號', '名稱', 'download_timestamp', 'process_timestamp']

    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for row in data:
            # Use foreign company map if stock_code is empty
            stock_code = row['stock_code']
            if not stock_code and row['stock_name'] in FOREIGN_COMPANY_MAP:
                stock_code = FOREIGN_COMPANY_MAP[row['stock_name']]

            writer.writerow({
                '位置': row['position'],
                '子分類': row['subcategory'],
                '代號': stock_code,
                '名稱': row['stock_name'],
                'download_timestamp': process_timestamp,
                'process_timestamp': process_timestamp
            })

    print(f"  📄 已匯出至 {output_path} ({len(data)} 筆)")

def build_supply_chain_map(chain_names):
    """從產業鏈 CSV 檔案建立 SupplyChainMap.csv"""
    import os

    # Read all supply chain CSVs
    all_chain_data = {}
    for filename in os.listdir('data'):
        if filename.startswith('raw_SupplyChain_') and filename.endswith('.csv') and filename != 'raw_SupplyChainMap.csv':
            chain_code = filename.replace('raw_SupplyChain_', '').replace('.csv', '')
            all_chain_data[chain_code] = []
            with open(f'data/{filename}', 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    all_chain_data[chain_code].append(row)

    # Read watchlist
    watchlist = []
    with open('StockID_TWSE_TPEX.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            code = row['代號'].strip()
            name = row['名稱'].strip()
            if code and code != '0000':
                watchlist.append({'code': code, 'name': name})

    print(f"\n建立 SupplyChainMap.csv ({len(watchlist)} 家觀察名單公司)...")

    # Build supply chain map
    results = []
    for company in watchlist:
        code = company['code']
        name = company['name']

        for chain_code, chain_data in all_chain_data.items():
            company_entries = [d for d in chain_data if d['代號'] == code]
            if not company_entries:
                continue

            positions = list(set(e['位置'] for e in company_entries))
            subcategories = list(set(e['子分類'] for e in company_entries))

            upstream_companies = []
            downstream_companies = []

            for pos in positions:
                if pos == '上游':
                    for d in chain_data:
                        if d['位置'] in ['中游', '下游'] and d['代號'] != code:
                            downstream_companies.append(f"{d['代號']}|{d['名稱']}")
                elif pos == '中游':
                    for d in chain_data:
                        if d['位置'] == '上游' and d['代號'] != code:
                            upstream_companies.append(f"{d['代號']}|{d['名稱']}")
                        elif d['位置'] == '下游' and d['代號'] != code:
                            downstream_companies.append(f"{d['代號']}|{d['名稱']}")
                elif pos == '下游':
                    for d in chain_data:
                        if d['位置'] in ['上游', '中游'] and d['代號'] != code:
                            upstream_companies.append(f"{d['代號']}|{d['名稱']}")

            upstream_companies = list(dict.fromkeys(upstream_companies))[:20]
            downstream_companies = list(dict.fromkeys(downstream_companies))[:20]

            results.append({
                '代號': code,
                '名稱': name,
                '產業鏈代碼': chain_code,
                '產業鏈名稱': chain_names.get(chain_code, chain_code),
                '位置': '/'.join(positions),
                '子分類': ';'.join(subcategories[:5]),
                '上游公司': ';'.join(upstream_companies),
                '下游公司': ';'.join(downstream_companies),
            })

    # Write CSV
    output_path = 'data/raw_SupplyChainMap.csv'
    process_timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    fieldnames = [
        '代號', '名稱', '產業鏈代碼', '產業鏈名稱', '位置', '子分類', '上游公司', '下游公司',
        'download_timestamp', 'process_timestamp'
    ]
    for row in results:
        row['download_timestamp'] = process_timestamp
        row['process_timestamp'] = process_timestamp

    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"  📄 已匯出 {len(results)} 筆記錄至 {output_path}")

def main():
    import sys
    import os
    sys.stdout.reconfigure(encoding='utf-8')

    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)

    print("=" * 60)
    print(f"產業鏈資料下載程式 v2.1")
    print(f"執行時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Load foreign company mapping
    load_foreign_company_map()

    # Industry chains to download
    chains = {
        'F000': '電腦及週邊設備',
        'I000': '通信網路',
        '5300': '人工智慧',
        '5800': '運動科技',
        'D000': '半導體',
        'U000': '金融',
        'T000': '交通運輸及航運',
        'B000': '休閒娛樂',
        'R000': '軟體服務',
        'C100': '製藥',
        '5500': '資通訊安全',
        'V000': '貿易百貨',
        'R300': '電子商務',
        '5200': '金融科技',
        'L000': '印刷電路板',
        'C200': '醫療器材',
        'M000': '食品',
        'X000': '其他',
        '6000': '自動化',
        'G000': '平面顯示器',
        'P000': '電機機械',
    }

    for chain_code, expected_name in chains.items():
        print(f"\n處理 {chain_code} ({expected_name})...")

        data, chain_name = get_chain_data(chain_code)
        time.sleep(2)  # Rate limiting

        if data:
            output_path = f"data/raw_SupplyChain_{chain_code}.csv"
            export_chain_csv(data, chain_code, chain_name, output_path)
        else:
            print(f"  ⚠️ {chain_code} 無資料")

    # Build SupplyChainMap.csv from the chain CSVs
    build_supply_chain_map(chains)

    print("\n" + "=" * 60)
    print("處理完成! 🎉")

if __name__ == "__main__":
    main()
