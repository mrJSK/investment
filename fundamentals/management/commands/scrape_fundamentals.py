# # fundamentals/management/commands/scrape_fundamentals.py

# import requests
# from bs4 import BeautifulSoup
# import time
# import re
# import os
# from django.core.management.base import BaseCommand
# from fundamentals.models import Company

# # --- UTILITY FUNCTIONS (Corrected) ---

# def get_soup(url):
#     """Fetches a URL and returns a BeautifulSoup object and its raw text."""
#     headers = {'User-Agent': 'Mozilla/5.0'}
#     try:
#         response = requests.get(url, headers=headers, timeout=20)
#         response.raise_for_status()
#         return BeautifulSoup(response.content, 'lxml'), response.text
#     except requests.exceptions.RequestException as e:
#         print(f"Error fetching {url}: {e}")
#         return None, None

# def clean_text(text):
#     """Cleans text by stripping whitespace and removing unwanted characters."""
#     if not text:
#         return None
#     # Remove currency symbols, commas, percentages, and "Cr." which is common
#     return text.strip().replace('₹', '').replace(',', '').replace('%', '').replace('Cr.', '').strip()

# def parse_number(text):
#     """Converts cleaned text to a float, handling potential errors."""
#     cleaned = clean_text(text)
#     if cleaned in [None, '']:
#         return None
#     # Extract the numerical part from the cleaned string.
#     match = re.search(r'[-+]?\d*\.\d+|\d+', cleaned)
#     if match:
#         try:
#             return float(match.group(0))
#         except (ValueError, TypeError):
#             return None
#     return None


# # --- SCRAPING HELPER FUNCTIONS (Corrected) ---

# def parse_financial_table(soup, table_id):
#     """A generic function to parse financial tables like Quarters, P&L, etc."""
#     table = soup.select_one(f'section#{table_id} table.data-table')
#     if not table:
#         return []

#     headers = [th.get_text(strip=True) for th in table.select('thead th')][1:]
#     data = []
#     for row in table.select('tbody tr'):
#         cols = row.select('td')
#         # Skip footer rows like 'Raw PDF'
#         if not cols or 'sub' in row.get('class', []):
#             continue
        
#         row_name_elem = cols[0]
#         if not row_name_elem:
#             continue
            
#         row_name = row_name_elem.get_text(strip=True).replace('+', '').strip()
#         if not row_name:
#             continue

#         row_data = {'Description': row_name}
        
#         for i, col in enumerate(cols[1:]):
#             if i < len(headers):
#                 row_data[headers[i]] = col.get_text(strip=True)
#         data.append(row_data)
#     return data

# def parse_shareholding_table(soup, table_id):
#     """Parses shareholding tables (quarterly or yearly)."""
#     table = soup.select_one(f'div#{table_id} table.data-table')
#     if not table:
#         return {}

#     headers = [th.get_text(strip=True) for th in table.select('thead th')][1:]
#     data = {}
#     for row in table.select('tbody tr'):
#         cols = row.select('td')
#         if not cols or 'sub' in row.get('class', []):
#             continue
        
#         row_name_elem = cols[0]
#         if not row_name_elem:
#             continue

#         row_name = row_name_elem.get_text(strip=True).replace('+', '').strip()
#         if not row_name:
#             continue

#         values = [col.get_text(strip=True) for col in cols[1:]]
#         row_data = {headers[i]: values[i] for i in range(len(values))}
#         data[row_name] = row_data
#     return data

# def parse_growth_tables(soup):
#     """Parses all four compounded growth tables."""
#     data = {}
#     tables = soup.select('#profit-loss table.ranges-table')
#     for table in tables:
#         title_elem = table.select_one('th')
#         if title_elem:
#             title = title_elem.get_text(strip=True).replace(':', '')
#             table_data = {}
#             for row in table.select('tr')[1:]:
#                 cols = row.select('td')
#                 if len(cols) == 2:
#                     key = cols[0].get_text(strip=True).replace(':', '')
#                     value = cols[1].get_text(strip=True)
#                     table_data[key] = value
#             data[title] = table_data
#     return data

