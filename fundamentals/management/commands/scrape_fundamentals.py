# # # fundamentals/management/commands/scrape_fundamentals.py

# # import requests
# # import re
# # import time
# # from bs4 import BeautifulSoup
# # from django.core.management.base import BaseCommand
# # from fundamentals.models import Company, IndustryClassification

# # # --- UTILITY AND HELPER FUNCTIONS ---

# # def get_soup(url):
# #     """Fetches a URL and returns a BeautifulSoup object."""
# #     headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
# #     try:
# #         response = requests.get(url, headers=headers, timeout=25)
# #         response.raise_for_status()
# #         return BeautifulSoup(response.content, 'lxml')
# #     except requests.exceptions.RequestException as e:
# #         print(f"Error fetching {url}: {e}")
# #         return None

# # def clean_text(text, field_name=""):
# #     """Cleans common text patterns from scraped strings."""
# #     if not text:
# #         return None
# #     # Specific cleaning for codes to only remove the prefix
# #     if field_name in ["bse_code", "nse_code"]:
# #         return text.strip().replace('BSE:', '').replace('NSE:', '').strip()
# #     return text.strip().replace('₹', '').replace(',', '').replace('%', '').replace('Cr.', '').strip()

# # def parse_number(text):
# #     """Parses a string to a float, returning None on failure."""
# #     cleaned = clean_text(text)
# #     if cleaned in [None, '']:
# #         return None
# #     match = re.search(r'[-+]?\d*\.\d+|\d+', cleaned)
# #     if match:
# #         try:
# #             return float(match.group(0))
# #         except (ValueError, TypeError):
# #             return None
# #     return None

# # def get_calendar_sort_key(header_string):
# #     """Creates a sortable key (year, month) from a date string like 'Mar 2024'."""
# #     MONTH_MAP = {
# #         'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
# #         'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
# #     }
# #     try:
# #         month_str, year_str = header_string.strip().split()
# #         year = int(year_str)
# #         month = MONTH_MAP.get(month_str, 0)
# #         return (year, month)
# #     except (ValueError, KeyError, IndexError):
# #         try:
# #             return (int(header_string), 0)
# #         except (ValueError, TypeError):
# #              return (0, 0)

# # # --- PARSING FUNCTIONS ---

# # def process_industry_path(soup):
# #     """Parses the industry classification path and creates/gets DB objects."""
# #     peers_section = soup.select_one('section#peers')
# #     if not peers_section: return None
    
# #     path_paragraph = peers_section.select_one('p.sub:not(#benchmarks)')
# #     if not path_paragraph: return None
    
# #     path_links = path_paragraph.select('a')
# #     if not path_links: return None
        
# #     path_names = [link.get_text(strip=True).replace('&', 'and') for link in path_links]
# #     parent_obj, last_classification_obj = None, None
    
# #     for name in path_names:
# #         classification_obj, _ = IndustryClassification.objects.get_or_create(
# #             name=name, defaults={'parent': parent_obj}
# #         )
# #         parent_obj = last_classification_obj = classification_obj
        
# #     return last_classification_obj

# # def parse_website_link(soup):
# #     """
# #     Finds the main company website link from the top links section,
# #     reliably ignoring the BSE and NSE links.
# #     """
# #     company_links_div = soup.select_one('div.company-links')
# #     if not company_links_div:
# #         return None
    
# #     all_links = company_links_div.find_all('a', href=True)
# #     for link in all_links:
# #         href = link['href']
# #         # The correct website is the first one that is NOT a stock exchange link
# #         if 'bseindia.com' not in href and 'nseindia.com' not in href:
# #             return href
            
# #     return None # Return None if no suitable link is found

# # def parse_financial_table(soup, table_id):
# #     """Parses a financial table into a structured JSON object, sorted chronologically."""
# #     section = soup.select_one(f'section#{table_id}')
# #     if not section: return {}
# #     table = section.select_one('table.data-table')
# #     if not table: return {}

# #     original_headers = [th.get_text(strip=True) for th in table.select('thead th')][1:]
# #     if not original_headers: return {}
    
