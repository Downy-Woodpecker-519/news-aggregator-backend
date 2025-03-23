from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

app = FastAPI()

NEWS_SOURCES = [
    "https://www.cbc.ca/cmlink/rss-world",
    "https://www.ctvnews.ca/rss/ctvnews-ca-top-stories-public-rss-1.822009",
    "https://globalnews.ca/world/feed/",
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://www.npr.org/rss/rss.php?id=1004",
    "https://www.reuters.com/rssFeed/worldNews",
]

def fetch_news():
    articles = []
    cutoff_date = datetime.utcnow() - timedelta(days=1)
    
    for url in NEWS_SOURCES:
        try:
            response = requests.get(url, timeout=20)  # Increased timeout
            soup = BeautifulSoup(response.content, "lxml")  # Use lxml parser

            for item in soup.find_all("item"):
                title = item.title.text
                link = item.link.text
                pub_date = item.pubDate.text if item.pubDate else "Unknown"

                articles.append({
                    "title": title,
                    "link": link,
                    "published": pub_date
                })

        except Exception as e:
            print(f"❌ Error fetching {url}: {e}")  # Debugging log
    
    return articles

@app.get("/news")
def get_news():
    return {"articles": fetch_news()}
