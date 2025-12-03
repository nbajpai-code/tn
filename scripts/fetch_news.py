import feedparser
import json
import datetime
import os
from dateutil import parser
import time

FEEDS_FILE = 'feeds.json'
OUTPUT_FILE = 'README.md'
MAX_ITEMS_PER_FEED = 5

def load_feeds():
    with open(FEEDS_FILE, 'r') as f:
        return json.load(f)

def fetch_feed(url):
    try:
        return feedparser.parse(url)
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def generate_markdown(categories):
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    md = f"# Tech News Aggregator\n\n"
    md += f"Automated tech news updates. Last updated: {now}\n\n"

    for category, urls in categories.items():
        md += f"## {category}\n\n"
        seen_links = set()
        
        # Collect all entries for the category
        all_entries = []
        for url in urls:
            feed = fetch_feed(url)
            if not feed:
                continue
            
            for entry in feed.entries[:MAX_ITEMS_PER_FEED]:
                # Normalize date
                published = None
                if hasattr(entry, 'published'):
                    published = entry.published
                elif hasattr(entry, 'updated'):
                    published = entry.updated
                
                dt = None
                if published:
                    try:
                        dt = parser.parse(published)
                    except:
                        dt = datetime.datetime.now() # Fallback
                else:
                    dt = datetime.datetime.now()

                all_entries.append({
                    'title': entry.title,
                    'link': entry.link,
                    'published': dt,
                    'source': feed.feed.title if hasattr(feed.feed, 'title') else url
                })

        # Sort by date descending
        all_entries.sort(key=lambda x: x['published'], reverse=True)

        # Deduplicate and limit
        count = 0
        for entry in all_entries:
            if entry['link'] in seen_links:
                continue
            seen_links.add(entry['link'])
            
            md += f"- [{entry['title']}]({entry['link']}) - *{entry['source']}* ({entry['published'].strftime('%Y-%m-%d')})\n"
            count += 1
            if count >= 10: # Max 10 items per category
                break
        
        md += "\n"
    
    return md

def main():
    categories = load_feeds()
    markdown_content = generate_markdown(categories)
    
    with open(OUTPUT_FILE, 'w') as f:
        f.write(markdown_content)
    print(f"Successfully generated {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
