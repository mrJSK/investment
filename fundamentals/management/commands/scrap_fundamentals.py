# fundamentals/management/commands/scrape_fundamentals.py

import requests
import re
import time
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from fundamentals.models import Company, IndustryClassification

# --- UTILITY AND HELPER FUNCTIONS ---

def get_soup(url):
    """Fetches a URL and returns a BeautifulSoup object."""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    try:
        response = requests.get(url, headers=headers, timeout=25)
        response.raise_for_status()
        return BeautifulSoup(response.content, 'lxml')
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def clean_text(text, field_name=""):
    """Cleans common text patterns from scraped strings."""
    if not text:
        return None
    # Specific cleaning for codes to only remove the prefix
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

# --- PARSING FUNCTIONS ---

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
    """
    Finds the main company website link from the top links section,
    reliably ignoring the BSE and NSE links.
    """
    company_links_div = soup.select_one('div.company-links')
    if not company_links_div:
        return None
    
    all_links = company_links_div.find_all('a', href=True)
    for link in all_links:
        href = link['href']
        # The correct website is the first one that is NOT a stock exchange link
        if 'bseindia.com' not in href and 'nseindia.com' not in href:
            return href
            
    return None # Return None if no suitable link is found

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
    help = 'Scrapes company fundamentals from screener.in, parses data in memory, and saves to the database.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("--- Starting On-the-Fly Fundamental Scraper ---"))
        
        company_urls_to_scrape = []
        for i in range(1, 2):
            list_url = f"https://www.screener.in/screens/515361/largecaptop-100midcap101-250smallcap251/?page={i}&limit=50"
            self.stdout.write(f"Fetching company list from page {i}...")
            list_soup = get_soup(list_url)
            if not list_soup: continue

            rows = list_soup.select('table.data-table tr[data-row-company-id]')
            if not rows:
                self.stdout.write(self.style.WARNING("No more companies found. Stopping list scrape."))
                break
            
            for row in rows:
                link_tag = row.select_one('a')
                if link_tag and link_tag.get('href'):
                    company_urls_to_scrape.append(f"https://www.screener.in{link_tag['href']}")
            
            time.sleep(2)

        self.stdout.write(self.style.SUCCESS(f"Found {len(company_urls_to_scrape)} companies to process."))

        for url in company_urls_to_scrape:
            try:
                company_symbol = url.strip('/').split('/')[4]
                self.stdout.write(f"\n--- Processing: {company_symbol} ({url}) ---")
                
                soup = get_soup(url)
                if not soup:
                    self.stdout.write(self.style.ERROR(f"Could not fetch HTML for {company_symbol}. Skipping."))
                    continue

                company_name = (soup.select_one('h1.margin-0').get_text(strip=True) 
                                if soup.select_one('h1.margin-0') else company_symbol)
                
                # --- Replicated exact scraping logic from process_local_html.py ---
                ratios_data = {li.select_one('.name').get_text(strip=True): li.select_one('.value').get_text(strip=True) 
                               for li in soup.select('#top-ratios li') if li.select_one('.name') and li.select_one('.value')}
                
                bse_link = soup.select_one('a[href*="bseindia.com"]')
                bse_code = clean_text(bse_link.get_text(strip=True), "bse_code") if bse_link else None
                
                nse_link = soup.select_one('a[href*="nseindia.com"]')
                nse_code = clean_text(nse_link.get_text(strip=True), "nse_code") if nse_link else None
                # --- End of replicated logic ---

                growth_tables = parse_growth_tables(soup)
                industry_object = process_industry_path(soup)

                defaults = {
                    'name': company_name,
                    'about': soup.select_one('.company-profile .about p').get_text(strip=True) if soup.select_one('.company-profile .about p') else None,
                    'website': parse_website_link(soup), # Using the new robust function
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
                self.stdout.write(self.style.SUCCESS(f"Successfully {action} data for {company_name} ({company_symbol})"))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"An unexpected error occurred for {company_symbol}: {e}"))
            
            finally:
                time.sleep(2)

        self.stdout.write(self.style.SUCCESS("\n--- Scraping process finished. ---"))
