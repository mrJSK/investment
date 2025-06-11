# fundamentals/management/commands/scrape_fundamentals.py

import os
import re
import time
import random
import requests
from datetime import datetime
from bs4 import BeautifulSoup

from django.core.management.base import BaseCommand
from django.db import transaction
from fundamentals.models import Company, IndustryClassification

# --- CONFIGURATION ---

# A list of user agents to rotate between to mimic different browsers
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
]

# The directory where we'll save the HTML files
HTML_STORAGE_PATH = 'data/scraped_html'

# --- HELPER & UTILITY FUNCTIONS ---

def get_timestamp():
    """Returns a formatted timestamp string for logging."""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# --- NETWORKING FUNCTIONS ---

def fetch_page(session, url, retries=3, backoff_factor=0.8, referer=None):
    """
    Fetches a URL using a persistent session with rotating headers and a retry mechanism.
    Returns the response object on success, None on failure.
    """
    headers = {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    if referer:
        headers['Referer'] = referer

    for attempt in range(retries):
        try:
            response = session.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            # Using print here as self.stdout is not available in this static context
            print(f"[{get_timestamp()}] [NETWORKING] Request to {url} failed: {e}. Retrying...")
            if attempt < retries - 1:
                wait_time = backoff_factor * (2 ** attempt) + random.uniform(0, 1)
                time.sleep(wait_time)
            else:
                print(f"[{get_timestamp()}] [NETWORKING] Final attempt to fetch {url} failed.")
                return None
    return None

# --- PARSING FUNCTIONS ---

def clean_text(text, field_name=""):
    if not text: return None
    if field_name in ["bse_code", "nse_code"]:
        return text.strip().replace('BSE:', '').replace('NSE:', '').strip()
    return text.strip().replace('₹', '').replace(',', '').replace('%', '').replace('Cr.', '').strip()

def parse_number(text):
    cleaned = clean_text(text)
    if cleaned in [None, '']: return None
    match = re.search(r'[-+]?\d*\.\d+|\d+', cleaned)
    if match:
        try:
            return float(match.group(0))
        except (ValueError, TypeError):
            return None
    return None

def get_calendar_sort_key(header_string):
    MONTH_MAP = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}
    try:
        month_str, year_str = header_string.strip().split()
        return (int(year_str), MONTH_MAP.get(month_str, 0))
    except (ValueError, KeyError, IndexError):
        try:
            return (int(header_string), 0)
        except (ValueError, TypeError):
            return (0, 0)

# ... (All other parsing functions are unchanged and included here)
def process_industry_path(soup):
    peers_section = soup.select_one('section#peers')
    if not peers_section: return None
    path_paragraph = peers_section.select_one('p.sub:not(#benchmarks)')
    if not path_paragraph: return None
    path_links = path_paragraph.select('a')
    if not path_links: return None
    path_names = [link.get_text(strip=True).replace('&', 'and') for link in path_links]
    parent_obj, last_classification_obj = None, None
    with transaction.atomic():
        for name in path_names:
            classification_obj, _ = IndustryClassification.objects.get_or_create(
                name=name, defaults={'parent': parent_obj}
            )
            parent_obj = last_classification_obj = classification_obj
    return last_classification_obj

def parse_website_link(soup):
    company_links_div = soup.select_one('div.company-links')
    if not company_links_div: return None
    all_links = company_links_div.find_all('a', href=True)
    for link in all_links:
        href = link['href']
        if 'bseindia.com' not in href and 'nseindia.com' not in href:
            return href
    return None

def parse_financial_table(soup, table_id):
    section = soup.select_one(f'section#{table_id}')
    if not section: return {}
    table = section.select_one('table.data-table')
    if not table: return {}
    original_headers = [th.get_text(strip=True) for th in table.select('thead th')][1:]
    if not original_headers: return {}
    sorted_headers = sorted(original_headers, key=get_calendar_sort_key, reverse=True)
    body_data = []
    for row in table.select('tbody tr'):
        cols = row.select('td')
        if not cols or 'sub' in row.get('class', []): continue
        row_name = cols[0].get_text(strip=True).replace('+', '').strip()
        if not row_name: continue
        original_values = [col.get_text(strip=True) for col in cols[1:]]
        value_map = dict(zip(original_headers, original_values))
        sorted_values = [value_map.get(h, '') for h in sorted_headers]
        body_data.append({'Description': row_name, 'values': sorted_values})
    return {'headers': sorted_headers, 'body': body_data}

def parse_shareholding_table(soup, table_id):
    table = soup.select_one(f'div#{table_id} table.data-table')
    if not table: return {}
    original_headers = [th.get_text(strip=True) for th in table.select('thead th')][1:]
    sorted_headers = sorted(original_headers, key=get_calendar_sort_key, reverse=True)
    data = {}
    for row in table.select('tbody tr'):
        cols = row.select('td')
        if not cols or 'sub' in row.get('class', []): continue
        row_name = cols[0].get_text(strip=True).replace('+', '').strip()
        if not row_name: continue
        original_values = [col.get_text(strip=True) for col in cols[1:]]
        value_map = dict(zip(original_headers, original_values))
        row_data = {h: value_map.get(h, '') for h in sorted_headers}
        data[row_name] = row_data
    return data

