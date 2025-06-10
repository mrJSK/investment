# # # fundamentals/management/commands/process_local_html.py

# # import os
# # import re
# # from bs4 import BeautifulSoup
# # from django.core.management.base import BaseCommand
# # from fundamentals.models import Company # Make sure your app is named 'fundamentals'

# # # --- UTILITY FUNCTIONS ---

# # def clean_text(text):
# #     """Cleans text by stripping whitespace and removing unwanted characters."""
# #     if not text:
# #         return None
# #     return text.strip().replace('₹', '').replace(',', '').replace('%', '').replace('Cr.', '').strip()

# # def parse_number(text):
# #     """Converts cleaned text to a float, handling potential errors."""
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

# # # --- SCRAPING HELPER FUNCTIONS ---

# # def parse_financial_table(soup, table_id):
# #     """A generic function to parse financial tables like Quarters, P&L, etc."""
# #     section = soup.select_one(f'section#{table_id}')
# #     if not section:
# #         return []
# #     table = section.select_one('table.data-table')
# #     if not table:
# #         return []

# #     headers = [th.get_text(strip=True) for th in table.select('thead th')][1:]
# #     data = []
# #     for row in table.select('tbody tr'):
# #         cols = row.select('td')
# #         if not cols or 'sub' in row.get('class', []):
# #             continue
# #         row_name_elem = cols[0]
# #         if not row_name_elem:
# #             continue
# #         row_name = row_name_elem.get_text(strip=True).replace('+', '').strip()
# #         if not row_name:
# #             continue
# #         row_data = {'Description': row_name}
# #         for i, col in enumerate(cols[1:]):
# #             if i < len(headers):
# #                 row_data[headers[i]] = col.get_text(strip=True)
# #         data.append(row_data)
# #     return data

# # def parse_shareholding_table(soup, table_id):
# #     """Parses shareholding tables (quarterly or yearly)."""
# #     table = soup.select_one(f'div#{table_id} table.data-table')
# #     if not table:
# #         return {}
# #     headers = [th.get_text(strip=True) for th in table.select('thead th')][1:]
# #     data = {}
# #     for row in table.select('tbody tr'):
# #         cols = row.select('td')
# #         if not cols or 'sub' in row.get('class', []):
# #             continue
# #         row_name_elem = cols[0]
# #         if not row_name_elem:
# #             continue
# #         row_name = row_name_elem.get_text(strip=True).replace('+', '').strip()
# #         if not row_name:
# #             continue
# #         values = [col.get_text(strip=True) for col in cols[1:]]
# #         row_data = {headers[i]: values[i] for i in range(len(values))}
# #         data[row_name] = row_data
# #     return data

# # def parse_growth_tables(soup):
# #     """Parses all four compounded growth tables."""
# #     data = {}
# #     tables = soup.select('#profit-loss table.ranges-table')
# #     for table in tables:
# #         title_elem = table.select_one('th')
# #         if title_elem:
# #             title = title_elem.get_text(strip=True).replace(':', '')
# #             table_data = {}
# #             for row in table.select('tr')[1:]:
# #                 cols = row.select('td')
# #                 if len(cols) == 2:
# #                     key = cols[0].get_text(strip=True).replace(':', '')
# #                     value = cols[1].get_text(strip=True)
# #                     table_data[key] = value
# #             data[title] = table_data
# #     return data

# # def extract_document_links(soup, container_selector):
# #     """Extracts links from a specific document container."""
# #     container = soup.select_one(container_selector)
# #     if not container:
# #         return []
# #     links = []
# #     for a in container.select('ul.list-links li a'):
# #         link_data = {
# #             'text': ' '.join(a.get_text(strip=True, separator=' ').split()),
# #             'href': a.get('href')
# #         }
# #         links.append(link_data)
# #     return links

# # def extract_concall_links(soup):
# #     """Extracts links specifically from the concalls section."""
# #     container = soup.select_one('div.concalls')
# #     if not container:
# #         return []
    
# #     concalls = []
# #     for li in container.select('ul.list-links li'):
# #         date_elem = li.select_one('div.nowrap')
# #         date = date_elem.get_text(strip=True) if date_elem else "N/A"
        