# def extract_document_links(soup, container_selector):
#     """Extracts links from a specific document container."""
#     container = soup.select_one(container_selector)
#     if not container:
#         return []
    
#     links = []
#     for a in container.select('ul.list-links li a'):
#         link_data = {
#             'text': ' '.join(a.get_text(strip=True, separator=' ').split()),
#             'href': a.get('href')
#         }
#         links.append(link_data)
#     return links

# # --- MAIN SCRAPER LOGIC (Corrected) ---

# class Command(BaseCommand):
#     help = 'Scrapes company fundamentals from screener.in'

#     def handle(self, *args, **options):
#         self.stdout.write("Starting company fundamentals scraper...")
        
#         visited_links_folder = 'visited_company_pages'
#         if not os.path.exists(visited_links_folder):
#             os.makedirs(visited_links_folder)
#             self.stdout.write(f"Created directory: {visited_links_folder}")

#         # 1. Scrape company names and symbols from the main list pages
#         company_list = []
#         for i in range(1, 100): 
#             list_url = f"https://www.screener.in/screens/515361/largecaptop-100midcap101-250smallcap251/?page={i}&limit=50"
#             self.stdout.write(f"Fetching page {i}: {list_url}")
#             soup, _ = get_soup(list_url)
#             if not soup:
#                 continue

#             rows = soup.select('table.data-table tr[data-row-company-id]')
#             if not rows:
#                 self.stdout.write(f"No more companies found on page {i}. Stopping.")
#                 break
                
#             for row in rows:
#                 link_tag = row.select_one('a')
#                 if link_tag:
#                     name = link_tag.get_text(strip=True)
#                     href = link_tag['href']
#                     symbol = href.split('/')[2]
#                     # Append the full URL for later use
#                     company_list.append({'name': name, 'symbol': symbol, 'url': f"https://www.screener.in{href}"})
            
#             time.sleep(1)

#         self.stdout.write(f"Found {len(company_list)} companies to process.")

#         # 2. Scrape detailed info for each company
#         for company_data in company_list:
#             symbol = company_data['symbol']
#             self.stdout.write(f"--- Processing {company_data['name']} ({symbol}) ---")
            
#             detail_url = company_data['url']
#             soup, html_content = get_soup(detail_url)
#             if not soup:
#                 continue
                
#             # Store the visited HTML
#             if html_content:
#                 try:
#                     with open(os.path.join(visited_links_folder, f"{symbol}.html"), "w", encoding="utf-8") as f:
#                         f.write(html_content)
#                     self.stdout.write(f"Saved HTML for {symbol}")
#                 except Exception as e:
#                     self.stdout.write(self.style.ERROR(f"Could not save HTML for {symbol}: {e}"))

#             try:
#                 # Basic Info
#                 about_div = soup.select_one('.company-profile .about p')
#                 about = about_div.get_text(strip=True) if about_div else None
                
#                 # Corrected website link selector
#                 website_link = soup.select_one('.company-links a:not([href*="bseindia.com"]):not([href*="nseindia.com"])')
#                 website = website_link['href'] if website_link else None

#                 bse_link = soup.select_one('a[href*="bseindia.com"]')
#                 bse_code = bse_link.get_text(strip=True).replace('BSE:', '').strip() if bse_link else None
                
#                 nse_link = soup.select_one('a[href*="nseindia.com"]')
#                 nse_code = nse_link.get_text(strip=True).replace('NSE:', '').strip() if nse_link else None

#                 # Ratios (This is now parsed correctly)
#                 ratios_data = {}
#                 for li in soup.select('#top-ratios li'):
#                     name_elem = li.select_one('.name')
#                     value_elem = li.select_one('.value')
#                     if name_elem and value_elem:
#                         name = name_elem.get_text(strip=True)
#                         value = value_elem.get_text(strip=True)
#                         ratios_data[name] = value

