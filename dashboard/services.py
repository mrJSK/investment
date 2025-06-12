# dashboard/services.py
import time
import feedparser
import requests
import json
import re
import xml.etree.ElementTree as ET
from collections import defaultdict
from bs4 import BeautifulSoup
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from django.core.cache import cache
from datetime import datetime
from .models import CorporateAction, FinancialReport, NewsArticle, StockInFocus, ImportantAnnouncement, QuarterlyFinancials

# --- 1. Sentiment Analysis Model ---
try:
    print("Loading FinBERT sentiment analysis model...")
    model_name = "ProsusAI/finbert"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    classifier = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)
    print("FinBERT model loaded successfully.")
except Exception as e:
    print(f"CRITICAL ERROR: Could not load FinBERT model. {e}")
    classifier = None

def analyze_sentiment(text):
    """Analyzes sentiment using the loaded FinBERT model."""
    if not classifier or not text:
        return {"sentiment": "Neutral", "confidence": 0.0, "action": "Hold"}
    try:
        truncated_text = " ".join(text.split()[:400])
        inputs = tokenizer(truncated_text, truncation=True, max_length=512, return_tensors="pt")
        outputs = model(**inputs)
        scores = outputs.logits.softmax(dim=1)[0]
        labels = model.config.id2label
        top_idx = scores.argmax().item()
        sentiment_label = labels[top_idx].lower()
        confidence = round(scores[top_idx].item() * 100, 2)
        action = {"positive": "Buy", "neutral": "Hold", "negative": "Sell"}.get(sentiment_label, "Hold")
        return {"sentiment": sentiment_label.capitalize(), "confidence": confidence, "action": action}
    except Exception as e:
        print(f"Error during sentiment analysis: {e}")
        return {"sentiment": "Neutral", "confidence": 0.0, "action": "Hold"}


# --- 2. Market News Service (Database-Driven) ---

