import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

app = FastAPI()

# Enable CORS to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GNews API Key (Replace with your actual key)
GNEWS_API_KEY = b47947106d7c0cb0c816ceea718bcdae
GNEWS_URL = "https://gnews.io/api/v4/top-headlines"

# Fetch news from GNews API
def fetch_news():
    params = {
        "token": GNEWS_API_KEY,
        "lang": "en",  # English news only
        "country": "ca",  # Canada (Change or remove for global news)
        "max": 20  # Max articles per request
    }
    
    response = requests.get(GNEWS_URL, params=params)
    
    if response.status_code == 200:
        data = response.json()
        articles = [
            {
                "title": article["title"],
                "link": article["url"],
                "published": article["publishedAt"],
                "source": article["source"]["name"]
            }
            for article in data.get("articles", [])
        ]
        return articles
    else:
        return []

@app.get("/news")
def get_news():
    return {"articles": fetch_news()}