# #     sorted_headers = sorted(original_headers, key=get_calendar_sort_key, reverse=True)
    
# #     body_data = []
# #     for row in table.select('tbody tr'):
# #         cols = row.select('td')
# #         if not cols or 'sub' in row.get('class', []): continue
# #         row_name = cols[0].get_text(strip=True).replace('+', '').strip()
# #         if not row_name: continue
        
# #         original_values = [col.get_text(strip=True) for col in cols[1:]]
# #         value_map = dict(zip(original_headers, original_values))
        
# #         sorted_values = [value_map.get(h, '') for h in sorted_headers]
        
# #         body_data.append({'Description': row_name, 'values': sorted_values})
        
# #     return {'headers': sorted_headers, 'body': body_data}

# # def parse_shareholding_table(soup, table_id):
# #     """Parses shareholding data, sorted chronologically."""
# #     table = soup.select_one(f'div#{table_id} table.data-table')
# #     if not table: return {}
# #     original_headers = [th.get_text(strip=True) for th in table.select('thead th')][1:]
# #     sorted_headers = sorted(original_headers, key=get_calendar_sort_key, reverse=True)
    
# #     data = {}
# #     for row in table.select('tbody tr'):
# #         cols = row.select('td')
# #         if not cols or 'sub' in row.get('class', []): continue
# #         row_name = cols[0].get_text(strip=True).replace('+', '').strip()
# #         if not row_name: continue
        
# #         original_values = [col.get_text(strip=True) for col in cols[1:]]
# #         value_map = dict(zip(original_headers, original_values))
# #         row_data = {h: value_map.get(h, '') for h in sorted_headers}
# #         data[row_name] = row_data
        
# #     return data

# # def parse_growth_tables(soup):
# #     """Parses the four small compounded growth tables."""
# #     data = {}
# #     pl_section = soup.select_one('section#profit-loss')
# #     if not pl_section: return data

# #     tables = pl_section.select('table.ranges-table')
# #     for table in tables:
# #         title_elem = table.select_one('th')
# #         if title_elem:
# #             title = title_elem.get_text(strip=True).replace(':', '')
# #             table_data = {
# #                 cols[0].get_text(strip=True).replace(':', ''): cols[1].get_text(strip=True)
# #                 for row in table.select('tr')[1:] if len(cols := row.select('td')) == 2
# #             }
# #             data[title] = table_data
# #     return data

# # # --- MAIN DJANGO COMMAND ---

# # class Command(BaseCommand):
# #     help = 'Scrapes company fundamentals from screener.in, parses data in memory, and saves to the database.'

# #     def handle(self, *args, **options):
# #         self.stdout.write(self.style.SUCCESS("--- Starting On-the-Fly Fundamental Scraper ---"))
        
# #         company_urls_to_scrape = []
# #         for i in range(1, 100):
# #             list_url = f"https://www.screener.in/screens/515361/largecaptop-100midcap101-250smallcap251/?page={i}&limit=50"
# #             self.stdout.write(f"Fetching company list from page {i}...")
# #             list_soup = get_soup(list_url)
# #             if not list_soup: continue

# #             rows = list_soup.select('table.data-table tr[data-row-company-id]')
# #             if not rows:
# #                 self.stdout.write(self.style.WARNING("No more companies found. Stopping list scrape."))
# #                 break
            
# #             for row in rows:
# #                 link_tag = row.select_one('a')
# #                 if link_tag and link_tag.get('href'):
# #                     company_urls_to_scrape.append(f"https://www.screener.in{link_tag['href']}")
            
# #             time.sleep(1)

# #         self.stdout.write(self.style.SUCCESS(f"Found {len(company_urls_to_scrape)} companies to process."))

# #         for url in company_urls_to_scrape:
# #             try:
# #                 company_symbol = url.strip('/').split('/')[4]
# #                 self.stdout.write(f"\n--- Processing: {company_symbol} ({url}) ---")
                
