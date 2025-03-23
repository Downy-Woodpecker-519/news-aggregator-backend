from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

app = FastAPI()  # ✅ Define app first

# ✅ Add CORS middleware after app definition
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

from datetime import datetime, timedelta, timezone

from urllib.parse import urlparse

def fetch_news():
    articles = []
    cutoff_date = (datetime.utcnow() - timedelta(days=1)).replace(tzinfo=timezone.utc)

    for url in NEWS_SOURCES:
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "xml")

            for item in soup.find_all("item"):
                title = item.title.text.strip() if item.title else "No title available"
                link = item.find("link")
                link = link.text.strip() if link else "No link available"
                pub_date = item.find("pubDate")
                pub_date = pub_date.text.strip() if pub_date else "Unknown"

                # Extract the news source from the link
                source = "Unknown Source"
                if link != "No link available":
                    parsed_url = urlparse(link)
                    source = parsed_url.netloc.replace("www.", "")

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
                    "published": pub_date,
                    "source": source  # ✅ Added source field
                })

        except requests.exceptions.Timeout:
            print(f"⏳ Timeout: {url} - Skipping slow source")
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching {url}: {e}")
        except Exception as e:
            print(f"🚨 Unexpected error: {e}")

    return articles

@app.get("/news")
def get_news():
    return {"articles": fetch_news()}