# #         links = {}
# #         for a in li.select('a.concall-link'):
# #             link_type = a.get_text(strip=True)
# #             links[link_type] = a.get('href')
            
# #         if date != "N/A" and links:
# #             concalls.append({'date': date, 'links': links})
# #     return concalls


# # # --- MAIN DJANGO COMMAND ---

# # class Command(BaseCommand):
# #     help = 'Processes all local HTML files and saves the data to the database.'

# #     def handle(self, *args, **options):
# #         """Main command handler."""
# #         folder_path = 'visited_company_pages'
# #         if not os.path.exists(folder_path):
# #             self.stdout.write(self.style.ERROR(f"Folder not found: {folder_path}"))
# #             return

# #         html_files = [f for f in os.listdir(folder_path) if f.endswith('.html')]
# #         if not html_files:
# #             self.stdout.write(self.style.WARNING("No HTML files found in the directory."))
# #             return

# #         self.stdout.write(f"Found {len(html_files)} HTML files to process.")

# #         for filename in html_files:
# #             company_symbol = os.path.splitext(filename)[0]
# #             file_path = os.path.join(folder_path, filename)
            
# #             self.stdout.write(f"--- Processing {filename} for symbol: {company_symbol} ---")

# #             try:
# #                 with open(file_path, 'r', encoding='utf-8') as f:
# #                     soup = BeautifulSoup(f.read(), 'lxml')
                
# #                 # Extract basic info
# #                 name_elem = soup.select_one('h1.margin-0')
# #                 company_name = name_elem.get_text(strip=True) if name_elem else company_symbol

# #                 about_div = soup.select_one('.company-profile .about p')
# #                 about = about_div.get_text(strip=True) if about_div else None
                
# #                 website_link = soup.select_one('.company-links a:not([href*="bseindia.com"]):not([href*="nseindia.com"])')
# #                 website = website_link['href'] if website_link else None

# #                 bse_link = soup.select_one('a[href*="bseindia.com"]')
# #                 bse_code = bse_link.get_text(strip=True).replace('BSE:', '').strip() if bse_link else None
                
# #                 nse_link = soup.select_one('a[href*="nseindia.com"]')
# #                 nse_code = nse_link.get_text(strip=True).replace('NSE:', '').strip() if nse_link else None

# #                 # Extract ratios
# #                 ratios_data = {}
# #                 for li in soup.select('#top-ratios li'):
# #                     name_elem = li.select_one('.name')
# #                     value_elem = li.select_one('.value')
# #                     if name_elem and value_elem:
# #                         name = name_elem.get_text(strip=True)
# #                         value = value_elem.get_text(strip=True)
# #                         ratios_data[name] = value

# #                 # Extract Pros and Cons
# #                 pros = [li.get_text(strip=True) for li in soup.select('.pros ul li')]
# #                 cons = [li.get_text(strip=True) for li in soup.select('.cons ul li')]

# #                 # Extract growth tables
# #                 growth_tables = parse_growth_tables(soup)

# #                 # Extract shareholding patterns
# #                 shareholding = {
# #                     'quarterly': parse_shareholding_table(soup, 'quarterly-shp'),
# #                     'yearly': parse_shareholding_table(soup, 'yearly-shp')
# #                 }

# #                 # Extract documents and concalls
# #                 announcements = extract_document_links(soup, '#company-announcements-tab')
# #                 annual_reports = extract_document_links(soup, 'div.annual-reports')
# #                 credit_ratings = extract_document_links(soup, 'div.credit-ratings')
# #                 concalls = extract_concall_links(soup)

# #                 # Prepare data for the database model
# #                 defaults = {
# #                     'name': company_name,
# #                     'about': about,
# #                     'website': website,
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
# #                     'pros': pros,
# #                     'cons': cons,
# #                     'quarterly_results': parse_financial_table(soup, 'quarters'),
# #                     'profit_loss_statement': parse_financial_table(soup, 'profit-loss'),
# #                     'balance_sheet': parse_financial_table(soup, 'balance-sheet'),
# #                     'cash_flow_statement': parse_financial_table(soup, 'cash-flow'),
# #                     'ratios': parse_financial_table(soup, 'ratios'),
# #                     'compounded_sales_growth': growth_tables.get('Compounded Sales Growth', {}),
# #                     'compounded_profit_growth': growth_tables.get('Compounded Profit Growth', {}),
# #                     'stock_price_cagr': growth_tables.get('Stock Price CAGR', {}),
# #                     'return_on_equity': growth_tables.get('Return on Equity', {}),
# #                     'shareholding_pattern': shareholding,
# #                     'announcements': announcements,
# #                     'annual_reports': annual_reports,
# #                     'credit_ratings': credit_ratings,
# #                     'concalls': concalls,
# #                 }