# #                 soup = get_soup(url)
# #                 if not soup:
# #                     self.stdout.write(self.style.ERROR(f"Could not fetch HTML for {company_symbol}. Skipping."))
# #                     continue

# #                 company_name = (soup.select_one('h1.margin-0').get_text(strip=True) 
# #                                 if soup.select_one('h1.margin-0') else company_symbol)
                
# #                 # --- Replicated exact scraping logic from process_local_html.py ---
# #                 ratios_data = {li.select_one('.name').get_text(strip=True): li.select_one('.value').get_text(strip=True) 
# #                                for li in soup.select('#top-ratios li') if li.select_one('.name') and li.select_one('.value')}
                
# #                 bse_link = soup.select_one('a[href*="bseindia.com"]')
# #                 bse_code = clean_text(bse_link.get_text(strip=True), "bse_code") if bse_link else None
                
# #                 nse_link = soup.select_one('a[href*="nseindia.com"]')
# #                 nse_code = clean_text(nse_link.get_text(strip=True), "nse_code") if nse_link else None
# #                 # --- End of replicated logic ---

# #                 growth_tables = parse_growth_tables(soup)
# #                 industry_object = process_industry_path(soup)

# #                 defaults = {
# #                     'name': company_name,
# #                     'about': soup.select_one('.company-profile .about p').get_text(strip=True) if soup.select_one('.company-profile .about p') else None,
# #                     'website': parse_website_link(soup), # Using the new robust function
# #                     'bse_code': bse_code,
# #                     'nse_code': nse_code,
# #                     'market_cap': parse_number(ratios_data.get('Market Cap')),
# #                     'current_price': parse_number(ratios_data.get('Current Price')),
# #                     'high_low': clean_text(ratios_data.get('High / Low')),
# #                     'stock_pe': parse_number(ratios_data.get('Stock P/E')),
# #                     'book_value': parse_number(ratios_data.get('Book Value')),
# #                     'dividend_yield': parse_number(ratios_data.get('Dividend Yield')),
# #                     'roce': parse_number(ratios_data.get('ROCE')),
# #                     'roe': parse_number(ratios_data.get('ROE')),
# #                     'face_value': parse_number(ratios_data.get('Face Value')),
# #                     'pros': [li.get_text(strip=True) for li in soup.select('.pros ul li')],
# #                     'cons': [li.get_text(strip=True) for li in soup.select('.cons ul li')],
# #                     'quarterly_results': parse_financial_table(soup, 'quarters'),
# #                     'profit_loss_statement': parse_financial_table(soup, 'profit-loss'),
# #                     'balance_sheet': parse_financial_table(soup, 'balance-sheet'),
# #                     'cash_flow_statement': parse_financial_table(soup, 'cash-flow'),
# #                     'ratios': parse_financial_table(soup, 'ratios'),
# #                     'compounded_sales_growth': growth_tables.get('Compounded Sales Growth', {}),
# #                     'compounded_profit_growth': growth_tables.get('Compounded Profit Growth', {}),
# #                     'stock_price_cagr': growth_tables.get('Stock Price CAGR', {}),
# #                     'return_on_equity': growth_tables.get('Return on Equity', {}),
# #                     'shareholding_pattern': {'quarterly': parse_shareholding_table(soup, 'quarterly-shp')},
# #                     'industry_classification': industry_object,
# #                 }

# #                 obj, created = Company.objects.update_or_create(symbol=company_symbol, defaults=defaults)
# #                 action = "Created" if created else "Updated"
# #                 self.stdout.write(self.style.SUCCESS(f"Successfully {action} data for {company_name} ({company_symbol})"))

# #             except Exception as e:
# #                 self.stdout.write(self.style.ERROR(f"An unexpected error occurred for {company_symbol}: {e}"))
            
# #             finally:
# #                 time.sleep(1)

# #         self.stdout.write(self.style.SUCCESS("\n--- Scraping process finished. ---"))

# import requests
# import re
# import time
# import threading
# from concurrent.futures import ThreadPoolExecutor
# from bs4 import BeautifulSoup

