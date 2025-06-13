# task.py
from celery import shared_task
from django.core.cache import cache
import asyncio
import httpx
import feedparser
from bs4 import BeautifulSoup
from datetime import datetime
import re
from collections import defaultdict
import time
import xml.etree.ElementTree as ET
from asgiref.sync import sync_to_async
from .models import CorporateAction, FinancialReport, NewsArticle, StockInFocus, ImportantAnnouncement, QuarterlyFinancials


# ==============================================================================
# SECTION 1: PARSING LOGIC
# Your original, synchronous XBRL parser classes are moved here.
# They don't need changes as they only process text data already in memory.
# ==============================================================================

class AnnualXBRLParser:
    """Parses Annual XBRL files and structures the financial data."""
    def __init__(self, xml_content):
        self.xml_content = xml_content
        self.statement_concepts = {
            'Statement of Profit and Loss': {'Revenue': ['RevenueFromOperations', 'OtherIncome'], 'Expenses': ['CostOfMaterialsConsumed', 'PurchasesOfStockInTrade', 'ChangesInInventoriesOfFinishedGoodsWorkInProgressAndStockInTrade', 'EmployeeBenefitsExpense', 'FinanceCosts', 'DepreciationAndAmortisationExpense', 'OtherExpenses'], 'TotalExpenses': None, 'ProfitLossBeforeExceptionalItemsAndTax': None, 'ExceptionalItems': None, 'ProfitLossBeforeTax': None, 'TaxExpense': ['CurrentTax', 'DeferredTax'], 'ProfitLossForPeriod': None, 'OtherComprehensiveIncome': None, 'TotalComprehensiveIncome': None, 'ProfitLoss': None, 'EarningsPerShare': ['BasicEarningsLossPerShare', 'DilutedEarningsLossPerShare']},
            'Balance Sheet': {'Assets': {'NonCurrentAssets': ['PropertyPlantAndEquipment', 'CapitalWorkInProgress', 'IntangibleAssets', 'IntangibleAssetsUnderDevelopment', 'FinancialAssetsNoncurrent', 'OtherNonCurrentAssets'], 'CurrentAssets': ['Inventories', 'FinancialAssetsCurrent', 'CurrentTaxAssetsNet', 'OtherCurrentAssets'],}, 'EquityAndLiabilities': {'Equity': ['EquityShareCapital', 'OtherEquity'], 'Liabilities': {'NonCurrentLiabilities': ['FinancialLiabilitiesNoncurrent', 'ProvisionsNoncurrent', 'DeferredTaxLiabilitiesNet', 'OtherNonCurrentLiabilities'], 'CurrentLiabilities': ['FinancialLiabilitiesCurrent', 'OtherCurrentLiabilities', 'ProvisionsCurrent', 'CurrentTaxLiabilitiesNet']}}},
            'Statement of Cash Flows': {'CashFlowsFromUsedInOperatingActivities': ['ProfitLossBeforeTax', 'AdjustmentsForDepreciationAndAmortisationExpense', 'AdjustmentsForFinanceCosts', 'AdjustmentsForInterestIncome', 'OperatingProfitBeforeWorkingCapitalChanges', 'AdjustmentsForTradeReceivables', 'AdjustmentsForInventories', 'AdjustmentsForTradePayables', 'AdjustmentsForOtherFinancialAndNonFinancialItems', 'CashGeneratedFromOperations', 'IncomeTaxesPaidNet',], 'CashFlowsFromUsedInInvestingActivities': ['PaymentsForPropertyPlantAndEquipment', 'ProceedsFromSaleOfPropertyPlantAndEquipment', 'InterestReceived', 'DividendsReceived'], 'CashFlowsFromUsedInFinancingActivities': ['ProceedsFromIssueOfEquityShares', 'ProceedsFromBorrowings', 'RepaymentsOfBorrowings', 'InterestPaid', 'DividendPaid'], 'NetIncreaseDecreaseInCashAndCashEquivalents': None, 'CashAndCashEquivalentsAtBeginningOfPeriod': None, 'CashAndCashEquivalentsAtEndOfPeriod': None}
        }
        self.namespaces = {'xbrli': 'http://www.xbrl.org/2003/instance'}

    def _parse_xbrl(self):
        try:
            root = ET.fromstring(self.xml_content.encode('utf-8'))
        except ET.ParseError as e: return []
        contexts, facts = {}, []
        for context in root.findall('xbrli:context', self.namespaces):
            period = context.find('xbrli:period', self.namespaces)
            contexts[context.attrib['id']] = {'period': (period.find('xbrli:instant') or period.find('xbrli:endDate')).text}
        for elem in root:
            if '}' in elem.tag and elem.tag.split('}')[0].strip('{') != self.namespaces['xbrli']:
                context_ref = elem.attrib.get('contextRef')
                if context_ref and context_ref in contexts:
                    try: value = float(elem.text)
                    except (ValueError, TypeError): value = 0.0
                    facts.append({'Concept': elem.tag.split('}')[-1], 'Period': contexts[context_ref]['period'], 'Value': value})
        return facts

    def _group_financial_data(self, all_data):
        all_dates = sorted(list(set(d['Period'] for d in all_data)), reverse=True)
        current_date, prior_date = (all_dates[0] if all_dates else None), (all_dates[1] if len(all_dates) > 1 else None)
        reports, facts_by_concept = {'periods': {'current': current_date, 'prior': prior_date}, 'statements': {}}, defaultdict(dict)
        for fact in all_data: facts_by_concept[fact['Concept']][fact['Period']] = fact['Value']
        def build_statement(concepts):
            result = []
            for concept, children in concepts.items():
                if isinstance(children, list): children = {child: None for child in children}
                pretty_concept = ' '.join(re.findall('[A-Z][^A-Z]*', concept.replace('UsedIn', '')))
                fact_data = {'Concept': pretty_concept, 'current': facts_by_concept.get(concept, {}).get(current_date), 'prior': facts_by_concept.get(concept, {}).get(prior_date), 'children': build_statement(children) if children else None}
                if fact_data['current'] is not None or fact_data['prior'] is not None or (fact_data.get('children') and len(fact_data['children']) > 0):
                    if fact_data.get('current') is None and fact_data.get('prior') is None: fact_data.pop('current', None); fact_data.pop('prior', None)
                    result.append(fact_data)
            return result
        for name, concepts in self.statement_concepts.items(): reports['statements'][name] = build_statement(concepts)
        return reports

    def get_structured_data(self):
        flat_facts = self._parse_xbrl()
        return self._group_financial_data(flat_facts) if flat_facts else {}