# #                 # Update or create the record in the database
# #                 obj, created = Company.objects.update_or_create(symbol=company_symbol, defaults=defaults)
# #                 action = "Created" if created else "Updated"
# #                 self.stdout.write(self.style.SUCCESS(f"Successfully {action} data for {company_name}"))

# #             except Exception as e:
# #                 self.stdout.write(self.style.ERROR(f"Error processing {filename}: {e}"))
        
# #         self.stdout.write(self.style.SUCCESS("Processing of all local files finished."))

# # fundamentals/management/commands/process_local_html.py

# import os
# import re
# from bs4 import BeautifulSoup
# from django.core.management.base import BaseCommand
# from fundamentals.models import Company
# from decimal import Decimal

# # --- UTILITY FUNCTIONS ---
# def clean_text(text):
#     if not text: return None
#     return text.strip().replace('₹', '').replace(',', '').replace('%', '').replace('Cr.', '').strip()

# def parse_number(text):
#     cleaned = clean_text(text)
#     if cleaned in [None, '']: return None
#     match = re.search(r'[-+]?\d*\.\d+|\d+', cleaned)
#     if match:
#         try: return float(match.group(0))
#         except (ValueError, TypeError): return None
#     return None

# # --- SCRAPING HELPER FUNCTIONS ---
# def parse_industry_classification(soup):
#     peers_section = soup.select_one('section#peers')
#     if not peers_section: return None
#     path_paragraph = peers_section.select_one('p.sub:not(#benchmarks)')
#     if not path_paragraph: return None
#     path_links = path_paragraph.select('a')
#     if not path_links: return None
#     return ' > '.join([link.get_text(strip=True).replace('&', 'and') for link in path_links])

# def get_latest_quarterly_value(results, key):
#     if not results or not isinstance(results, list): return None
#     for quarter in reversed(results):
#         if quarter.get(key) and quarter.get(key) not in ['--', '']:
#             return parse_number(quarter.get(key))
#     return None

# def get_latest_financial_value(table_data, description):
#     if not table_data: return None
#     for row in table_data:
#         if row.get('Description') == description:
#             keys = list(row.keys())
#             if len(keys) > 1:
#                 latest_date_key = keys[-1]
#                 return parse_number(row[latest_date_key])
#     return None

# def calculate_debt_to_equity(balance_sheet_data):
#     if not balance_sheet_data: return None
#     borrowings = get_latest_financial_value(balance_sheet_data, 'Borrowings')
#     reserves = get_latest_financial_value(balance_sheet_data, 'Reserves')
#     equity_capital = get_latest_financial_value(balance_sheet_data, 'Equity Capital')
    
#     if borrowings is not None and reserves is not None and equity_capital is not None:
#         total_equity = equity_capital + reserves
#         if total_equity > 0:
#             return round(borrowings / total_equity, 2)
#     return None

# def parse_financial_table(soup, table_id):
#     section = soup.select_one(f'section#{table_id}')
#     if not section: return []
#     table = section.select_one('table.data-table')
#     if not table: return []
#     headers = [th.get_text(strip=True) for th in table.select('thead th')][1:]
#     data = []
#     for row in table.select('tbody tr'):
#         cols = row.select('td')
#         if not cols or 'sub' in row.get('class', []): continue
#         row_name = cols[0].get_text(strip=True).replace('+', '').strip()
#         if not row_name: continue
#         row_data = {'Description': row_name}
#         for i, col in enumerate(cols[1:]):
#             if i < len(headers): row_data[headers[i]] = col.get_text(strip=True)
#         data.append(row_data)
#     return data