# from django.core.management.base import BaseCommand
# from django.db import connection
# from fundamentals.models import Company, IndustryClassification

# # --- UTILITY AND HELPER FUNCTIONS (Unchanged) ---

# def get_soup(url):
#     """Fetches a URL and returns a BeautifulSoup object."""
#     headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
#     try:
#         response = requests.get(url, headers=headers, timeout=25)
#         response.raise_for_status()
#         return BeautifulSoup(response.content, 'lxml')
#     except requests.exceptions.RequestException as e:
#         # Error will be logged in the worker thread
#         return None

# def clean_text(text, field_name=""):
#     """Cleans common text patterns from scraped strings."""
#     if not text:
#         return None
#     if field_name in ["bse_code", "nse_code"]:
#         return text.strip().replace('BSE:', '').replace('NSE:', '').strip()
#     return text.strip().replace('₹', '').replace(',', '').replace('%', '').replace('Cr.', '').strip()

# def parse_number(text):
#     """Parses a string to a float, returning None on failure."""
#     cleaned = clean_text(text)
#     if cleaned in [None, '']:
#         return None
#     match = re.search(r'[-+]?\d*\.\d+|\d+', cleaned)
#     if match:
#         try:
#             return float(match.group(0))
#         except (ValueError, TypeError):
#             return None
#     return None

# def get_calendar_sort_key(header_string):
#     """Creates a sortable key (year, month) from a date string like 'Mar 2024'."""
#     MONTH_MAP = {
#         'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
#         'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
#     }
#     try:
#         month_str, year_str = header_string.strip().split()
#         year = int(year_str)
#         month = MONTH_MAP.get(month_str, 0)
#         return (year, month)
#     except (ValueError, KeyError, IndexError):
#         try:
#             return (int(header_string), 0)
#         except (ValueError, TypeError):
#             return (0, 0)

# # --- PARSING FUNCTIONS (Unchanged) ---

# def process_industry_path(soup):
#     """Parses the industry classification path and creates/gets DB objects."""
#     peers_section = soup.select_one('section#peers')
#     if not peers_section: return None
    
#     path_paragraph = peers_section.select_one('p.sub:not(#benchmarks)')
#     if not path_paragraph: return None
    
#     path_links = path_paragraph.select('a')
#     if not path_links: return None
        
#     path_names = [link.get_text(strip=True).replace('&', 'and') for link in path_links]
#     parent_obj, last_classification_obj = None, None
    
#     for name in path_names:
#         classification_obj, _ = IndustryClassification.objects.get_or_create(
#             name=name, defaults={'parent': parent_obj}
#         )
#         parent_obj = last_classification_obj = classification_obj
        
#     return last_classification_obj

# def parse_website_link(soup):
#     """Finds the main company website link, ignoring exchange links."""
#     company_links_div = soup.select_one('div.company-links')
#     if not company_links_div:
#         return None
    
#     all_links = company_links_div.find_all('a', href=True)
#     for link in all_links:
#         href = link['href']
#         if 'bseindia.com' not in href and 'nseindia.com' not in href:
#             return href
            
#     return None

# def parse_financial_table(soup, table_id):
#     """Parses a financial table into a structured JSON object, sorted chronologically."""
#     section = soup.select_one(f'section#{table_id}')
#     if not section: return {}
#     table = section.select_one('table.data-table')
#     if not table: return {}

#     original_headers = [th.get_text(strip=True) for th in table.select('thead th')][1:]
#     if not original_headers: return {}
    
#     sorted_headers = sorted(original_headers, key=get_calendar_sort_key, reverse=True)
    
#     body_data = []
#     for row in table.select('tbody tr'):
#         cols = row.select('td')
#         if not cols or 'sub' in row.get('class', []): continue
#         row_name = cols[0].get_text(strip=True).replace('+', '').strip()
#         if not row_name: continue
        
#         original_values = [col.get_text(strip=True) for col in cols[1:]]
#         value_map = dict(zip(original_headers, original_values))
        
#         sorted_values = [value_map.get(h, '') for h in sorted_headers]
        