class QuarterlyXBRLParser:
    """A dedicated parser for quarterly Ind-AS XBRL results files."""
    def __init__(self, xml_content):
        self.xml_content = xml_content.encode('utf-8')
        self.contexts = {}
        self.facts = {"general": {}, "statements": {}}

    def parse(self):
        """Main method to parse the document and return structured data."""
        try:
            root = ET.fromstring(self.xml_content)
        except ET.ParseError:
            return None
        self._parse_contexts(root)
        self._extract_facts(root)
        return self.facts

    def _parse_contexts(self, root):
        """Parses all context nodes to map context IDs to their period and dimension info."""
        for context_node in root.findall('.//{http://www.xbrl.org/2003/instance}context'):
            context_id = context_node.attrib['id']
            period_node = context_node.find('.//{http://www.xbrl.org/2003/instance}period')
            
            instant_node = period_node.find('.//{http://www.xbrl.org/2003/instance}instant')
            start_date_node = period_node.find('.//{http://www.xbrl.org/2003/instance}startDate')
            end_date_node = period_node.find('.//{http://www.xbrl.org/2003/instance}endDate')

            if instant_node is not None:
                period_label = f"As at {instant_node.text}"
                end_date = instant_node.text
            else:
                period_label = f"From {start_date_node.text} to {end_date_node.text}"
                end_date = end_date_node.text
            
            self.contexts[context_id] = {
                'period_label': period_label,
                'end_date': end_date,
                'explicit_members': {}
            }
            
            for member in context_node.findall('.//{http://xbrl.org/2006/xbrldi}explicitMember'):
                dimension = member.attrib['dimension'].split(':')[-1]
                member_value = member.text.split(':')[-1]
                self.contexts[context_id]['explicit_members'][dimension] = member_value

    def _extract_facts(self, root):
        """Extracts all facts from the document and categorizes them."""
        numeric_facts = []
        detail_descriptions = {}
        
        for elem in root:
            if 'contextRef' not in elem.attrib:
                continue

            concept = elem.tag.split('}')[-1]
            context_ref = elem.attrib['contextRef']
            value = (elem.text or '').strip()
            context = self.contexts.get(context_ref)

            if not context:
                continue
            
            # Store descriptions for detailed facts
            if concept.startswith('DescriptionOf'):
                detail_descriptions[context_ref] = value
                continue
            
            decimals = elem.attrib.get('decimals')
            is_numeric = decimals is not None and value and value.replace('.', '', 1).replace('-', '', 1).isdigit()

            if is_numeric:
                numeric_facts.append({
                    'concept': concept, 
                    'value': float(value), 
                    'decimals': decimals, 
                    'context_ref': context_ref
                })
            elif not context['explicit_members']:
                # Store non-numeric, general facts
                self.facts['general'][concept] = value
        
        self._group_numeric_facts(numeric_facts, detail_descriptions)

    def _group_numeric_facts(self, numeric_facts, detail_descriptions):
        """Groups numeric facts into main statements and their detailed line items."""
        grouped = defaultdict(lambda: {'main': [], 'details': []})
        
        for fact in numeric_facts:
            context = self.contexts.get(fact['context_ref'])
            fact_data = {**fact, 'context': context}
            
            if context.get('explicit_members'):
                # This is a detailed breakdown (e.g., a specific type of revenue)
                fact_data['description'] = detail_descriptions.get(fact['context_ref'], 'Detail')
                grouped[fact['concept']]['details'].append(fact_data)
            else:
                # This is a main line item
                grouped[fact['concept']]['main'].append(fact_data)
        
        self.facts['statements'] = dict(grouped)