# def parse_shareholding_table(soup, table_id):
#     table = soup.select_one(f'div#{table_id} table.data-table')
#     if not table: return {}
#     headers = [th.get_text(strip=True) for th in table.select('thead th')][1:]
#     data = {}
#     for row in table.select('tbody tr'):
#         cols = row.select('td')
#         if not cols or 'sub' in row.get('class', []): continue
#         row_name = cols[0].get_text(strip=True).replace('+', '').strip()
#         if not row_name: continue
#         values = [col.get_text(strip=True) for col in cols[1:]]
#         row_data = {headers[i]: values[i] for i in range(len(values))}
#         data[row_name] = row_data
#     return data

# def parse_growth_tables(soup):
#     data = {}
#     tables = soup.select('#profit-loss table.ranges-table')
#     for table in tables:
#         title_elem = table.select_one('th')
#         if title_elem:
#             title = title_elem.get_text(strip=True).replace(':', '')
#             table_data = {}
#             for row in table.select('tr')[1:]:
#                 cols = row.select('td')
#                 if len(cols) == 2: table_data[cols[0].get_text(strip=True).replace(':', '')] = cols[1].get_text(strip=True)
#             data[title] = table_data
#     return data

# def extract_document_links(soup, container_selector):
#     container = soup.select_one(container_selector)
#     if not container: return []
#     links = []
#     for a in container.select('ul.list-links li a'):
#         links.append({'text': ' '.join(a.get_text(strip=True, separator=' ').split()), 'href': a.get('href')})
#     return links

# def extract_concall_links(soup):
#     container = soup.select_one('div.concalls')
#     if not container: return []
#     concalls = []
#     for li in container.select('ul.list-links li'):
#         date = li.select_one('div.nowrap').get_text(strip=True) if li.select_one('div.nowrap') else "N/A"
#         links = {a.get_text(strip=True): a.get('href') for a in li.select('a.concall-link')}
#         if date != "N/A" and links: concalls.append({'date': date, 'links': links})
#     return concalls


# class Command(BaseCommand):
#     help = 'Processes local HTML files to populate company data, then builds peer comparison data.'

#     def handle(self, *args, **options):
#         self.stdout.write(self.style.SUCCESS("--- PHASE 1: Processing local HTML files to populate database ---"))
#         folder_path = 'visited_company_pages'
#         if not os.path.exists(folder_path):
#             self.stdout.write(self.style.ERROR(f"Folder not found: {folder_path}"))
#             return

#         html_files = [f for f in os.listdir(folder_path) if f.endswith('.html')]
#         self.stdout.write(f"Found {len(html_files)} HTML files to process.")

#         for filename in html_files:
#             company_symbol = os.path.splitext(filename)[0]
#             file_path = os.path.join(folder_path, filename)
#             self.stdout.write(f"Processing {filename}...")

#             try:
#                 with open(file_path, 'r', encoding='utf-8') as f: soup = BeautifulSoup(f.read(), 'lxml')
                
#                 name_elem = soup.select_one('h1.margin-0'); company_name = name_elem.get_text(strip=True) if name_elem else company_symbol
                
#                 ratios_data = {}
#                 for li in soup.select('#top-ratios li'):
#                     name_elem = li.select_one('.name'); value_elem = li.select_one('.value')
#                     if name_elem and value_elem: ratios_data[name_elem.get_text(strip=True)] = value_elem.get_text(strip=True)

#                 growth_tables = parse_growth_tables(soup)
                