#         body_data.append({'Description': row_name, 'values': sorted_values})
        
#     return {'headers': sorted_headers, 'body': body_data}


# def parse_shareholding_table(soup, table_id):
#     """Parses shareholding data, sorted chronologically."""
#     table = soup.select_one(f'div#{table_id} table.data-table')
#     if not table: return {}
#     original_headers = [th.get_text(strip=True) for th in table.select('thead th')][1:]
#     sorted_headers = sorted(original_headers, key=get_calendar_sort_key, reverse=True)
    
#     data = {}
#     for row in table.select('tbody tr'):
#         cols = row.select('td')
#         if not cols or 'sub' in row.get('class', []): continue
#         row_name = cols[0].get_text(strip=True).replace('+', '').strip()
#         if not row_name: continue
        
#         original_values = [col.get_text(strip=True) for col in cols[1:]]
#         value_map = dict(zip(original_headers, original_values))
#         row_data = {h: value_map.get(h, '') for h in sorted_headers}
#         data[row_name] = row_data
        
#     return data

# def parse_growth_tables(soup):
#     """Parses the four small compounded growth tables."""
#     data = {}
#     pl_section = soup.select_one('section#profit-loss')
#     if not pl_section: return data

#     tables = pl_section.select('table.ranges-table')
#     for table in tables:
#         title_elem = table.select_one('th')
#         if title_elem:
#             title = title_elem.get_text(strip=True).replace(':', '')
#             table_data = {
#                 cols[0].get_text(strip=True).replace(':', ''): cols[1].get_text(strip=True)
#                 for row in table.select('tr')[1:] if len(cols := row.select('td')) == 2
#             }
#             data[title] = table_data
#     return data


# # --- MAIN DJANGO COMMAND ---

# class Command(BaseCommand):
#     help = 'Scrapes company fundamentals from screener.in using multiple thread' \
#     '' \
#     's, parses data, and saves to the database.'

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.lock = threading.Lock() # Lock for thread-safe console output

#     def add_arguments(self, parser):
#         parser.add_argument(
#             '--max-workers',
#             type=int,
#             default=10,
#             help='The maximum number of threads to use for fetching company data.'
#         )

#     def _scrape_and_save_company_data(self, url):
#         """Worker function to fetch, parse, and save data for a single company."""
#         company_symbol = None
#         try:
#             company_symbol = url.strip('/').split('/')[-1]
            
#             with self.lock:
#                 self.stdout.write(f"  [Thread] Processing: {company_symbol}")

#             soup = get_soup(url)
#             if not soup:
#                 raise ValueError(f"Could not fetch or parse HTML from {url}")

#             company_name = (soup.select_one('h1.margin-0').get_text(strip=True) 
#                             if soup.select_one('h1.margin-0') else company_symbol)
            
#             ratios_data = {li.select_one('.name').get_text(strip=True): li.select_one('.value').get_text(strip=True) 
#                            for li in soup.select('#top-ratios li') if li.select_one('.name') and li.select_one('.value')}
            
#             bse_link = soup.select_one('a[href*="bseindia.com"]')
#             bse_code = clean_text(bse_link.get_text(strip=True), "bse_code") if bse_link else None
            
#             nse_link = soup.select_one('a[href*="nseindia.com"]')
#             nse_code = clean_text(nse_link.get_text(strip=True), "nse_code") if nse_link else None

#             growth_tables = parse_growth_tables(soup)
#             industry_object = process_industry_path(soup)

