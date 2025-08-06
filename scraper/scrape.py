import json
import re
import os
import subprocess
import tempfile
from datetime import datetime

import pandas as pd
import requests
from playwright.sync_api import sync_playwright

# --- 配置 ---
API_KEY = os.getenv('EXCHANGE_RATE_API_KEY')
BASE_CURRENCY = "CNY"
EXCHANGE_RATE_API_URL = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/{BASE_CURRENCY}"

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
REPO_URL = os.getenv('REPO_URL') # e.g., https://github.com/your-username/your-repo.git

TARGET_COUNTRIES = {
    'ng': 'NGN', 'sg': 'SGD', 'in': 'INR', 'us': 'USD', 'gb': 'GBP', 
    'de': 'EUR', 'jp': 'JPY', 'br': 'BRL', 'au': 'AUD', 'ca': 'CAD', 
    'za': 'ZAR', 'tr': 'TRY', 'pk': 'PKR', 'kr': 'KRW'
}

PLAN_CARD_SELECTOR = '[data-testid="plan-card"]'
PLAN_NAME_SELECTOR = '[data-testid="plan-title"]'
PLAN_PRICE_SELECTOR = '[data-testid="plan-price"]'

# --- 辅助函数 ---
def get_exchange_rates():
    try:
        response = requests.get(EXCHANGE_RATE_API_URL)
        response.raise_for_status()
        return response.json().get("conversion_rates", {})
    except requests.RequestException as e:
        print(f"Error fetching exchange rates: {e}")
        return None

def normalize_plan_name(name):
    name_lower = name.lower()
    if 'family' in name_lower: return 'Family'
    if 'duo' in name_lower: return 'Duo'
    if 'student' in name_lower: return 'Student'
    if 'individual' in name_lower or 'standard' in name_lower or 'basic' in name_lower: return 'Individual'
    return 'Unknown'

def clean_price(price_str):
    price_str = price_str.replace(',', '').replace(' ', '')
    numbers = re.findall(r'[\d\.]+', price_str)
    return float(numbers) if numbers else None

# --- 主抓取逻辑 ---
def scrape_spotify_prices():
    all_prices =
    rates = get_exchange_rates()
    if not rates:
        print("Halting scrape due to inability to fetch exchange rates.")
        return None

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--no-sandbox'])
        page = browser.new_page()

        for code, currency in TARGET_COUNTRIES.items():
            url = f"https://www.spotify.com/{code}/premium"
            print(f"Scraping {url}...")
            try:
                page.goto(url, timeout=45000)
                page.wait_for_selector(PLAN_CARD_SELECTOR, timeout=20000)
                
                plan_cards = page.locator(PLAN_CARD_SELECTOR).all()
                for card in plan_cards:
                    try:
                        name = card.locator(PLAN_NAME_SELECTOR).first.inner_text()
                        price_str = card.locator(PLAN_PRICE_SELECTOR).first.inner_text()
                        local_price = clean_price(price_str)
                        if local_price is None: continue

                        price_cny = round(local_price / rates[currency], 2) if currency in rates else None
                        
                        all_prices.append({
                            "country_code": code.upper(), "plan_name": normalize_plan_name(name),
                            "local_price": local_price, "local_currency": currency,
                            "price_cny": price_cny
                        })
                    except Exception as e:
                        print(f"  - Error parsing a plan card on {url}: {e}")
            except Exception as e:
                print(f"Failed to scrape {url}: {e}")
        
        browser.close()

    if not all_prices: return None
        
    df = pd.DataFrame(all_prices)
    df.dropna(subset=['price_cny'], inplace=True)
    df = df.loc[df.groupby(['country_code', 'plan_name'])['price_cny'].idxmin()]
    return df.to_dict('records')

# --- Git 操作 ---
def update_repo_with_data(data):
    if not REPO_URL or not GITHUB_TOKEN:
        print("REPO_URL or GITHUB_TOKEN environment variable not set. Skipping git push.")
        return

    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = os.path.join(tmpdir, 'repo')
        
        # 构建认证后的仓库 URL
        auth_repo_url = REPO_URL.replace('https://', f'https://oauth2:{GITHUB_TOKEN}@')
        
        print("Cloning repository...")
        subprocess.run(['git', 'clone', auth_repo_url, repo_path], check=True)
        
        # 配置 Git 用户
        subprocess.run(['git', 'config', '--global', 'user.email', 'bot@render.com'], cwd=repo_path, check=True)
        subprocess.run(, cwd=repo_path, check=True)

        # 写入数据文件
        output_file = os.path.join(repo_path, 'frontend', 'spotify_prices.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        print(f"Data written to {output_file}")

        # 检查是否有变动
        status_result = subprocess.run(['git', 'status', '--porcelain'], cwd=repo_path, check=True, capture_output=True, text=True)
        if not status_result.stdout.strip():
            print("No changes to commit.")
            return

        print("Committing and pushing changes...")
        subprocess.run(['git', 'add', output_file], cwd=repo_path, check=True)
        commit_message = f"Data update: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}"
        subprocess.run(['git', 'commit', '-m', commit_message], cwd=repo_path, check=True)
        subprocess.run(['git', 'push'], cwd=repo_path, check=True)
        print("Changes pushed to repository successfully.")

# --- 主执行函数 ---
if __name__ == "__main__":
    print("Starting Spotify price scraping process...")
    scraped_data = scrape_spotify_prices()
    if scraped_data:
        print(f"Successfully scraped {len(scraped_data)} records.")
        update_repo_with_data(scraped_data)
    else:
        print("Scraping process failed or returned no data.")
