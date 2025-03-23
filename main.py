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

# Fetch news with a single request per topic
def fetch_news(topic, max_articles):
    params = {
        "token": GNEWS_API_KEY,
        "lang": "en",
        "max": max_articles,
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
                "topic": topic
            }
            for article in data.get("articles", [])
        ]
        logging.info(f"{topic.upper()} NEWS: {len(articles)} articles fetched.")
        return articles
    else:
        logging.warning(f"Failed to fetch {topic} news: {response.status_code}")
        return []

@app.get("/news")
def get_news():
    news_data = {
        "General News": fetch_news("general", 20),
        "Business News": fetch_news("business", 20),
        "Technology News": fetch_news("technology", 20),
    }
    return news_data