#             defaults = {
#                 'name': company_name,
#                 'about': soup.select_one('.company-profile .about p').get_text(strip=True) if soup.select_one('.company-profile .about p') else None,
#                 'website': parse_website_link(soup),
#                 'bse_code': bse_code,
#                 'nse_code': nse_code,
#                 'market_cap': parse_number(ratios_data.get('Market Cap')),
#                 'current_price': parse_number(ratios_data.get('Current Price')),
#                 'high_low': clean_text(ratios_data.get('High / Low')),
#                 'stock_pe': parse_number(ratios_data.get('Stock P/E')),
#                 'book_value': parse_number(ratios_data.get('Book Value')),
#                 'dividend_yield': parse_number(ratios_data.get('Dividend Yield')),
#                 'roce': parse_number(ratios_data.get('ROCE')),
#                 'roe': parse_number(ratios_data.get('ROE')),
#                 'face_value': parse_number(ratios_data.get('Face Value')),
#                 'pros': [li.get_text(strip=True) for li in soup.select('.pros ul li')],
#                 'cons': [li.get_text(strip=True) for li in soup.select('.cons ul li')],
#                 'quarterly_results': parse_financial_table(soup, 'quarters'),
#                 'profit_loss_statement': parse_financial_table(soup, 'profit-loss'),
#                 'balance_sheet': parse_financial_table(soup, 'balance-sheet'),
#                 'cash_flow_statement': parse_financial_table(soup, 'cash-flow'),
#                 'ratios': parse_financial_table(soup, 'ratios'),
#                 'compounded_sales_growth': growth_tables.get('Compounded Sales Growth', {}),
#                 'compounded_profit_growth': growth_tables.get('Compounded Profit Growth', {}),
#                 'stock_price_cagr': growth_tables.get('Stock Price CAGR', {}),
#                 'return_on_equity': growth_tables.get('Return on Equity', {}),
#                 'shareholding_pattern': {'quarterly': parse_shareholding_table(soup, 'quarterly-shp')},
#                 'industry_classification': industry_object,
#             }

#             obj, created = Company.objects.update_or_create(symbol=company_symbol, defaults=defaults)
#             action = "Created" if created else "Updated"
            
#             with self.lock:
#                 self.stdout.write(self.style.SUCCESS(f"  [Thread] Successfully {action} data for {company_name} ({company_symbol})"))

#         except Exception as e:
#             with self.lock:
#                 self.stdout.write(self.style.ERROR(f"  [Thread] FAILED for {company_symbol or url}: {e}"))
#         finally:
#             # IMPORTANT: Close the database connection for this thread
#             connection.close()

#     def handle(self, *args, **options):
#         max_workers = options['max_workers']
#         self.stdout.write(self.style.SUCCESS(f"--- Starting Multi-Threaded Fundamental Scraper (Max Workers: {max_workers}) ---"))
        
#         company_urls_to_scrape = []
#         for i in range(1, 100):
#             list_url = f"https://www.screener.in/screens/515361/largecaptop-100midcap101-250smallcap251/?page={i}&limit=50"
#             self.stdout.write(f"Fetching company list from page {i}...")
#             list_soup = get_soup(list_url)
#             if not list_soup:
#                 self.stdout.write(self.style.WARNING(f"Could not fetch page {i}. Stopping."))
#                 break

#             rows = list_soup.select('table.data-table tr[data-row-company-id]')
#             if not rows:
#                 self.stdout.write(self.style.WARNING("No more companies found. Stopping list scrape."))
#                 break
            
#             for row in rows:
#                 link_tag = row.select_one('a')
#                 if link_tag and link_tag.get('href'):
#                     company_urls_to_scrape.append(f"https://www.screener.in{link_tag['href']}")
            
#             time.sleep(2) # Be polite to the server when fetching list pages

#         self.stdout.write(self.style.SUCCESS(f"\nFound {len(company_urls_to_scrape)} companies. Starting parallel processing..."))

#         # Use ThreadPoolExecutor to process URLs in parallel
#         with ThreadPoolExecutor(max_workers=max_workers) as executor:
#             executor.map(self._scrape_and_save_company_data, company_urls_to_scrape)

#         self.stdout.write(self.style.SUCCESS("\n--- Scraping process finished. ---"))

import requests
import re
import time
import threading
import random
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup

from django.core.management.base import BaseCommand
from django.db import connection
from fundamentals.models import Company, IndustryClassification

# --- NEW: ANTI-DETECTION CONFIGURATION ---
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0',
]


# --- UPDATED UTILITY AND HELPER FUNCTIONS ---

