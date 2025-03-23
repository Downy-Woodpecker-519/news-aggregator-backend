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

import warnings
from bs4 import XMLParsedAsHTMLWarning

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)  # Suppress warning

def fetch_news():
    articles = []
    cutoff_date = datetime.utcnow() - timedelta(days=1)

    for url in NEWS_SOURCES:
        try:
            response = requests.get(url, timeout=30)  # Increased timeout to 30 seconds
            response.raise_for_status()  # Raise error for bad responses

            soup = BeautifulSoup(response.content, "xml")  # Corrected parser usage

            for item in soup.find_all("item"):
                title = item.title.text.strip() if item.title else "No title available"
                link = item.link.text.strip() if item.link else item.guid.text.strip() if item.guid else "No link available"
                pub_date = item.pubDate.text.strip() if item.pubDate else "Unknown"

                if pub_date != "Unknown":
                    try:
                        article_date = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %z")
                        if article_date < cutoff_date:
                            continue
                    except ValueError:
                        pass  # Ignore errors and keep the article

                articles.append({
                    "title": title,
                    "link": link,
                    "published": pub_date
                })

        except requests.exceptions.Timeout:
            print(f"⏳ Timeout: {url} - Skipping slow source")
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching {url}: {e}")

    return articles



@app.get("/news")
def get_news():
    return {"articles": fetch_news()}