def scrape_headlines_from_main_page():
    """Scrapes news headlines, links, and publication times from the source."""
    market_url = "https://www.cnbctv18.com/market/"
    print(f"Fetching headlines from main page: {market_url}")
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(market_url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Could not download the main market page. {e}")
        return []
    all_news, scraped_links = [], set()
    def clean_timestamp(ts_text):
        if not ts_text: return "Timestamp not found"
        return re.sub(r'\s*\d+\s+Min Read.*$', '', ts_text).strip()
    top_news_section = soup.select_one("section.mrkt-top-widget.common-mkt-css")
    if top_news_section:
        for a in top_news_section.select("a"):
            link = a.get("href", "")
            if link and link not in scraped_links:
                full_url = f"https://www.cnbctv18.com{link}" if link.startswith("/") else link
                title = (a.find(['h3', 'h4']) or a).get_text(strip=True)
                timestamp_tag = a.find("div", class_="mkt-ts")
                timestamp_str = clean_timestamp(timestamp_tag.get_text(strip=True)) if timestamp_tag else "N/A"
                if title:
                    all_news.append({"title": title, "link": full_url, "publication_time": timestamp_str})
                    scraped_links.add(link)
    timeline_items = soup.select("ul.live-mrkt-timeline li.live-mrkt-item")
    for item in timeline_items:
        link_tag = item.select_one("a.live-mrkt-exp")
        if link_tag and (link := link_tag.get("href", "")) and link not in scraped_links and 'cnbctv18.com' in link:
            title = link_tag.get_text(strip=True)
            timestamp_tag = item.find("div", class_="live-mrkt-time")
            timestamp_str = clean_timestamp(timestamp_tag.get_text(strip=True)) if timestamp_tag else "N/A"
            if title:
                all_news.append({"title": title, "link": link, "publication_time": timestamp_str})
                scraped_links.add(link)
    print(f"Found {len(all_news)} unique article links to process.")
    return all_news

def extract_full_text_from_article(article_url):
    """Downloads and extracts the body text of a single news article."""
    print(f"  -> Fetching full text from: {article_url}")
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(article_url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
    except requests.exceptions.RequestException as e:
        return f"Could not download article: {e}"
    article_body_tag = None
    content_selectors = ['div.narticle-data', 'div.article-content', 'div.story-content', 'div.articleWrap', 'div.entry-content', 'article.post', 'article']
    for selector in content_selectors:
        article_body_tag = soup.select_one(selector)
        if article_body_tag: break
    if article_body_tag:
        for s in ['.advertisement', '.related-articles', 'aside', '.social-share', '.tags', 'figure']:
            for tag in article_body_tag.select(s): tag.decompose()
        meaningful_paragraphs = [p.get_text(strip=True) for p in article_body_tag.find_all('p') if len(p.get_text(strip=True).split()) > 5]
        full_text = '\n\n'.join(meaningful_paragraphs) if meaningful_paragraphs else article_body_tag.get_text(separator='\n\n', strip=True)
        if "Also Read:" in full_text: full_text = full_text.split("Also Read:")[0].strip()
        elif "Also, Watch" in full_text: full_text = full_text.split("Also, Watch")[0].strip()
        return full_text
    return "Article content could not be extracted."

def parse_stocks_to_watch(full_text):
    """Parses the text of 'Stocks to Watch' articles into individual stock snippets."""
    print("  -> Parsing 'Stocks to Watch' article...")
    stock_snippets = [snippet.strip() for snippet in full_text.split('|') if snippet.strip()]
    parsed_stocks = []
    for snippet in stock_snippets:
        parts = snippet.split('\n', 1)
        stock_name = parts[0].strip()
        news_text = parts[1].strip() if len(parts) > 1 else ""
        if not stock_name or not news_text: continue
        sentiment_data = analyze_sentiment(news_text)
        parsed_stocks.append({"stock_name": stock_name, "text": news_text, **sentiment_data})
    print(f"  -> Parsed into {len(parsed_stocks)} individual stock snippets.")
    return parsed_stocks

def scrape_and_store_news():
    """Orchestrates scraping and saves results to the database."""
    articles_to_process = scrape_headlines_from_main_page()
    processed_count = 0
    for article_data in articles_to_process:
        if NewsArticle.objects.filter(link=article_data['link']).exists():
            continue
        print(f"Processing new article: {article_data['title']}")
        full_text = extract_full_text_from_article(article_data['link'])
        if "could not be extracted" in full_text or "Could not download" in full_text: continue
        is_stw = "stocks to watch" in article_data['title'].lower()
        sentiment_data = {"sentiment": "Neutral", "confidence": 0.0, "action": "Hold"} if is_stw else analyze_sentiment(full_text)
        db_article, created = NewsArticle.objects.update_or_create(
            link=article_data['link'],
            defaults={'headline': article_data['title'], 'publication_time_str': article_data['publication_time'], 'full_text': full_text, 'is_stocks_to_watch': is_stw, **sentiment_data}
        )
        if is_stw:
            stock_snippets = parse_stocks_to_watch(full_text)
            for snippet in stock_snippets:
                StockInFocus.objects.create(article=db_article, **snippet)
        processed_count += 1
        time.sleep(1)
    return processed_count

def get_and_update_market_news():
    """Primary function for news: updates DB then fetches latest for the API."""
    print("--- Running News Update Service ---")
    try:
        newly_added = scrape_and_store_news()
        print(f"Added {newly_added} new articles to the database.")
    except Exception as e:
        print(f"An error occurred during news scraping: {e}")
    regular_news_qs = NewsArticle.objects.filter(is_stocks_to_watch=False).order_by('-updated_at')[:10]
    watch_list_qs = StockInFocus.objects.select_related('article').order_by('-created_at')[:20]
    regular_news_list = [{"headline": a.headline, "link": a.link, "publication_time": a.publication_time_str, "sentiment": a.sentiment, "confidence": a.confidence, "action": a.action, "full_text": a.full_text, "scraped_at": a.updated_at.isoformat()} for a in regular_news_qs]
    watch_list_list = [{"stock_name": i.stock_name, "text": i.text, "sentiment": i.sentiment, "confidence": i.confidence, "action": i.action} for i in watch_list_qs]
    return {"regular": regular_news_list, "watch_list": watch_list_list}


# --- 3. Corporate Announcements Service (with Prioritization & DB Storage) ---

def fetch_and_parse_nse_announcements():
    """
    Fetches the NSE RSS feed, parses it, saves important ones to the DB,
    and returns all announcements categorized and prioritized.
    """
    rss_url = "https://nsearchives.nseindia.com/content/RSS/Online_announcements.xml"
    print(f"Fetching NSE announcements from: {rss_url}")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.nseindia.com/'
    }
    
    try:
        response = requests.get(rss_url, headers=headers, timeout=20)
        response.raise_for_status()
        feed = feedparser.parse(response.content)
    except requests.exceptions.RequestException as e:
        print(f"❌ ERROR: Could not fetch NSE announcements RSS feed. {e}")
        return {}
    
    if feed.bozo:
        print(f"⚠️ Warning: Malformed RSS feed. Reason: {feed.bozo_exception}")

    PRIORITY_KEYWORDS = {
        'order': 1, 'contract': 1, 'acquisition': 1, 'resignation': 1, 'appointment': 1,
        'buyback': 1, 'delisting': 1, 'fpo': 1, 'ipo': 1, 'bonus': 2, 'allotment': 1,
        'stock split': 2, 'dividend': 2, 'merger': 2, 'demerger': 2,
        'results': 3, 'financial results': 3,
        'investor presentation': 4, 'press release': 4, 'concall': 4,
        'conference call': 4, 'analyst meet': 4, 'credit rating': 4,
        'board meeting': 5, 'agm': 5, 'egm': 5, 'postal ballot': 5,
        'closure of trading window': 6, 'intimation': 6, 'disclosure': 6
    }

    def get_announcement_priority(subject):
        subject_lower = subject.lower()
        for keyword, priority in PRIORITY_KEYWORDS.items():
            if keyword in subject_lower:
                return priority
        return 99

    all_announcements = []
    for entry in feed.entries:
        description = entry.get("description", "")
        subject_text = "Updates"
        if "|SUBJECT:" in description:
            try:
                subject_text = re.sub(r'(-XBRL|XBRL)$', '', description.split("|SUBJECT:")[1].strip(), flags=re.I).strip()
            except IndexError:
                subject_text = "Updates" # Failsafe
        
        priority = get_announcement_priority(subject_text)
        all_announcements.append({
            "company": entry.get("title", "N/A"),
            "category": subject_text,
            "description": description.split("|SUBJECT:")[0].strip(),
            "link": entry.get("link", "#"),
            "pub_date": entry.get("published", "N/A"),
            "priority": priority
        })
    
    for ann in all_announcements:
        if ann['priority'] <= 3 and ann['link'] != '#':
            try:
                ImportantAnnouncement.objects.update_or_create(
                    link=ann['link'],
                    defaults={'company_name': ann['company'], 'category': ann['category'], 'description': ann['description'], 'publication_date_str': ann['pub_date'], 'priority': ann['priority']}
                )
            except Exception as e:
                print(f"Error saving important announcement for {ann['company']}: {e}")

    categorized_announcements = defaultdict(list)
    for ann in all_announcements:
        categorized_announcements[ann['category']].append(ann)
    for category in categorized_announcements:
        categorized_announcements[category].sort(key=lambda x: x['priority'])
    IMPORTANT_CATEGORIES = ['Awarding of Order(s) / Contract(s)', 'Acquisition', 'Financial Results', 'Board Meeting']
    sorted_categories = sorted(categorized_announcements.items(), key=lambda item: (IMPORTANT_CATEGORIES.index(item[0]) if item[0] in IMPORTANT_CATEGORIES else len(IMPORTANT_CATEGORIES), item[0]))
    print(f"✅ Processed {len(feed.entries)} announcements into {len(categorized_announcements)} sorted categories.")
    return dict(sorted_categories)

def get_cached_or_fresh_announcements():
    """Implements a 5-minute caching logic for the prioritized announcements."""
    CACHE_KEY = 'nse_announcements_data_prioritized'
    cached_data = cache.get(CACHE_KEY)
    if cached_data:
        print("Returning cached NSE announcements.")
        return cached_data
    print("Cache for NSE announcements expired. Fetching fresh data...")
    fresh_data = fetch_and_parse_nse_announcements()
    if fresh_data:
        cache.set(CACHE_KEY, fresh_data, 300)
        print("Set new cache for prioritized NSE announcements for 5 minutes.")
    return fresh_data


# --- 4. Annual Financial Reports Service ---
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
        contexts = {}
        for context in root.findall('xbrli:context', self.namespaces):
            period = context.find('xbrli:period', self.namespaces)
            contexts[context.attrib['id']] = {'period': (period.find('xbrli:instant') or period.find('xbrli:endDate')).text}
        facts = []
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
        reports = {'periods': {'current': current_date, 'prior': prior_date}, 'statements': {}}
        facts_by_concept = defaultdict(dict)
        for fact in all_data: facts_by_concept[fact['Concept']][fact['Period']] = fact['Value']
        def build_statement(concepts):
            result = []
            for concept, children in concepts.items():
                if isinstance(children, list): children = {child: None for child in children}
                pretty_concept = ' '.join(re.findall('[A-Z][^A-Z]*', concept.replace('UsedIn', '')))
                fact_data = {'Concept': pretty_concept, 'current': facts_by_concept.get(concept, {}).get(current_date), 'prior': facts_by_concept.get(concept, {}).get(prior_date), 'children': build_statement(children) if children else None}
                if fact_data['current'] is not None or fact_data['prior'] is not None or (fact_data['children'] and len(fact_data['children']) > 0):
                    if fact_data['current'] is None and fact_data['prior'] is None: fact_data.pop('current'); fact_data.pop('prior')
                    result.append(fact_data)
            return result
        for name, concepts in self.statement_concepts.items(): reports['statements'][name] = build_statement(concepts)
        return reports

    def get_structured_data(self):
        flat_facts = self._parse_xbrl()
        return self._group_financial_data(flat_facts) if flat_facts else {}

def process_nse_annual_reports_feed():
    rss_url = "https://nsearchives.nseindia.com/content/RSS/Annual_Reports_XBRL.xml"
    base_xbrl_url = "https://nsearchives.nseindia.com/corporate/xbrl/"
    print(f"Fetching Annual Reports from: {rss_url}")
    feed = feedparser.parse(rss_url)
    if feed.bozo: print(f"Warning: Malformed feed. Reason: {feed.bozo_exception}")
    processed_count = 0
    for entry in feed.entries[:10]:
        company_name, relative_link = entry.get('title', 'Unknown'), entry.get('link')
        if not relative_link: continue
        full_xbrl_url = f"{base_xbrl_url}{relative_link}"
        if FinancialReport.objects.filter(source_url=full_xbrl_url).exists(): continue
        print(f"--- Processing Annual Report: {company_name} ---")
        try:
            response = requests.get(full_xbrl_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=20)
            response.raise_for_status()
            structured_data = AnnualXBRLParser(response.text).get_structured_data()
        except requests.exceptions.RequestException as e: continue
        if structured_data and structured_data.get('periods', {}).get('current'):
            try:
                report_date = datetime.strptime(structured_data['periods']['current'], '%Y-%m-%d').date()
                FinancialReport.objects.create(company_name=company_name, report_date=report_date, structured_data=structured_data, source_url=full_xbrl_url)
                processed_count += 1
            except Exception as e: print(f"   -> ERROR: Could not save report for {company_name} to DB. {e}")
        time.sleep(1)
    return processed_count

def get_cached_or_fresh_financial_reports():
    """Implements 1-hour caching for ANNUAL reports."""
    CACHE_KEY = 'financial_reports_data'
    cached_data = cache.get(CACHE_KEY)
    if cached_data: return cached_data
    try:
        process_nse_annual_reports_feed()
    except Exception as e:
        print(f"An error occurred during annual feed processing: {e}")
    reports = FinancialReport.objects.order_by('-report_date')[:10]
    fresh_data = [report.structured_data for report in reports]
    if fresh_data: cache.set(CACHE_KEY, fresh_data, 3600)
    return fresh_data


# --- 5. Quarterly Financials Service ---
class QuarterlyXBRLParser:
    """A dedicated parser for quarterly Ind-AS XBRL results files."""
    def __init__(self, xml_content):
        self.xml_content = xml_content.encode('utf-8')
        self.contexts = {}
        self.facts = {"general": {}, "statements": {}}

    def parse(self):
        try:
            root = ET.fromstring(self.xml_content)
        except ET.ParseError as e: return None
        self._parse_contexts(root)
        self._extract_facts(root)
        return self.facts

    def _parse_contexts(self, root):
        for context_node in root.findall('.//{http://www.xbrl.org/2003/instance}context'):
            context_id, period_node = context_node.attrib['id'], context_node.find('.//{http://www.xbrl.org/2003/instance}period')
            instant, start_date, end_date = period_node.find('.//{http://www.xbrl.org/2003/instance}instant'), period_node.find('.//{http://www.xbrl.org/2003/instance}startDate'), period_node.find('.//{http://www.xbrl.org/2003/instance}endDate')
            period_label = f"As at {instant.text}" if instant is not None else f"From {start_date.text} to {end_date.text}"
            self.contexts[context_id] = {'period_label': period_label, 'end_date': instant.text if instant is not None else end_date.text, 'explicit_members': {}}
            for member in context_node.findall('.//{http://xbrl.org/2006/xbrldi}explicitMember'):
                self.contexts[context_id]['explicit_members'][member.attrib['dimension'].split(':')[-1]] = member.text.split(':')[-1]

    def _extract_facts(self, root):
        numeric_facts, detail_descriptions = [], {}
        for elem in root:
            if 'contextRef' not in elem.attrib: continue
            concept, context_ref, value = elem.tag.split('}')[-1], elem.attrib['contextRef'], (elem.text or '').strip()
            context = self.contexts.get(context_ref)
            if not context: continue
            if concept.startswith('DescriptionOf'): detail_descriptions[context_ref] = value; continue
            decimals = elem.attrib.get('decimals')
            is_numeric = decimals is not None and value and value.replace('.', '', 1).replace('-', '', 1).isdigit()
            if is_numeric:
                numeric_facts.append({'concept': concept, 'value': float(value), 'decimals': decimals, 'context_ref': context_ref})
            elif not context['explicit_members']:
                self.facts['general'][concept] = value
        self._group_numeric_facts(numeric_facts, detail_descriptions)

    def _group_numeric_facts(self, numeric_facts, detail_descriptions):
        grouped = defaultdict(lambda: {'main': [], 'details': []})
        for fact in numeric_facts:
            context = self.contexts.get(fact['context_ref'])
            fact_data = {**fact, 'context': context}
            if context['explicit_members']:
                fact_data['description'] = detail_descriptions.get(fact['context_ref'], 'Detail')
                grouped[fact['concept']]['details'].append(fact_data)
            else:
                grouped[fact['concept']]['main'].append(fact_data)
        self.facts['statements'] = dict(grouped)

def process_and_store_quarterly_results():
    """Fetches corporate filings, filters for Financial Results, parses, and saves to DB."""
    rss_url = "https://nsearchives.nseindia.com/content/RSS/corporatefilings.xml"
    print(f"Fetching Corporate Filings from: {rss_url}")
    feed = feedparser.parse(rss_url)
    if feed.bozo: print(f"Warning: Malformed feed. Reason: {feed.bozo_exception}")
    results_found = 0
    for entry in feed.entries:
        subject = next((d.get('value', '') for d in entry.get('tags', []) if d.get('term') == 'subject'), '')
        if 'Financial Results' not in subject: continue
        xbrl_link = next((link.get('href', '') for link in entry.get('links', []) if link.get('href', '').lower().endswith('.xml')), None)
        if not xbrl_link: continue
        if QuarterlyFinancials.objects.filter(source_url=xbrl_link).exists(): continue
        print(f"--- Processing Quarterly Result: {entry.title} ---")
        try:
            response = requests.get(xbrl_link, headers={'User-Agent': 'Mozilla/5.0'}, timeout=20)
            response.raise_for_status()
            parser = QuarterlyXBRLParser(response.text)
            parsed_data = parser.parse()
        except requests.exceptions.RequestException as e: print(f"   -> ERROR: Failed to download. {e}"); continue
        except Exception as e: print(f"   -> ERROR: Failed to parse. {e}"); continue
        if parsed_data and parsed_data['general'].get('Symbol'):
            try:
                main_context = next((c for c in parser.contexts.values() if not c['explicit_members'] and c['end_date']), None)
                if not main_context: continue
                QuarterlyFinancials.objects.create(
                    symbol=parsed_data['general']['Symbol'], company_name=parsed_data['general'].get('NameOfTheCompany', entry.title),
                    period_end_date=datetime.strptime(main_context['end_date'], '%Y-%m-%d').date(),
                    structured_data=parsed_data, source_url=xbrl_link
                )
                results_found += 1
            except Exception as e: print(f"   -> ERROR: Could not save to DB. {e}")
        time.sleep(1)
    return results_found

def get_latest_quarterly_reports():
    """Primary function for quarterly reports: updates DB, then fetches the latest for the API."""
    CACHE_KEY = 'quarterly_reports_data'
    cached_data = cache.get(CACHE_KEY)
    if cached_data: return cached_data
    try:
        process_and_store_quarterly_results()
    except Exception as e:
        print(f"An error occurred during quarterly feed processing: {e}")
    latest_reports = QuarterlyFinancials.objects.order_by('company_name', '-period_end_date').distinct('company_name')[:10]
    fresh_data = [report.structured_data for report in latest_reports]
    if fresh_data: cache.set(CACHE_KEY, fresh_data, 3600)
    return fresh_data

def process_financial_corporate_actions():
    """
    NEW: Fetches and processes the dedicated Corporate Actions feed
    for dividends, splits, etc., and saves them to the database.
    """
    rss_url = "https://nsearchives.nseindia.com/content/RSS/Corporate_action.xml"
    print(f"Fetching Financial Corporate Actions from: {rss_url}")
    try:
        feed = feedparser.parse(rss_url)
    except Exception as e:
        print(f"❌ ERROR fetching financial corporate actions: {e}")
        return
        
    for entry in feed.entries:
        try:
            # Parse the description field
            desc = entry.get("description", "")
            details_dict = {item.split(':')[0].strip(): item.split(':')[1].strip() for item in desc.split('|') if ':' in item}
            
            # Clean up company name
            company_name = entry.title.split(' - Ex-Date:')[0].strip()

            # Determine action type from PURPOSE
            purpose = details_dict.get('PURPOSE', '').upper()
            action_type = "Financial" # Default
            if 'DIVIDEND' in purpose: action_type = 'Dividend'
            elif 'DEMERGER' in purpose: action_type = 'Demerger'
            elif 'SPLIT' in purpose: action_type = 'Stock Split'
            elif 'BONUS' in purpose: action_type = 'Bonus'
            
            # Parse dates
            ex_date_str = entry.title.split('Ex-Date: ')[-1].strip()
            ex_date = datetime.strptime(ex_date_str, '%d-%b-%Y').date() if ex_date_str else None
            
            record_date_str = details_dict.get('RECORD DATE')
            record_date = datetime.strptime(record_date_str, '%d-%b-%Y').date() if record_date_str else None

            # Save to the database
            CorporateAction.objects.update_or_create(
                link=entry.link,
                subject=entry.title,
                defaults={
                    'company_name': company_name,
                    'category': 'Financial',
                    'action_type': action_type,
                    'description': desc,
                    'ex_date': ex_date,
                    'record_date': record_date,
                    'details': details_dict,
                    'publication_date_str': entry.published,
                }
            )
            print(f"   -> Saved Financial Event: [{action_type}] for {company_name}")
        except Exception as e:
            print(f"   -> Error processing financial action for '{entry.title}': {e}")

            
def fetch_and_parse_general_announcements():
    """
    Fetches operational announcements (orders, contracts, etc.) and saves them.
    This function is repurposed from the old announcements function.
    """
    rss_url = "https://nsearchives.nseindia.com/content/RSS/Online_announcements.xml"
    print(f"Fetching General Announcements from: {rss_url}")
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        feed = feedparser.parse(requests.get(rss_url, headers=headers, timeout=20).content)
    except Exception as e:
        print(f"❌ ERROR fetching general announcements: {e}")
        return
        
    ACTION_KEYWORDS = {'order': 'Order / Contract', 'contract': 'Order / Contract', 'bagging': 'Order / Contract', 'agreement': 'Agreement / MOU', 'mou': 'Agreement / MOU', 'collaboration': 'Agreement / MOU', 'partnership': 'Agreement / MOU', 'acquisition': 'Acquisition / Stake', 'acquire': 'Acquisition / Stake', 'stake': 'Acquisition / Stake'}

    for entry in feed.entries:
        subject = next((t.get('value') for t in entry.get('tags', []) if t.get('term') == 'subject'), 'Updates')
        action_type = None
        for keyword, type_name in ACTION_KEYWORDS.items():
            if keyword in subject.lower():
                action_type = type_name
                break
        
        if action_type:
            try:
                CorporateAction.objects.update_or_create(
                    link=entry.link,
                    subject=subject,
                    defaults={
                        'company_name': entry.title,
                        'category': 'Operational',
                        'action_type': action_type,
                        'description': entry.summary,
                        'publication_date_str': entry.published,
                    }
                )
                print(f"   -> Saved Operational Event: [{action_type}] for {entry.title}")
            except Exception as e:
                print(f"   -> DB Error saving Operational Action: {e}")
            
def get_latest_corporate_actions():
    """
    Primary function for actions: updates DB from all sources, then fetches 
    the latest for the API, with financial actions prioritized.
    """
    CACHE_KEY = 'corporate_actions_data'
    cached_data = cache.get(CACHE_KEY)
    if cached_data:
        print("Returning cached Corporate Actions.")
        return cached_data

    print("--- Running Corporate Actions Update Service ---")
    try:
        fetch_and_parse_general_announcements()
        process_financial_corporate_actions()
    except Exception as e:
        print(f"An error occurred during corporate action processing: {e}")

    # Fetch latest actions, financial ones first
    actions = CorporateAction.objects.order_by('category', '-scraped_at')[:15]
    
    fresh_data = [{
            "company_name": a.company_name, "action_type": a.action_type, "category": a.category,
            "subject": a.subject, "link": a.link, "details": a.details,
            "publication_date": a.publication_date_str, "ex_date": a.ex_date
        } for a in actions]

    cache.set(CACHE_KEY, fresh_data, 300) # Cache for 5 minutes
    print(f"Set new cache for {len(fresh_data)} corporate actions.")
    return fresh_data