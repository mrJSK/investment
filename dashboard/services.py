# import time
# import requests
# import json
# import re
# from bs4 import BeautifulSoup
# from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
# from django.core.cache import cache
# from datetime import datetime

# # --- Sentiment Analysis Model (Unchanged) ---
# try:
#     print("Loading FinBERT sentiment analysis model...")
#     model_name = "ProsusAI/finbert"
#     tokenizer = AutoTokenizer.from_pretrained(model_name)
#     model = AutoModelForSequenceClassification.from_pretrained(model_name)
#     classifier = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)
#     print("FinBERT model loaded successfully.")
# except Exception as e:
#     print(f"CRITICAL ERROR: Could not load FinBERT model. {e}")
#     classifier = None

# def analyze_sentiment(text):
#     """
#     Analyzes the sentiment of a given text using the loaded FinBERT model.
#     (This function is unchanged)
#     """
#     if not classifier or not text:
#         return {"sentiment": "Neutral", "confidence": 0.0, "action": "Hold"}
#     try:
#         inputs = tokenizer(text, truncation=True, max_length=512, return_tensors="pt")
#         outputs = model(**inputs)
#         scores = outputs.logits.softmax(dim=1)[0]
#         labels = model.config.id2label
#         top_idx = scores.argmax().item()
#         sentiment_label = labels[top_idx].lower()
#         confidence = round(scores[top_idx].item() * 100, 2)
#         action = {"positive": "Buy", "neutral": "Hold", "negative": "Sell"}.get(sentiment_label, "Hold")
#         return {"sentiment": sentiment_label.capitalize(), "confidence": confidence, "action": action}
#     except Exception as e:
#         print(f"Error during sentiment analysis: {e}")
#         return {"sentiment": "Neutral", "confidence": 0.0, "action": "Hold"}

# # --- UPDATED Scraping Functions ---

# def scrape_headlines_from_main_page():
#     """
#     Downloads and parses the main market page HTML to get a list of article links,
#     headlines, and their original publication timestamps.
#     """
#     market_url = "https://www.cnbctv18.com/market/"
#     print(f"Fetching headlines from main page: {market_url}")
#     headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
#     try:
#         response = requests.get(market_url, headers=headers, timeout=15)
#         response.raise_for_status()
#         soup = BeautifulSoup(response.text, "html.parser")
#     except requests.exceptions.RequestException as e:
#         print(f"ERROR: Could not download the main market page. {e}")
#         return []

#     all_news = []
#     scraped_links = set()

#     # Helper to clean up timestamp text
#     def clean_timestamp(ts_text):
#         if not ts_text:
#             return "Timestamp not found"
#         # Removes the "Min Read" part
#         return re.sub(r'\s*\d+\s+Min Read.*$', '', ts_text).strip()

#     # Scraper for "Top Market News" section
#     top_news_section = soup.select_one("section.mrkt-top-widget.common-mkt-css")
#     if top_news_section:
#         articles = top_news_section.select("a")
#         for a in articles:
#             link = a.get("href", "")
#             if link and link not in scraped_links:
#                 full_url = "https://www.cnbctv18.com" + link if link.startswith("/") else link
#                 title_tag = a.find(['h3', 'h4'])
#                 title = title_tag.get_text(strip=True) if title_tag else a.get_text(strip=True)
                
#                 # NEW: Find the timestamp element relative to the link
#                 timestamp_tag = a.find("div", class_="mkt-ts")
#                 timestamp_str = clean_timestamp(timestamp_tag.get_text(strip=True)) if timestamp_tag else "N/A"

#                 if title:
#                     all_news.append({"title": title, "link": full_url, "publication_time": timestamp_str})
#                     scraped_links.add(link)

#     # Scraper for "MARKET NEWS" live timeline
#     timeline_items = soup.select("ul.live-mrkt-timeline li.live-mrkt-item")
#     for item in timeline_items:
#         link_tag = item.select_one("a.live-mrkt-exp")
#         if link_tag:
#             link = link_tag.get("href", "")
#             # Ensure the link is a full article URL
#             if link and link not in scraped_links and 'cnbctv18.com' in link:
#                 title = link_tag.get_text(strip=True)
                
#                 # NEW: Find the timestamp element
#                 timestamp_tag = item.find("div", class_="live-mrkt-time")
#                 timestamp_str = clean_timestamp(timestamp_tag.get_text(strip=True)) if timestamp_tag else "N/A"
                
#                 if title:
#                     all_news.append({"title": title, "link": link, "publication_time": timestamp_str})
#                     scraped_links.add(link)

#     print(f"Found {len(all_news)} unique article links to process.")
#     return all_news

# def extract_full_text_from_article(article_url):
#     """
#     Downloads an individual article page and extracts the full text.
#     (This function is unchanged but its output is now essential for the dropdown)
#     """
#     print(f"  -> Fetching full text from: {article_url}")
#     headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
#     try:
#         response = requests.get(article_url, headers=headers, timeout=15)
#         response.raise_for_status()
#         soup = BeautifulSoup(response.text, 'html.parser')
#     except requests.exceptions.RequestException as e:
#         return f"Could not download article: {e}"

