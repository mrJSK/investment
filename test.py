import csv
import json
import os
import re
from bs4 import BeautifulSoup

# --- UTILITY FUNCTIONS ---

def clean_text(text):
    """Cleans text by stripping whitespace and removing unwanted characters."""
    if not text:
        return None
    # Remove currency symbols, commas, percentages, and "Cr." which is common
    return text.strip().replace('₹', '').replace(',', '').replace('%', '').replace('Cr.', '').strip()

def parse_number(text):
    """Converts cleaned text to a float, handling potential errors."""
    cleaned = clean_text(text)
    if cleaned in [None, '']:
        return None
    # Extract the numerical part from the cleaned string.
    match = re.search(r'[-+]?\d*\.\d+|\d+', cleaned)
    if match:
        try:
            return float(match.group(0))
        except (ValueError, TypeError):
            return None
    return None

# --- SCRAPING HELPER FUNCTIONS ---

def parse_financial_table(soup, table_id):
    """A generic function to parse financial tables like Quarters, P&L, etc."""
    table = soup.select_one(f'section#{table_id} table.data-table')
    if not table:
        return []

    headers = [th.get_text(strip=True) for th in table.select('thead th')][1:]
    data = []
    for row in table.select('tbody tr'):
        cols = row.select('td')
        if not cols or 'sub' in row.get('class', []): # Skip footer rows
            continue
        
        row_name_elem = cols[0]
        if not row_name_elem:
            continue
            
        row_name = row_name_elem.get_text(strip=True).replace('+', '').strip()
        if not row_name: # Skip empty rows
            continue

        row_data = {'Description': row_name}
        
        for i, col in enumerate(cols[1:]):
            if i < len(headers):
                row_data[headers[i]] = col.get_text(strip=True)
        data.append(row_data)
    return data

def parse_shareholding_table(soup, table_id):
    """Parses shareholding tables (quarterly or yearly)."""
    table = soup.select_one(f'div#{table_id} table.data-table')
    if not table:
        return {}

    headers = [th.get_text(strip=True) for th in table.select('thead th')][1:]
    data = {}
    for row in table.select('tbody tr'):
        cols = row.select('td')
        if not cols or 'sub' in row.get('class', []):
            continue
        
        row_name_elem = cols[0]
        if not row_name_elem:
            continue

        row_name = row_name_elem.get_text(strip=True).replace('+', '').strip()
        if not row_name:
            continue

        values = [col.get_text(strip=True) for col in cols[1:]]
        row_data = {headers[i]: values[i] for i in range(len(values))}
        data[row_name] = row_data
    return data

def parse_growth_tables(soup):
    """Parses all four compounded growth tables."""
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
                    key = cols[0].get_text(strip=True).replace(':', '')
                    value = cols[1].get_text(strip=True)
                    table_data[key] = value
            data[title] = table_data
    return data

def extract_document_links(soup, container_selector):
    """Extracts links from a specific document container."""
    container = soup.select_one(container_selector)
    if not container:
        return []
    
    links = []
    for a in container.select('ul.list-links li a'):
        link_data = {
            'text': ' '.join(a.get_text(strip=True, separator=' ').split()),
            'href': a.get('href')
        }
        links.append(link_data)
    return links

# --- MAIN SCRIPT LOGIC ---