#                 defaults = {
#                     'name': company_name,
#                     'about': soup.select_one('.company-profile .about p').get_text(strip=True) if soup.select_one('.company-profile .about p') else None,
#                     'website': soup.select_one('.company-links a:not([href*="bseindia.com"]):not([href*="nseindia.com"])')['href'] if soup.select_one('.company-links a:not([href*="bseindia.com"]):not([href*="nseindia.com"])') else None,
#                     'bse_code': clean_text(soup.select_one('a[href*="bseindia.com"]').get_text(strip=True)) if soup.select_one('a[href*="bseindia.com"]') else None,
#                     'nse_code': clean_text(soup.select_one('a[href*="nseindia.com"]').get_text(strip=True)) if soup.select_one('a[href*="nseindia.com"]') else None,
#                     'market_cap': parse_number(ratios_data.get('Market Cap')),
#                     'current_price': parse_number(ratios_data.get('Current Price')),
#                     'high_low': clean_text(ratios_data.get('High / Low')),
#                     'stock_pe': parse_number(ratios_data.get('Stock P/E')),
#                     'book_value': parse_number(ratios_data.get('Book Value')),
#                     'dividend_yield': parse_number(ratios_data.get('Dividend Yield')),
#                     'roce': parse_number(ratios_data.get('ROCE')),
#                     'roe': parse_number(ratios_data.get('ROE')),
#                     'face_value': parse_number(ratios_data.get('Face Value')),
#                     'pros': [li.get_text(strip=True) for li in soup.select('.pros ul li')],
#                     'cons': [li.get_text(strip=True) for li in soup.select('.cons ul li')],
#                     'quarterly_results': parse_financial_table(soup, 'quarters'),
#                     'profit_loss_statement': parse_financial_table(soup, 'profit-loss'),
#                     'balance_sheet': parse_financial_table(soup, 'balance-sheet'),
#                     'cash_flow_statement': parse_financial_table(soup, 'cash-flow'),
#                     'ratios': parse_financial_table(soup, 'ratios'),
#                     'compounded_sales_growth': growth_tables.get('Compounded Sales Growth', {}),
#                     'compounded_profit_growth': growth_tables.get('Compounded Profit Growth', {}),
#                     'stock_price_cagr': growth_tables.get('Stock Price CAGR', {}),
#                     'return_on_equity': growth_tables.get('Return on Equity', {}),
#                     'shareholding_pattern': {'quarterly': parse_shareholding_table(soup, 'quarterly-shp'), 'yearly': parse_shareholding_table(soup, 'yearly-shp')},
#                     'announcements': extract_document_links(soup, '#company-announcements-tab'),
#                     'annual_reports': extract_document_links(soup, 'div.annual-reports'),
#                     'credit_ratings': extract_document_links(soup, 'div.credit-ratings'),
#                     'concalls': extract_concall_links(soup),
#                     'industry_classification': parse_industry_classification(soup)
#                 }
                
#                 Company.objects.update_or_create(symbol=company_symbol, defaults=defaults)

#             except Exception as e:
#                 self.stdout.write(self.style.ERROR(f"Error during PHASE 1 for {filename}: {e}"))
        
#         self.stdout.write(self.style.SUCCESS("--- PHASE 1 Complete. ---"))

#         # --- PHASE 2: BUILD AND SAVE PEER COMPARISON DATA ---
#         self.stdout.write(self.style.SUCCESS("\n--- PHASE 2: Building peer comparison data ---"))
        
#         all_companies = list(Company.objects.all())
#         industry_groups = {}
#         for company in all_companies:
#             if company.industry_classification:
#                 industry_groups.setdefault(company.industry_classification, []).append(company)

#         self.stdout.write(f"Found {len(industry_groups)} unique industry groups.")
        
#         update_count = 0
#         for company in all_companies:
#             if not company.industry_classification:
#                 continue

#             peer_objects = [p for p in industry_groups.get(company.industry_classification, []) if p.symbol != company.symbol]
            
#             peer_comparison_data = []
#             for peer in peer_objects:
#                 cmp_bv = None
#                 if peer.current_price and peer.book_value and peer.book_value > 0:
#                     cmp_bv = round(float(peer.current_price) / float(peer.book_value), 2)
                
#                 # CORRECTED: Convert Decimal types to float for JSON serialization
#                 peer_dict = {
#                     "name": peer.name,
#                     "cmp": float(peer.current_price) if peer.current_price is not None else None,
#                     "pe": float(peer.stock_pe) if peer.stock_pe is not None else None,
#                     "mar_cap_cr": float(peer.market_cap) if peer.market_cap is not None else None,
#                     "div_yld_pct": float(peer.dividend_yield) if peer.dividend_yield is not None else None,
#                     "np_qtr_cr": get_latest_quarterly_value(peer.quarterly_results, 'Net Profit'),
#                     "sales_qtr_cr": get_latest_quarterly_value(peer.quarterly_results, 'Sales'),
#                     "roce_pct": float(peer.roce) if peer.roce is not None else None,
#                     "cmp_bv": cmp_bv,
#                     "debt_eq": calculate_debt_to_equity(peer.balance_sheet),
#                 }
#                 peer_comparison_data.append(peer_dict)