#                 # Pros and Cons
#                 pros = [li.get_text(strip=True) for li in soup.select('.pros ul li')]
#                 cons = [li.get_text(strip=True) for li in soup.select('.cons ul li')]

#                 # Growth tables
#                 growth_tables = parse_growth_tables(soup)

#                 # Shareholding pattern
#                 shareholding = {
#                     'quarterly': parse_shareholding_table(soup, 'quarterly-shp'),
#                     'yearly': parse_shareholding_table(soup, 'yearly-shp')
#                 }
                
#                 # Corrected document extraction with specific selectors
#                 annual_reports = extract_document_links(soup, 'div.annual-reports')
#                 credit_ratings = extract_document_links(soup, 'div.credit-ratings')

#                 # Update or Create Company in DB
#                 company_obj, created = Company.objects.update_or_create(
#                     symbol=symbol,
#                     defaults={
#                         'name': company_data['name'],
#                         'about': about,
#                         'website': website,
#                         'bse_code': bse_code,
#                         'nse_code': nse_code,
#                         'market_cap': parse_number(ratios_data.get('Market Cap')),
#                         'current_price': parse_number(ratios_data.get('Current Price')),
#                         'high_low': clean_text(ratios_data.get('High / Low')),
#                         'stock_pe': parse_number(ratios_data.get('Stock P/E')),
#                         'book_value': parse_number(ratios_data.get('Book Value')),
#                         'dividend_yield': parse_number(ratios_data.get('Dividend Yield')),
#                         'roce': parse_number(ratios_data.get('ROCE')),
#                         'roe': parse_number(ratios_data.get('ROE')),
#                         'face_value': parse_number(ratios_data.get('Face Value')),
#                         'pros': pros,
#                         'cons': cons,
#                         'quarterly_results': parse_financial_table(soup, 'quarters'),
#                         'profit_loss_statement': parse_financial_table(soup, 'profit-loss'),
#                         'balance_sheet': parse_financial_table(soup, 'balance-sheet'),
#                         'cash_flow_statement': parse_financial_table(soup, 'cash-flow'),
#                         'ratios': parse_financial_table(soup, 'ratios'),
#                         'compounded_sales_growth': growth_tables.get('Compounded Sales Growth', {}),
#                         'compounded_profit_growth': growth_tables.get('Compounded Profit Growth', {}),
#                         'stock_price_cagr': growth_tables.get('Stock Price CAGR', {}),
#                         'return_on_equity': growth_tables.get('Return on Equity', {}),
#                         'shareholding_pattern': shareholding,
#                         'annual_reports': annual_reports,
#                         'credit_ratings': credit_ratings, 
#                     }
#                 )
                
#                 action = "Created" if created else "Updated"
#                 self.stdout.write(self.style.SUCCESS(f"Successfully {action} data for {company_data['name']}"))

#             except Exception as e:
#                 import traceback
#                 self.stdout.write(self.style.ERROR(f"Error processing {company_data['name']}: {e}"))
#                 traceback.print_exc()

#             time.sleep(1)

#         self.stdout.write(self.style.SUCCESS("Scraping finished."))
# fundamentals/management/commands/populate_fundamentals.py

import os
import re
import time
from decimal import Decimal
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
import requests
from fundamentals.models import Company

# --- UTILITY FUNCTIONS ---

def get_soup(url):
    """Fetches a URL and returns a BeautifulSoup object and its raw text."""
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        return BeautifulSoup(response.content, 'lxml'), response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None, None

def clean_text(text):
    """Cleans text by stripping whitespace and removing unwanted characters."""
    if not text: return None
    return text.strip().replace('₹', '').replace(',', '').replace('%', '').replace('Cr.', '').strip()