# --- ASYNC DATABASE HELPERS ---
@sync_to_async
def db_update_or_create(model, defaults, **kwargs):
    model.objects.update_or_create(defaults=defaults, **kwargs)

@sync_to_async
def db_check_existing_urls(model, url_list):
    return set(model.objects.filter(source_url__in=url_list).values_list('source_url', flat=True))

@sync_to_async
def db_get_existing_urls(model, url_list):
    return set(model.objects.filter(source_url__in=url_list).values_list('source_url', flat=True))

async def update_annual_reports():
    rss_url, base_xbrl_url = "https://nsearchives.nseindia.com/content/RSS/Annual_Reports_XBRL.xml", "https://nsearchives.nseindia.com/corporate/xbrl/"
    print("[CELERY] Scraping Annual Reports")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(rss_url, timeout=30)
        feed = feedparser.parse(response.content)
        
        entries = feed.entries[:15]
        urls_to_check = [f"{base_xbrl_url}{e.get('link')}" for e in entries if e.get('link')]
        existing_urls = await db_check_existing_urls(FinancialReport, urls_to_check)

        new_entries = [e for e in entries if f"{base_xbrl_url}{e.get('link')}" not in existing_urls]
        if not new_entries: return

        async with httpx.AsyncClient(headers={'User-Agent': 'Mozilla/5.0'}) as client:
            tasks = [client.get(f"{base_xbrl_url}{e.get('link')}", timeout=30) for e in new_entries]
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
        save_tasks = []
        for response, entry in zip(responses, new_entries):
            if isinstance(response, httpx.Response) and response.status_code == 200:
                parser = AnnualXBRLParser(response.text)
                structured_data = parser.get_structured_data()
                if structured_data and structured_data.get('periods', {}).get('current'):
                    report_date = datetime.strptime(structured_data['periods']['current'], '%Y-%m-%d').date()
                    defaults = {'company_name': entry.get('title', 'Unknown'), 'report_date': report_date, 'structured_data': structured_data}
                    source_url = f"{base_xbrl_url}{entry.get('link')}"
                    save_tasks.append(db_update_or_create(FinancialReport, defaults=defaults, source_url=source_url))
        await asyncio.gather(*save_tasks)
    except Exception as e:
        print(f"[CELERY] ERROR updating annual reports: {e}")

