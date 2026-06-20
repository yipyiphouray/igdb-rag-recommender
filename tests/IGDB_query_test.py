import os
import requests
from dotenv import load_dotenv

load_dotenv()

"""Run this script to test querying the 
IGDB API for games with more than 50 ratings, 
sorted by rating count, and print their names."""

client_id = os.getenv("IGDB_CLIENT_ID")
client_secret = os.getenv("IGDB_CLIENT_SECRET") 

# 1. Get access token
token_url = "https://id.twitch.tv/oauth2/token"

params = {
    "client_id": client_id,
    "client_secret": client_secret,
    "grant_type": "client_credentials"
}

token_response = requests.post(token_url, params=params)
token_response.raise_for_status()

access_token = token_response.json()["access_token"]

# 2. Query IGDB
headers = {
    "Client-ID": client_id,
    "Authorization": f"Bearer {access_token}",
    "Accept": "application/json"
}

query = """
fields name, summary, genres.name, platforms.name, first_release_date, rating, total_rating, total_rating_count;
where total_rating_count > 50;
sort total_rating_count desc;
limit 10;
"""

igdb_response = requests.post(
    "https://api.igdb.com/v4/games",
    headers=headers,
    data=query
)

print("IGDB status:", igdb_response.status_code)
print("IGDB response:", igdb_response.text)

igdb_response.raise_for_status()

games = igdb_response.json()

for game in games:
    print(game.get("name"))