def parse_number(text):
    """Converts cleaned text to a float, handling potential errors."""
    cleaned = clean_text(text)
    if cleaned in [None, '']: return None
    match = re.search(r'[-+]?\d*\.\d+|\d+', cleaned)
    if match:
        try: return float(match.group(0))
        except (ValueError, TypeError): return None
    return None

# --- SCRAPING HELPER FUNCTIONS ---

def parse_industry_classification(soup):
    """Parses the industry classification breadcrumb from the peers section."""
    peers_section = soup.select_one('section#peers')
    if not peers_section: return None
    path_paragraph = peers_section.select_one('p.sub:not(#benchmarks)')
    if not path_paragraph: return None
    path_links = path_paragraph.select('a')
    if not path_links: return None
    return ' > '.join([link.get_text(strip=True).replace('&', 'and') for link in path_links])

def get_latest_quarterly_value(results, key):
    """Extracts the latest value from a quarterly results JSON list."""
    if not results or not isinstance(results, list): return None
    for quarter in reversed(results):
        if quarter.get(key) and quarter.get(key) not in ['--', '']:
            return parse_number(quarter.get(key))
    return None

def get_latest_financial_value(table_data, description):
    """Gets the latest value for a specific row from a parsed financial table."""
    if not table_data: return None
    for row in table_data:
        if row.get('Description') == description:
            keys = list(row.keys())
            if len(keys) > 1:
                latest_date_key = keys[-1]
                return parse_number(row[latest_date_key])
    return None

def calculate_debt_to_equity(balance_sheet_data):
    """Calculates Debt/Equity ratio from balance sheet data."""
    if not balance_sheet_data: return None
    borrowings = get_latest_financial_value(balance_sheet_data, 'Borrowings')
    reserves = get_latest_financial_value(balance_sheet_data, 'Reserves')
    equity_capital = get_latest_financial_value(balance_sheet_data, 'Equity Capital')
    
    if borrowings is not None and reserves is not None and equity_capital is not None:
        total_equity = equity_capital + reserves
        if total_equity > 0:
            return round(borrowings / total_equity, 2)
    return None

def parse_financial_table(soup, table_id):
    section = soup.select_one(f'section#{table_id}')
    if not section: return []
    table = section.select_one('table.data-table')
    if not table: return []
    headers = [th.get_text(strip=True) for th in table.select('thead th')][1:]
    data = []
    for row in table.select('tbody tr'):
        cols = row.select('td')
        if not cols or 'sub' in row.get('class', []): continue
        row_name = cols[0].get_text(strip=True).replace('+', '').strip()
        if not row_name: continue
        row_data = {'Description': row_name}
        for i, col in enumerate(cols[1:]):
            if i < len(headers): row_data[headers[i]] = col.get_text(strip=True)
        data.append(row_data)
    return data

def parse_shareholding_table(soup, table_id):
    table = soup.select_one(f'div#{table_id} table.data-table')
    if not table: return {}
    headers = [th.get_text(strip=True) for th in table.select('thead th')][1:]
    data = {}
    for row in table.select('tbody tr'):
        cols = row.select('td')
        if not cols or 'sub' in row.get('class', []): continue
        row_name = cols[0].get_text(strip=True).replace('+', '').strip()
        if not row_name: continue
        values = [col.get_text(strip=True) for col in cols[1:]]
        row_data = {headers[i]: values[i] for i in range(len(values))}
        data[row_name] = row_data
    return data

def parse_growth_tables(soup):
    data = {}
    tables = soup.select('#profit-loss table.ranges-table')
    for table in tables:
        title_elem = table.select_one('th')
        if title_elem:
            title = title_elem.get_text(strip=True).replace(':', '')
            table_data = {}
            for row in table.select('tr')[1:]:
                cols = row.select('td')
                if len(cols) == 2: table_data[cols[0].get_text(strip=True).replace(':', '')] = cols[1].get_text(strip=True)
            data[title] = table_data
    return data