def get_soup(session, url, retries=3, backoff_factor=0.5, referer=None):
    """
    Fetches a URL using a session object with rotating headers and a retry mechanism.
    """
    # Choose a random User-Agent for this request
    headers = {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    if referer:
        headers['Referer'] = referer

    for attempt in range(retries):
        try:
            # PROXY INTEGRATION POINT:
            # proxies = {'http': 'http://user:pass@host:port', 'https': 'https://user:pass@host:port'}
            # response = session.get(url, headers=headers, timeout=25, proxies=proxies)
            
            response = session.get(url, headers=headers, timeout=25)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'lxml')
        except requests.exceptions.RequestException as e:
            if attempt < retries - 1:
                wait_time = backoff_factor * (2 ** attempt)
                # Using print here as stdout might be locked by another thread
                print(f"Request to {url} failed: {e}. Retrying in {wait_time:.2f}s... (Attempt {attempt + 1}/{retries})")
                time.sleep(wait_time)
            else:
                return None
    return None

# --- Other helper functions remain unchanged ---
# (clean_text, parse_number, get_calendar_sort_key, etc.)
# ... (rest of the parsing functions from previous answer) ...

def clean_text(text, field_name=""):
    """Cleans common text patterns from scraped strings."""
    if not text:
        return None
    if field_name in ["bse_code", "nse_code"]:
        return text.strip().replace('BSE:', '').replace('NSE:', '').strip()
    return text.strip().replace('₹', '').replace(',', '').replace('%', '').replace('Cr.', '').strip()

def parse_number(text):
    """Parses a string to a float, returning None on failure."""
    cleaned = clean_text(text)
    if cleaned in [None, '']:
        return None
    match = re.search(r'[-+]?\d*\.\d+|\d+', cleaned)
    if match:
        try:
            return float(match.group(0))
        except (ValueError, TypeError):
            return None
    return None

def get_calendar_sort_key(header_string):
    """Creates a sortable key (year, month) from a date string like 'Mar 2024'."""
    MONTH_MAP = {
        'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
        'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
    }
    try:
        month_str, year_str = header_string.strip().split()
        year = int(year_str)
        month = MONTH_MAP.get(month_str, 0)
        return (year, month)
    except (ValueError, KeyError, IndexError):
        try:
            return (int(header_string), 0)
        except (ValueError, TypeError):
            return (0, 0)

def process_industry_path(soup):
    """Parses the industry classification path and creates/gets DB objects."""
    peers_section = soup.select_one('section#peers')
    if not peers_section: return None
    
    path_paragraph = peers_section.select_one('p.sub:not(#benchmarks)')
    if not path_paragraph: return None
    
    path_links = path_paragraph.select('a')
    if not path_links: return None
        
    path_names = [link.get_text(strip=True).replace('&', 'and') for link in path_links]
    parent_obj, last_classification_obj = None, None
    
    for name in path_names:
        classification_obj, _ = IndustryClassification.objects.get_or_create(
            name=name, defaults={'parent': parent_obj}
        )
        parent_obj = last_classification_obj = classification_obj
        
    return last_classification_obj

def parse_website_link(soup):
    """Finds the main company website link, ignoring exchange links."""
    company_links_div = soup.select_one('div.company-links')
    if not company_links_div:
        return None
    
    all_links = company_links_div.find_all('a', href=True)
    for link in all_links:
        href = link['href']
        if 'bseindia.com' not in href and 'nseindia.com' not in href:
            return href
            
    return None