def parse_growth_tables(soup):
    data = {}
    pl_section = soup.select_one('section#profit-loss')
    if not pl_section: return data
    tables = pl_section.select('table.ranges-table')
    for table in tables:
        title_elem = table.select_one('th')
        if title_elem:
            title = title_elem.get_text(strip=True).replace(':', '')
            table_data = {
                cols[0].get_text(strip=True).replace(':', ''): cols[1].get_text(strip=True)
                for row in table.select('tr')[1:] if len(cols := row.select('td')) == 2
            }
            data[title] = table_data
    return data

# --- MAIN DJANGO COMMAND ---

class Command(BaseCommand):
    help = 'A comprehensive command to download and/or process company fundamentals from screener.in'

    def add_arguments(self, parser):
        parser.add_argument(
            '--mode',
            type=str,
            choices=['download', 'process', 'all'],
            default='all',
            help='Specify the operation mode: "download" to only fetch HTML, "process" to only parse local HTML, "all" to do both.'
        )

    def _log(self, message, style=None):
        """Helper function for styled, timestamped logging."""
        style = style or self.style.SUCCESS
        self.stdout.write(style(f"[{get_timestamp()}] {message}"))

    def _run_download_phase(self):
        """Handles the logic for fetching and saving HTML files."""
        self._log("====== STARTING DOWNLOAD PHASE ======", self.style.HTTP_SUCCESS)
        os.makedirs(HTML_STORAGE_PATH, exist_ok=True)
        self._log(f"[INFO] HTML will be saved to '{HTML_STORAGE_PATH}/'")

        summary = {'success': 0, 'skipped': 0, 'failed': 0}
        company_urls_to_scrape = []
        
        with requests.Session() as session:
            # 1. Get all company URLs from the listing pages
            for i in range(1, 100):
                list_url = f"https://www.screener.in/screens/515361/largecaptop-100midcap101-250smallcap251/?page={i}&limit=50"
                self._log(f"[LISTING] Fetching company list from page {i}...", self.style.HTTP_INFO)
                
                response = fetch_page(session, list_url)
                if not response:
                    self._log(f"[LISTING] Could not fetch list page {i}. Stopping URL collection.", self.style.WARNING)
                    break

                list_soup = BeautifulSoup(response.content, 'lxml')
                rows = list_soup.select('table.data-table tr[data-row-company-id]')
                
                if not rows:
                    self._log("[LISTING] No more companies found. Moving to download phase.", self.style.SUCCESS)
                    break
                
                for row in rows:
                    link_tag = row.select_one('a')
                    if link_tag and link_tag.get('href'):
                        company_urls_to_scrape.append(f"https://www.screener.in{link_tag['href']}")
                
                time.sleep(random.uniform(2, 4))

            self._log(f"\n[INFO] Found {len(company_urls_to_scrape)} company URLs to download.", self.style.SUCCESS)

            # 2. Download the HTML for each company
            total_urls = len(company_urls_to_scrape)
            for i, url in enumerate(company_urls_to_scrape):
                try:
                    company_symbol = url.strip('/').split('/')[-1]
                    filename = f"{company_symbol}.html"
                    filepath = os.path.join(HTML_STORAGE_PATH, filename)
                    
                    progress = f"[{i+1}/{total_urls}]"

                    if os.path.exists(filepath):
                        self._log(f"{progress} [SKIP] {company_symbol} already exists.", self.style.NOTICE)
                        summary['skipped'] += 1
                        continue

                    self._log(f"{progress} [DOWNLOAD] Fetching {company_symbol}...", self.style.HTTP_INFO)
                    
                    response = fetch_page(session, url, referer="https://www.screener.in/screens/")
                    if response:
                        with open(filepath, 'wb') as f:
                            f.write(response.content)
                        self._log(f"{progress} [SUCCESS] Saved {company_symbol} to {filepath}", self.style.SUCCESS)
                        summary['success'] += 1
                    else:
                        self._log(f"{progress} [FAILURE] Failed to download {company_symbol}", self.style.ERROR)
                        summary['failed'] += 1

                except Exception as e:
                    self._log(f"{progress} [ERROR] Unexpected error for {url}: {e}", self.style.ERROR)
                    summary['failed'] += 1
                
                finally:
                    time.sleep(random.uniform(1.5, 3.5))
        
        self._log("====== DOWNLOAD PHASE FINISHED ======", self.style.HTTP_SUCCESS)
        self._log(f"[SUMMARY] Success: {summary['success']}, Skipped: {summary['skipped']}, Failed: {summary['failed']}\n", self.style.SUCCESS)

    def _run_process_phase(self):
        """Handles the logic for parsing local HTML files and saving to DB."""
        self._log("====== STARTING PROCESSING PHASE ======", self.style.HTTP_SUCCESS)
        
        if not os.path.exists(HTML_STORAGE_PATH):
            self._log(f"[ERROR] Storage directory '{HTML_STORAGE_PATH}' not found.", self.style.ERROR)
            self._log("[INFO] Please run with '--mode download' first.", self.style.WARNING)
            return

        html_files = [f for f in os.listdir(HTML_STORAGE_PATH) if f.endswith('.html')]
        total_files = len(html_files)
        self._log(f"[INFO] Found {total_files} HTML files to process.", self.style.SUCCESS)

        summary = {'created': 0, 'updated': 0, 'failed': 0}

        for i, filename in enumerate(html_files):
            company_symbol = filename.replace('.html', '')
            filepath = os.path.join(HTML_STORAGE_PATH, filename)
            progress = f"[{i+1}/{total_files}]"
            self._log(f"{progress} --- Processing: {company_symbol} ---", self.style.HTTP_INFO)

            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    soup = BeautifulSoup(f.read(), 'lxml')

                # All data parsing logic is called here
                company_name = (soup.select_one('h1.margin-0').get_text(strip=True) or company_symbol)
                ratios_data = {li.select_one('.name').get_text(strip=True): li.select_one('.value').get_text(strip=True) 
                               for li in soup.select('#top-ratios li') if li.select_one('.name') and li.select_one('.value')}
                
                defaults = {
                    'name': company_name,
                    'about': soup.select_one('.company-profile .about p').get_text(strip=True) if soup.select_one('.company-profile .about p') else None,
                    'website': parse_website_link(soup),
                    'bse_code': clean_text(soup.select_one('a[href*="bseindia.com"]').get_text(strip=True) if soup.select_one('a[href*="bseindia.com"]') else None, "bse_code"),
                    'nse_code': clean_text(soup.select_one('a[href*="nseindia.com"]').get_text(strip=True) if soup.select_one('a[href*="nseindia.com"]') else None, "nse_code"),
                    'market_cap': parse_number(ratios_data.get('Market Cap')),
                    'current_price': parse_number(ratios_data.get('Current Price')),
                    'high_low': clean_text(ratios_data.get('High / Low')),
                    'stock_pe': parse_number(ratios_data.get('Stock P/E')),
                    'book_value': parse_number(ratios_data.get('Book Value')),
                    'dividend_yield': parse_number(ratios_data.get('Dividend Yield')),
                    'roce': parse_number(ratios_data.get('ROCE')),
                    'roe': parse_number(ratios_data.get('ROE')),
                    'face_value': parse_number(ratios_data.get('Face Value')),
                    'pros': [li.get_text(strip=True) for li in soup.select('.pros ul li')],
                    'cons': [li.get_text(strip=True) for li in soup.select('.cons ul li')],
                    'quarterly_results': parse_financial_table(soup, 'quarters'),
                    'profit_loss_statement': parse_financial_table(soup, 'profit-loss'),
                    'balance_sheet': parse_financial_table(soup, 'balance-sheet'),
                    'cash_flow_statement': parse_financial_table(soup, 'cash-flow'),
                    'ratios': parse_financial_table(soup, 'ratios'),
                    'industry_classification': process_industry_path(soup),
                    'shareholding_pattern': {'quarterly': parse_shareholding_table(soup, 'quarterly-shp')},
                    **parse_growth_tables(soup) # Directly merge growth tables into defaults
                }
                
                # Database Operation
                obj, created = Company.objects.update_or_create(symbol=company_symbol, defaults=defaults)
                
                if created:
                    action = "CREATED"
                    summary['created'] += 1
                else:
                    action = "UPDATED"
                    summary['updated'] += 1
                
                self._log(f"{progress} [SUCCESS] {action} data for {company_name}", self.style.SUCCESS)

            except Exception as e:
                self._log(f"{progress} [FAILURE] Error processing {company_symbol}: {e}", self.style.ERROR)
                summary['failed'] += 1

        self._log("====== PROCESSING PHASE FINISHED ======", self.style.HTTP_SUCCESS)
        self._log(f"[SUMMARY] Created: {summary['created']}, Updated: {summary['updated']}, Failed: {summary['failed']}\n", self.style.SUCCESS)

    def handle(self, *args, **options):
        start_time = time.time()
        mode = options['mode']
        
        self._log(f"SCRIPT STARTED in '{mode.upper()}' mode.", self.style.SUCCESS)

        if mode in ['download', 'all']:
            self._run_download_phase()

        if mode in ['process', 'all']:
            self._run_process_phase()

        end_time = time.time()
        duration = end_time - start_time
        self._log(f"SCRIPT FINISHED. Total execution time: {duration:.2f} seconds.", self.style.SUCCESS)