def extract_document_links(soup, container_selector):
    container = soup.select_one(container_selector)
    if not container: return []
    links = []
    for a in container.select('ul.list-links li a'):
        links.append({'text': ' '.join(a.get_text(strip=True, separator=' ').split()), 'href': a.get('href')})
    return links

def extract_concall_links(soup):
    container = soup.select_one('div.concalls')
    if not container: return []
    concalls = []
    for li in container.select('ul.list-links li'):
        date = li.select_one('div.nowrap').get_text(strip=True) if li.select_one('div.nowrap') else "N/A"
        links = {a.get_text(strip=True): a.get('href') for a in li.select('a.concall-link')}
        if date != "N/A" and links: concalls.append({'date': date, 'links': links})
    return concalls


class Command(BaseCommand):
    help = 'Scrapes, parses, and populates company and peer data in one go.'

    def handle(self, *args, **options):
        
        # --- PHASE 1: SCRAPE COMPANY LIST AND SAVE HTML LOCALLY ---
        self.stdout.write(self.style.SUCCESS("--- PHASE 1: Scraping company list and saving HTML files ---"))
        folder_path = 'visited_company_pages'
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            self.stdout.write(f"Created directory: {folder_path}")

        company_list = []
        for i in range(1, 101): # Scrape up to 100 pages
            list_url = f"https://www.screener.in/screens/515361/largecaptop-100midcap101-250smallcap251/?page={i}&limit=50"
            self.stdout.write(f"Fetching company list from page {i}...")
            soup, _ = get_soup(list_url)
            if not soup: continue

            rows = soup.select('table.data-table tr[data-row-company-id]')
            if not rows:
                self.stdout.write(self.style.WARNING(f"No more companies found on page {i}. Stopping list scrape."))
                break
            
            for row in rows:
                link_tag = row.select_one('a')
                if link_tag:
                    href = link_tag['href']
                    symbol = href.split('/')[2]
                    company_list.append({'symbol': symbol, 'url': f"https://www.screener.in{href}"})
            time.sleep(1)

        self.stdout.write(f"Found {len(company_list)} companies. Now fetching and saving individual HTML pages.")
        
        for company_data in company_list:
            symbol = company_data['symbol']
            file_path = os.path.join(folder_path, f"{symbol}.html")
            if os.path.exists(file_path):
                self.stdout.write(self.style.NOTICE(f"HTML for {symbol} already exists. Skipping download."))
                continue

            self.stdout.write(f"Downloading HTML for {symbol}...")
            soup, html_content = get_soup(company_data['url'])
            if html_content:
                with open(file_path, "w", encoding="utf-8") as f: f.write(html_content)
            time.sleep(1)

        self.stdout.write(self.style.SUCCESS("--- PHASE 1 Complete. ---"))


        # --- PHASE 2: PARSE LOCAL FILES AND POPULATE DATABASE ---
        self.stdout.write(self.style.SUCCESS("\n--- PHASE 2: Parsing local HTML and populating database ---"))
        html_files = [f for f in os.listdir(folder_path) if f.endswith('.html')]
        self.stdout.write(f"Found {len(html_files)} HTML files to process.")

        for filename in html_files:
            company_symbol = os.path.splitext(filename)[0]
            file_path = os.path.join(folder_path, filename)
            self.stdout.write(f"Parsing {filename}...")

            try:
                with open(file_path, 'r', encoding='utf-8') as f: soup = BeautifulSoup(f.read(), 'lxml')
                
                name_elem = soup.select_one('h1.margin-0'); company_name = name_elem.get_text(strip=True) if name_elem else company_symbol
                
                ratios_data = {li.select_one('.name').get_text(strip=True): li.select_one('.value').get_text(strip=True) for li in soup.select('#top-ratios li') if li.select_one('.name') and li.select_one('.value')}
                growth_tables = parse_growth_tables(soup)
                
                defaults = {
                    'name': company_name,
                    'about': soup.select_one('.company-profile .about p').get_text(strip=True) if soup.select_one('.company-profile .about p') else None,
                    'website': soup.select_one('.company-links a:not([href*="bseindia.com"]):not([href*="nseindia.com"])')['href'] if soup.select_one('.company-links a:not([href*="bseindia.com"]):not([href*="nseindia.com"])') else None,
                    'bse_code': clean_text(soup.select_one('a[href*="bseindia.com"]').get_text(strip=True)) if soup.select_one('a[href*="bseindia.com"]') else None,
                    'nse_code': clean_text(soup.select_one('a[href*="nseindia.com"]').get_text(strip=True)) if soup.select_one('a[href*="nseindia.com"]') else None,
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
                    'compounded_sales_growth': growth_tables.get('Compounded Sales Growth', {}),
                    'compounded_profit_growth': growth_tables.get('Compounded Profit Growth', {}),
                    'stock_price_cagr': growth_tables.get('Stock Price CAGR', {}),
                    'return_on_equity': growth_tables.get('Return on Equity', {}),
                    'shareholding_pattern': {'quarterly': parse_shareholding_table(soup, 'quarterly-shp'), 'yearly': parse_shareholding_table(soup, 'yearly-shp')},
                    'announcements': extract_document_links(soup, '#company-announcements-tab'),
                    'annual_reports': extract_document_links(soup, 'div.annual-reports'),
                    'credit_ratings': extract_document_links(soup, 'div.credit-ratings'),
                    'concalls': extract_concall_links(soup),
                    'industry_classification': parse_industry_classification(soup)
                }
                
                Company.objects.update_or_create(symbol=company_symbol, defaults=defaults)

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error during PHASE 2 for {filename}: {e}"))
        
        self.stdout.write(self.style.SUCCESS("--- PHASE 2 Complete. ---"))

        # --- PHASE 3: BUILD AND SAVE PEER COMPARISON DATA ---
        self.stdout.write(self.style.SUCCESS("\n--- PHASE 3: Building peer comparison data ---"))
        
        all_companies = list(Company.objects.all())
        industry_groups = {}
        for company in all_companies:
            if company.industry_classification:
                industry_groups.setdefault(company.industry_classification, []).append(company)

        self.stdout.write(f"Found {len(industry_groups)} unique industry groups to process.")
        
        update_count = 0
        for company in all_companies:
            if not company.industry_classification:
                continue

            peer_objects = [p for p in industry_groups.get(company.industry_classification, []) if p.symbol != company.symbol]
            
            peer_comparison_data = []
            for peer in peer_objects:
                cmp_bv = None
                if peer.current_price and peer.book_value and float(peer.book_value) > 0:
                    cmp_bv = round(float(peer.current_price) / float(peer.book_value), 2)
                
                peer_dict = {
                    "name": peer.name,
                    "cmp": float(peer.current_price) if peer.current_price is not None else None,
                    "pe": float(peer.stock_pe) if peer.stock_pe is not None else None,
                    "mar_cap_cr": float(peer.market_cap) if peer.market_cap is not None else None,
                    "div_yld_pct": float(peer.dividend_yield) if peer.dividend_yield is not None else None,
                    "np_qtr_cr": get_latest_quarterly_value(peer.quarterly_results, 'Net Profit'),
                    "sales_qtr_cr": get_latest_quarterly_value(peer.quarterly_results, 'Sales'),
                    "roce_pct": float(peer.roce) if peer.roce is not None else None,
                    "cmp_bv": cmp_bv,
                    "debt_eq": calculate_debt_to_equity(peer.balance_sheet),
                }
                peer_comparison_data.append(peer_dict)

            company.peer_comparison = peer_comparison_data
            company.save(update_fields=['peer_comparison'])
            update_count += 1

        self.stdout.write(self.style.SUCCESS(f"--- PHASE 3 Complete. Updated peer data for {update_count} companies. ---"))