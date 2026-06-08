import os
import requests
from dotenv import load_dotenv
from pathlib import Path

"""Run this script to test the connection to 
the IGDB API and retrieve an access token."""


load_dotenv()

client_id = os.getenv("IGDB_CLIENT_ID")
client_secret = os.getenv("IGDB_CLIENT_SECRET")

if not client_id or not client_secret:
    raise ValueError("Missing IGDB credentials.")

token_url = "https://id.twitch.tv/oauth2/token"

params = {
    "client_id": client_id,
    "client_secret": client_secret,
    "grant_type": "client_credentials"
}

response = requests.post(token_url, params=params)

print("Token status:", response.status_code)
print("Token response:", response.text)

response.raise_for_status()

access_token = response.json()["access_token"]

print("Access token received.")