def main():
    """Main function to extract data and save to CSV."""
    company_name = '5Paisa Capital'
    company_symbol = '5PAISA'
    file_path = os.path.join('visited_company_pages', '5PAISA.html')
    output_csv_file = '5paisa_data.csv'

    print(f"--- Processing {company_name} ({company_symbol}) from {file_path} ---")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        soup = BeautifulSoup(html_content, 'lxml')
    except FileNotFoundError:
        print(f"ERROR: HTML file not found at {file_path}")
        return

    if not soup:
        print("ERROR: Could not parse HTML.")
        return

    try:
        # Basic Info
        about_div = soup.select_one('.company-profile .about p') #
        about = about_div.get_text(strip=True) if about_div else None #
        
        website_link = soup.select_one('.company-links a:not([href*="bseindia.com"]):not([href*="nseindia.com"])') #
        website = website_link['href'] if website_link else None #

        bse_link = soup.select_one('a[href*="bseindia.com"]') #
        bse_code = bse_link.get_text(strip=True).replace('BSE:', '').strip() if bse_link else None #
        
        nse_link = soup.select_one('a[href*="nseindia.com"]') #
        nse_code = nse_link.get_text(strip=True).replace('NSE:', '').strip() if nse_link else None #

        # Ratios
        ratios_data = {} #
        for li in soup.select('#top-ratios li'): #
            name_elem = li.select_one('.name') #
            value_elem = li.select_one('.value') #
            if name_elem and value_elem:
                name = name_elem.get_text(strip=True) #
                value = value_elem.get_text(strip=True) #
                ratios_data[name] = value #

        # Pros and Cons
        pros = [li.get_text(strip=True) for li in soup.select('.pros ul li')] #
        cons = [li.get_text(strip=True) for li in soup.select('.cons ul li')] #

        # Growth tables
        growth_tables = parse_growth_tables(soup) #

        # Shareholding pattern
        shareholding = {
            'quarterly': parse_shareholding_table(soup, 'quarterly-shp'), #
            'yearly': parse_shareholding_table(soup, 'yearly-shp') #
        }

        # Documents
        annual_reports = extract_document_links(soup, 'div.annual-reports') #
        credit_ratings = extract_document_links(soup, 'div.credit-ratings') #

        # Consolidate all extracted data
        extracted_data = {
            'symbol': company_symbol,
            'name': company_name,
            'about': about,
            'website': website,
            'bse_code': bse_code,
            'nse_code': nse_code,
            'market_cap_cr': parse_number(ratios_data.get('Market Cap')), #
            'current_price': parse_number(ratios_data.get('Current Price')), #
            'high_low': clean_text(ratios_data.get('High / Low')), #
            'stock_pe': parse_number(ratios_data.get('Stock P/E')), #
            'book_value': parse_number(ratios_data.get('Book Value')), #
            'dividend_yield': parse_number(ratios_data.get('Dividend Yield')), #
            'roce': parse_number(ratios_data.get('ROCE')), #
            'roe': parse_number(ratios_data.get('ROE')), #
            'face_value': parse_number(ratios_data.get('Face Value')), #
            'pros': pros, #
            'cons': cons, #
            'quarterly_results': parse_financial_table(soup, 'quarters'), #
            'profit_loss_statement': parse_financial_table(soup, 'profit-loss'), #
            'balance_sheet': parse_financial_table(soup, 'balance-sheet'), #
            'cash_flow_statement': parse_financial_table(soup, 'cash-flow'), #
            'ratios_table': parse_financial_table(soup, 'ratios'), #
            'compounded_sales_growth': growth_tables.get('Compounded Sales Growth', {}), #
            'compounded_profit_growth': growth_tables.get('Compounded Profit Growth', {}), #
            'stock_price_cagr': growth_tables.get('Stock Price CAGR', {}), #
            'return_on_equity': growth_tables.get('Return on Equity', {}), #
            'shareholding_pattern': shareholding, #
            'annual_reports': annual_reports, #
            'credit_ratings': credit_ratings, #
        }
        
        # Prepare data for CSV by serializing complex types (lists/dicts) to JSON strings
        csv_ready_data = {}
        for key, value in extracted_data.items():
            if isinstance(value, (dict, list)):
                csv_ready_data[key] = json.dumps(value)
            else:
                csv_ready_data[key] = value

        # Write to CSV
        with open(output_csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=csv_ready_data.keys())
            writer.writeheader()
            writer.writerow(csv_ready_data)
        
        print(f"SUCCESS: Successfully extracted data and saved to {output_csv_file}")

    except Exception as e:
        import traceback
        print(f"ERROR: An error occurred while processing {company_name}: {e}")
        traceback.print_exc()


if __name__ == '__main__':
    main()