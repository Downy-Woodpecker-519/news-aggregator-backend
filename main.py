import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GNews API Key
GNEWS_API_KEY = "b47947106d7c0cb0c816ceea718bcdae"
GNEWS_URL = "https://gnews.io/api/v4/top-headlines"

# Setup logging
logging.basicConfig(level=logging.INFO)

# Fetch news and log the number of articles returned
def fetch_news(topic, countries, max_articles):
    all_articles = []
    articles_per_country = max_articles // len(countries)

    for country in countries:
        params = {
            "token": GNEWS_API_KEY,
            "lang": "en",
            "country": country,
            "max": articles_per_country,
            "topic": topic
        }

        response = requests.get(GNEWS_URL, params=params)
        if response.status_code == 200:
            data = response.json()
            articles = [
                {
                    "title": article["title"],
                    "link": article["url"],
                    "published": article["publishedAt"],
                    "source": article["source"]["name"],
                    "country": country,
                    "topic": topic
                }
                for article in data.get("articles", [])
            ]
            logging.info(f"{topic.upper()} NEWS from {country}: {len(articles)} articles fetched.")
            all_articles.extend(articles)
        else:
            logging.warning(f"Failed to fetch {topic} news from {country}: {response.status_code}")

    logging.info(f"Total {topic.upper()} articles collected: {len(all_articles)}")
    return all_articles

@app.get("/news")
def get_news():
    news_data = {
        "General News (Canada)": fetch_news("general", ["ca"], 20),
        "Business News (Canada & USA)": fetch_news("business", ["ca", "us"], 20),
        "Technology News (Canada, USA & UK)": fetch_news("technology", ["ca", "us", "gb"], 20),
    }
    return news_data