def parse_financial_table(soup, table_id):
    """Parses a financial table into a structured JSON object, sorted chronologically."""
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
    """Parses shareholding data, sorted chronologically."""
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
    """Parses the four small compounded growth tables."""
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
    help = 'Scrapes company fundamentals with anti-detection measures.'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lock = threading.Lock()

    def add_arguments(self, parser):
        parser.add_argument(
            '--max-workers', type=int, default=10,
            help='The maximum number of threads to use for fetching.'
        )

    def _scrape_and_save_company_data(self, args):
        """Worker function that now accepts a session and referer URL."""
        url, session, list_url_referer = args
        company_symbol = None
        try:
            company_symbol = url.strip('/').split('/')[-1]
            
            with self.lock:
                self.stdout.write(f"  [Thread] Processing: {company_symbol}")

            soup = get_soup(session, url, referer=list_url_referer)
            if not soup:
                raise ValueError(f"Could not fetch HTML from {url} after multiple retries.")

            # ... (All data parsing logic remains exactly the same) ...
            company_name = (soup.select_one('h1.margin-0').get_text(strip=True) 
                            if soup.select_one('h1.margin-0') else company_symbol)
            
            ratios_data = {li.select_one('.name').get_text(strip=True): li.select_one('.value').get_text(strip=True) 
                           for li in soup.select('#top-ratios li') if li.select_one('.name') and li.select_one('.value')}
            
            bse_link = soup.select_one('a[href*="bseindia.com"]')
            bse_code = clean_text(bse_link.get_text(strip=True), "bse_code") if bse_link else None
            
            nse_link = soup.select_one('a[href*="nseindia.com"]')
            nse_code = clean_text(nse_link.get_text(strip=True), "nse_code") if nse_link else None

            growth_tables = parse_growth_tables(soup)
            industry_object = process_industry_path(soup)

            defaults = {
                'name': company_name,
                'about': soup.select_one('.company-profile .about p').get_text(strip=True) if soup.select_one('.company-profile .about p') else None,
                'website': parse_website_link(soup),
                'bse_code': bse_code,
                'nse_code': nse_code,
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
                'shareholding_pattern': {'quarterly': parse_shareholding_table(soup, 'quarterly-shp')},
                'industry_classification': industry_object,
            }

            obj, created = Company.objects.update_or_create(symbol=company_symbol, defaults=defaults)
            action = "Created" if created else "Updated"
            
            with self.lock:
                self.stdout.write(self.style.SUCCESS(f"  [Thread] Successfully {action} data for {company_name}"))

        except Exception as e:
            with self.lock:
                self.stdout.write(self.style.ERROR(f"  [Thread] FAILED for {company_symbol or url}: {e}"))
        finally:
            # Add a small, randomized delay to mimic human behavior
            time.sleep(random.uniform(1, 3))
            connection.close()

    def handle(self, *args, **options):
        max_workers = options['max_workers']
        self.stdout.write(self.style.SUCCESS(f"--- Starting Scraper (Max Workers: {max_workers}) ---"))
        
        company_urls_to_scrape = []
        
        # Create a single session to handle cookies and connection pooling
        with requests.Session() as session:
            for i in range(1, 100):
                list_url = f"https://www.screener.in/screens/515361/largecaptop-100midcap101-250smallcap251/?page={i}&limit=50"
                self.stdout.write(f"Fetching company list from page {i}...")
                
                # We pass the session to get_soup
                list_soup = get_soup(session, list_url) 
                
                if not list_soup:
                    self.stdout.write(self.style.ERROR(f"Could not fetch page {i}. Stopping list scrape."))
                    break

                rows = list_soup.select('table.data-table tr[data-row-company-id]')
                if not rows:
                    self.stdout.write(self.style.WARNING("No more companies found. Stopping."))
                    break
                
                for row in rows:
                    link_tag = row.select_one('a')
                    if link_tag and link_tag.get('href'):
                        # Store the page URL along with the company URL to use as a 'Referer'
                        company_url = f"https://www.screener.in{link_tag['href']}"
                        company_urls_to_scrape.append((company_url, list_url))
                
                time.sleep(random.uniform(2, 4)) # Randomize delay between list pages

            self.stdout.write(self.style.SUCCESS(f"\nFound {len(company_urls_to_scrape)} companies. Starting parallel processing..."))

            # Prepare arguments for the worker function
            worker_args = [(url, session, referer) for url, referer in company_urls_to_scrape]

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # We pass the session object to each worker
                executor.map(self._scrape_and_save_company_data, worker_args)

        self.stdout.write(self.style.SUCCESS("\n--- Scraping process finished. ---"))