#             company.peer_comparison = peer_comparison_data
#             company.save(update_fields=['peer_comparison'])
#             update_count += 1

#         self.stdout.write(self.style.SUCCESS(f"--- PHASE 2 Complete. Updated peer data for {update_count} companies. ---"))


# fundamentals/management/commands/process_local_html.py

import os
import re
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from fundamentals.models import Company, IndustryClassification

# --- UTILITY FUNCTIONS ---
def clean_text(text):
    if not text: return None
    return text.strip().replace('₹', '').replace(',', '').replace('%', '').replace('Cr.', '').strip()

def parse_number(text):
    cleaned = clean_text(text)
    if cleaned in [None, '']: return None
    match = re.search(r'[-+]?\d*\.\d+|\d+', cleaned)
    if match:
        try: return float(match.group(0))
        except (ValueError, TypeError): return None
    return None

# --- ROBUST DATE SORTING HELPER ---
def get_calendar_sort_key(header_string):
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

# --- SCRAPING HELPER FUNCTIONS ---
def process_industry_path(soup):
    peers_section = soup.select_one('section#peers')
    if not peers_section: return None
    path_paragraph = peers_section.select_one('p.sub:not(#benchmarks)')
    if not path_paragraph: return None
    path_links = path_paragraph.select('a')
    if not path_links: return None
    path_names = [link.get_text(strip=True).replace('&', 'and') for link in path_links]
    parent_obj, last_classification_obj = None, None
    for name in path_names:
        classification_obj, _ = IndustryClassification.objects.get_or_create(name=name, parent=parent_obj)
        parent_obj = last_classification_obj = classification_obj
    return last_classification_obj

# --- HELPERS UPDATED FOR NEW DATA STRUCTURE ---
def get_latest_financial_value(table_data, description):
    """Gets the most recent value from the new {headers, body} structure."""
    if not table_data or 'body' not in table_data: return None
    for row in table_data['body']:
        if row.get('Description') == description:
            if row.get('values'):
                # The first value corresponds to the first (latest) header
                return parse_number(row['values'][0])
    return None

def calculate_debt_to_equity(balance_sheet_data):
    if not balance_sheet_data: return None
    borrowings = get_latest_financial_value(balance_sheet_data, 'Borrowings')
    reserves = get_latest_financial_value(balance_sheet_data, 'Reserves')
    equity_capital = get_latest_financial_value(balance_sheet_data, 'Equity Capital')
    if borrowings is not None and reserves is not None and equity_capital is not None:
        total_equity = equity_capital + reserves
        if total_equity > 0: return round(borrowings / total_equity, 2)
    return None

# --- PARSING FUNCTIONS UPDATED TO CREATE NEW STRUCTURE ---
def parse_financial_table(soup, table_id):
    """
    Parses a financial table into a new, order-guaranteed structure:
    { "headers": [sorted_list], "body": [{ "Description": "...", "values": [sorted_list] }] }
    """
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
        
        # Create a list of values in the correct sorted order
        sorted_values = [value_map.get(h, '') for h in sorted_headers]
        
        body_data.append({
            'Description': row_name,
            'values': sorted_values
        })
        
    return {'headers': sorted_headers, 'body': body_data}

def parse_shareholding_table(soup, table_id):
    # This function creates a different structure, but the sorting logic is the same
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
    tables = soup.select('#profit-loss table.ranges-table')
    for table in tables:
        title_elem = table.select_one('th')
        if title_elem:
            title = title_elem.get_text(strip=True).replace(':', '')
            table_data = {}
            for row in table.select('tr')[1:]:
                cols = row.select('td')
                if len(cols) == 2:
                    table_data[cols[0].get_text(strip=True).replace(':', '')] = cols[1].get_text(strip=True)
            data[title] = table_data
    return data
    