async def update_quarterly_results():
    rss_url = "https://nsearchives.nseindia.com/content/RSS/corporatefilings.xml"
    print("[CELERY] Scraping Quarterly Results")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(rss_url, timeout=30)
        feed = feedparser.parse(response.content)

        entries = [e for e in feed.entries if 'Financial Results' in next((d.get('value', '') for d in e.get('tags', [])), '')]
        urls_to_check = [next((l.get('href', '') for l in e.get('links', []) if l.get('href','').lower().endswith('.xml')), None) for e in entries]
        urls_to_check = [url for url in urls_to_check if url]
        existing_urls = await db_check_existing_urls(QuarterlyFinancials, urls_to_check)

        new_entries = []
        links_to_fetch = []
        for entry in entries:
            link = next((l.get('href', '') for l in entry.get('links', []) if l.get('href','').lower().endswith('.xml')), None)
            if link and link not in existing_urls:
                new_entries.append(entry)
                links_to_fetch.append(link)

        if not new_entries: return
        
        async with httpx.AsyncClient(headers={'User-Agent': 'Mozilla/5.0'}) as client:
            tasks = [client.get(link, timeout=30) for link in links_to_fetch]
            responses = await asyncio.gather(*tasks, return_exceptions=True)

        save_tasks = []
        for response, entry in zip(responses, new_entries):
            if isinstance(response, httpx.Response) and response.status_code == 200:
                # 1. Instantiate the parser with the downloaded text
                parser = QuarterlyXBRLParser(response.text)
                
                # 2. Call the parse method to get the structured data
                parsed_data = parser.parse()

                if parsed_data and parsed_data.get('general', {}).get('Symbol'):
                    # 3. Find the primary reporting period context
                    main_context = next((c for c in parser.contexts.values() if not c.get('explicit_members') and c.get('end_date')), None)
                    if main_context:
                        # 4. Prepare data for database insertion
                        defaults = {
                            'company_name': parsed_data['general'].get('NameOfTheCompany', entry.title),
                            'period_end_date': datetime.strptime(main_context['end_date'], '%Y-%m-%d').date(),
                            'structured_data': parsed_data
                        }
                        source_url = next((l.get('href', '') for l in entry.get('links', []) if l.get('href','').lower().endswith('.xml')), None)
                        
                        # 5. Create an async task to save the data
                        if source_url:
                            save_tasks.append(db_update_or_create(
                                QuarterlyFinancials, 
                                defaults=defaults, 
                                symbol=parsed_data['general']['Symbol'], 
                                source_url=source_url
                            ))
                            
        # 6. Execute all database save tasks concurrently
        await asyncio.gather(*save_tasks)
    except Exception as e:
        print(f"[CELERY] ERROR updating quarterly results: {e}")

async def update_corporate_actions():
    financial_url = "https://nsearchives.nseindia.com/content/RSS/Corporate_action.xml"
    print("[CELERY] Scraping Corporate Actions")
    try:
        async with httpx.AsyncClient(headers={'User-Agent': 'Mozilla/5.0'}) as client:
            response = await client.get(financial_url, timeout=20)
        
        feed = feedparser.parse(response.content)
        save_tasks = []
        for entry in feed.entries:
            desc = entry.get("description", "")
            details_dict = {item.split(':')[0].strip(): item.split(':')[1].strip() for item in desc.split('|') if ':' in item}
            company_name = entry.title.split(' - Ex-Date:')[0].strip()
            purpose = details_dict.get('PURPOSE', '').upper()
            action_type = 'Financial'
            if 'DIVIDEND' in purpose: action_type = 'Dividend'
            elif 'DEMERGER' in purpose: action_type = 'Demerger'
            elif 'SPLIT' in purpose: action_type = 'Stock Split'
            elif 'BONUS' in purpose: action_type = 'Bonus'
            ex_date_str = entry.title.split('Ex-Date: ')[-1].strip() if 'Ex-Date: ' in entry.title else None
            ex_date = datetime.strptime(ex_date_str, '%d-%b-%Y').date() if ex_date_str else None
            defaults = {'company_name': company_name, 'category': 'Financial', 'action_type': action_type, 'description': desc, 'ex_date': ex_date, 'details': details_dict}
            save_tasks.append(db_update_or_create(CorporateAction, defaults=defaults, link=entry.link, subject=entry.title))
        
        await asyncio.gather(*save_tasks)
    except Exception as e:
        print(f"[CELERY] ERROR updating corporate actions: {e}")

@shared_task
def update_all_data_task():
    print(f"--- [CELERY TASK] Starting scheduled data update at {datetime.now()} ---")
    
    async def run_all_updates():
        await asyncio.gather(
            update_corporate_actions(),
            update_annual_reports(),
            update_quarterly_results()
        )

    asyncio.run(run_all_updates())
    
    cache.clear()
    print("--- [CELERY TASK] Caches cleared. Update cycle finished. ---")
    return "Data update cycle completed successfully."