#     # Method A: Prioritize JSON-LD structured data
#     try:
#         script_tags = soup.find_all('script', {'type': 'application/ld+json'})
#         for script in script_tags:
#             if script.string:
#                 json_data = json.loads(script.string)
#                 data_to_check = json_data if isinstance(json_data, list) else [json_data]
#                 for item in data_to_check:
#                     if isinstance(item, dict) and item.get('@type') == 'NewsArticle' and 'articleBody' in item:
#                         body_soup = BeautifulSoup(item['articleBody'], 'html.parser')
#                         return body_soup.get_text(separator=' ', strip=True)
#     except Exception:
#         pass

#     # Method B: Fallback to manual scraping
#     article_body = soup.select_one('div.articleWrap') or soup.select_one('div.narticle-data')
#     if article_body:
#         return article_body.get_text(separator=' ', strip=True)

#     return "Article content could not be extracted."

# # --- UPDATED: Main Service Function to include full text and pub date ---
# def fetch_and_analyze_news():
#     """
#     Orchestrates the entire static process:
#     1. Scrapes headlines, links, and publication times.
#     2. For each headline, fetches the full article text.
#     3. Performs sentiment analysis on the full text.
#     4. Returns a comprehensive dictionary for each article.
#     """
#     articles = scrape_headlines_from_main_page()
#     analyzed_news = []

#     # Process the first 10 articles found
#     for article in articles[:10]:
#         full_text = extract_full_text_from_article(article['link'])
#         sentiment_data = analyze_sentiment(full_text)
        
#         analyzed_news.append({
#             "headline": article['title'],
#             "link": article['link'],
#             "publication_time": article['publication_time'], # NEW: Pass the original timestamp
#             "sentiment": sentiment_data['sentiment'],
#             "confidence": sentiment_data['confidence'],
#             "action": sentiment_data['action'],
#             "full_text": full_text, # NEW: Include the full text for the dropdown
#             "scraped_at": datetime.now().isoformat()
#         })
#     return analyzed_news

# # --- Caching logic remains unchanged ---
# def get_cached_or_fresh_news():
#     """Implements a 1-minute caching logic."""
#     CACHE_KEY = 'market_news_data'
#     cached_news = cache.get(CACHE_KEY)
#     if cached_news:
#         print("Returning cached news (valid for 60s).")
#         return cached_news
#     print("Cache expired or empty. Fetching fresh news...")
#     fresh_news = fetch_and_analyze_news()
#     if fresh_news:
#         print("Setting new cache for 60 seconds.")
#         cache.set(CACHE_KEY, fresh_news, 60)
#     return fresh_news

import time
import feedparser
import requests
import json
import re
from bs4 import BeautifulSoup
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from django.core.cache import cache
from datetime import datetime

# --- Sentiment Analysis Model (No Changes) ---
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
    if not classifier or not text:
        return {"sentiment": "Neutral", "confidence": 0.0, "action": "Hold"}
    try:
        # Truncate text to avoid model errors with very long snippets
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

# --- Scraping Functions (No Changes to these two) ---
def scrape_headlines_from_main_page():
    market_url = "https://www.cnbctv18.com/market/"
    print(f"Fetching headlines from main page: {market_url}")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
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
    print(f"  -> Fetching full text from: {article_url}")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
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
        if article_body_tag:
            print(f"    -> Found article body using selector: '{selector}'")
            break
    if article_body_tag:
        elements_to_remove = ['.advertisement', '.related-articles', 'aside', '.social-share', '.tags', 'figure']
        for s in elements_to_remove:
            for tag in article_body_tag.select(s):
                tag.decompose()
        meaningful_paragraphs = [p.get_text(strip=True) for p in article_body_tag.find_all('p') if len(p.get_text(strip=True).split()) > 5]
        full_text = '\n\n'.join(meaningful_paragraphs) if meaningful_paragraphs else article_body_tag.get_text(separator='\n\n', strip=True)

        # Remove content after "Also Read"
        if "Also Read:" in full_text:
            full_text = full_text.split("Also Read:")[0].strip()
        elif "Also, Watch" in full_text:
            full_text = full_text.split("Also, Watch")[0].strip()

        return full_text
    return "Article content could not be extracted. The page layout may have changed."