# --- MAIN DJANGO COMMAND ---
class Command(BaseCommand):
    help = 'Processes local HTML files to populate company and industry data, then builds peer comparisons.'

    def handle(self, *args, **options):
        # --- PHASE 1: PROCESS HTML FILES AND POPULATE DATABASE ---
        self.stdout.write(self.style.SUCCESS("--- PHASE 1: Processing local HTML files ---"))
        folder_path = 'visited_company_pages'
        if not os.path.exists(folder_path):
            self.stdout.write(self.style.ERROR(f"Folder not found: {folder_path}"))
            return
        html_files = [f for f in os.listdir(folder_path) if f.endswith('.html')]
        self.stdout.write(f"Found {len(html_files)} HTML files to process.")
        for filename in html_files:
            company_symbol = os.path.splitext(filename)[0]
            file_path = os.path.join(folder_path, filename)
            self.stdout.write(f"Processing {filename}...")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    soup = BeautifulSoup(f.read(), 'lxml')
                company_name = (soup.select_one('h1.margin-0').get_text(strip=True) 
                                if soup.select_one('h1.margin-0') else company_symbol)
                ratios_data = {li.select_one('.name').get_text(strip=True): li.select_one('.value').get_text(strip=True) 
                               for li in soup.select('#top-ratios li') if li.select_one('.name') and li.select_one('.value')}
                growth_tables = parse_growth_tables(soup)
                industry_object = process_industry_path(soup)
                defaults = {
                    'name': company_name,
                    'about': soup.select_one('.company-profile .about p').get_text(strip=True) if soup.select_one('.company-profile .about p') else None,
                    'website': soup.select_one('.company-links a:not([href*="bseindia.com"]):not([href*="nseindia.com"])')['href'] if soup.select_one('.company-links a:not([href*="bseindia.com"]):not([href*="nseindia.com"])') else None,
                    'bse_code': clean_text(soup.select_one('a[href*="bseindia.com"]').get_text(strip=True).replace('BSE:', '')) if soup.select_one('a[href*="bseindia.com"]') else None,
                    'nse_code': clean_text(soup.select_one('a[href*="nseindia.com"]').get_text(strip=True).replace('NSE:', '')) if soup.select_one('a[href*="nseindia.com"]') else None,
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
                    'industry_classification': industry_object,
                }
                Company.objects.update_or_create(symbol=company_symbol, defaults=defaults)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error processing {filename}: {e}"))
        self.stdout.write(self.style.SUCCESS("--- PHASE 1 Complete. ---"))
        # --- PHASE 2: BUILD AND SAVE PEER COMPARISON DATA ---
        self.stdout.write(self.style.SUCCESS("\n--- PHASE 2: Building peer comparison data ---"))
        all_companies = Company.objects.select_related('industry_classification').all()
        industry_groups = {}
        for company in all_companies:
            if company.industry_classification:
                industry_groups.setdefault(company.industry_classification.id, []).append(company)
        self.stdout.write(f"Found {len(industry_groups)} unique industry groups.")
        update_count = 0
        for company in all_companies:
            if not company.industry_classification:
                continue
            peer_objects = [p for p in industry_groups.get(company.industry_classification.id, []) if p.symbol != company.symbol]
            peer_comparison_data = []
            for peer in peer_objects:
                cmp_bv = None
                if peer.current_price and peer.book_value and peer.book_value > 0:
                    cmp_bv = round(float(peer.current_price) / float(peer.book_value), 2)
                peer_dict = {
                    "name": peer.name, "symbol": peer.symbol,
                    "cmp": float(peer.current_price) if peer.current_price is not None else None,
                    "pe": float(peer.stock_pe) if peer.stock_pe is not None else None,
                    "mar_cap_cr": float(peer.market_cap) if peer.market_cap is not None else None,
                    "div_yld_pct": float(peer.dividend_yield) if peer.dividend_yield is not None else None,
                    "np_qtr_cr": get_latest_financial_value(peer.quarterly_results, 'Net Profit'),
                    "sales_qtr_cr": get_latest_financial_value(peer.quarterly_results, 'Sales'),
                    "roce_pct": float(peer.roce) if peer.roce is not None else None,
                    "cmp_bv": cmp_bv, "debt_eq": calculate_debt_to_equity(peer.balance_sheet),
                }
                peer_comparison_data.append(peer_dict)
            company.peer_comparison = peer_comparison_data
            company.save(update_fields=['peer_comparison'])
            update_count += 1
        self.stdout.write(self.style.SUCCESS(f"--- PHASE 2 Complete. Updated peer data for {update_count} companies. ---"))