# --- NEW: Function to parse the special "Stocks to Watch" article ---
def parse_stocks_to_watch(full_text):
    """
    Parses the text of a "Stocks to Watch" article, splitting it by stock,
    and running sentiment analysis on each part.
    """
    print("  -> Parsing 'Stocks to Watch' article...")
    # Split the article by the "|" delimiter, which separates each stock.
    # We clean up whitespace and filter out any empty strings that might result.
    stock_snippets = [snippet.strip() for snippet in full_text.split('|') if snippet.strip()]
    
    parsed_stocks = []
    for snippet in stock_snippets:
        # The first part before a newline is likely the stock name
        parts = snippet.split('\n', 1)
        stock_name = parts[0].strip()
        news_text = parts[1].strip() if len(parts) > 1 else ""

        if not stock_name or not news_text:
            continue

        # Run sentiment analysis on the specific text for this stock
        sentiment_data = analyze_sentiment(news_text)
        parsed_stocks.append({
            "stock_name": stock_name,
            "text": news_text,
            "sentiment": sentiment_data['sentiment'],
            "confidence": sentiment_data['confidence'],
            "action": sentiment_data['action']
        })
    print(f"  -> Parsed into {len(parsed_stocks)} individual stock snippets.")
    return parsed_stocks

# --- UPDATED: Main Service Function to handle the two types of news ---
def fetch_and_analyze_news():
    """
    Orchestrates the scraping and analysis process, now separating
    regular news from the special "Stocks to Watch" list.
    """
    articles = scrape_headlines_from_main_page()
    
    regular_news = []
    watch_list = []
    
    # Process only the first 10 articles to keep it fast
    for article in articles[:10]:
        full_text = extract_full_text_from_article(article['link'])
        
        # Check if this is the special article
        if "stocks to watch" in article['title'].lower():
            watch_list.extend(parse_stocks_to_watch(full_text))
        else:
            # Otherwise, process as a regular news item
            sentiment_data = analyze_sentiment(full_text)
            regular_news.append({
                "headline": article['title'],
                "link": article['link'],
                "publication_time": article['publication_time'],
                "sentiment": sentiment_data['sentiment'],
                "confidence": sentiment_data['confidence'],
                "action": sentiment_data['action'],
                "full_text": full_text,
                "scraped_at": datetime.now().isoformat()
            })
            
    # Return a dictionary containing both lists
    return {"regular": regular_news, "watch_list": watch_list}

# --- Caching logic remains unchanged ---
def get_cached_or_fresh_news():
    CACHE_KEY = 'market_news_data'
    cached_news = cache.get(CACHE_KEY)
    if cached_news:
        print("Returning cached news (valid for 60s).")
        return cached_news
    print("Cache expired or empty. Fetching fresh news...")
    fresh_news = fetch_and_analyze_news()
    if fresh_news:
        print("Setting new cache for 60 seconds.")
        cache.set(CACHE_KEY, fresh_news, 60)
    return fresh_news

# --- CORRECTED: NSE Announcements Service ---
def fetch_and_parse_nse_announcements():
    """
    Fetches the NSE RSS feed, parses it, and categorizes announcements exhaustively.
    """
    # CORRECTED URL to prevent 404 errors
    rss_url = "https://nsearchives.nseindia.com/content/RSS/Online_announcements.xml"
    print(f"Fetching NSE announcements from: {rss_url}")
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(rss_url, headers=headers, timeout=20)
        response.raise_for_status()
        # Using feedparser which is robust for RSS feeds
        feed = feedparser.parse(response.content)
    except requests.exceptions.RequestException as e:
        print(f"❌ ERROR: Could not fetch NSE announcements RSS feed. {e}")
        return {}

    categorized_announcements = {}
    processed_links = set()

    for entry in feed.entries:
        if entry.link in processed_links:
            continue
        
        description = entry.description if hasattr(entry, 'description') else ""
        
        # Extract subject/category exhaustively from the description
        subject = "Updates" # Default category
        if "|SUBJECT:" in description:
            subject_text = description.split("|SUBJECT:")[1].strip()
            # Clean up common variations like '-XBRL'
            subject = re.sub(r'(-XBRL|XBRL)$', '', subject_text, flags=re.I).strip()

        if subject not in categorized_announcements:
            categorized_announcements[subject] = []
        
        categorized_announcements[subject].append({
            "company": entry.title,
            "description": description.split("|SUBJECT:")[0].strip(),
            "link": entry.link,
            "pub_date": entry.get("published", "N/A")
        })
        processed_links.add(entry.link)

    print(f"✅ Processed {len(feed.entries)} announcements into {len(categorized_announcements)} categories.")
    return categorized_announcements

def get_cached_or_fresh_announcements():
    """Implements a 5-minute caching logic for NSE announcements."""
    CACHE_KEY = 'nse_announcements_data'
    cached_data = cache.get(CACHE_KEY)
    if cached_data:
        print("Returning cached NSE announcements.")
        return cached_data
    
    print("Cache for NSE announcements expired. Fetching fresh data...")
    fresh_data = fetch_and_parse_nse_announcements()
    if fresh_data:
        # Cache duration is 300 seconds (5 minutes)
        cache.set(CACHE_KEY, fresh_data, 300) 
        print("Set new cache for NSE announcements for 5 minutes.")
    return fresh_data