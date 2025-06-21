import os
import tweepy
from pathlib import Path
import re

# Load secrets from environment as before
API_KEY = os.environ["DAU6lMuxLTAAoVkBJqdNY0cch"]
API_SECRET = os.environ["Yt5ZuCmESWTtDioPF084PKtbVAqkt8kJDQut1B8z2ibSfV66he"]
ACCESS_TOKEN = os.environ["1877103205214994432-1uyjznwOLm7wMhRZq4XZgJv9OBVKBd"]
ACCESS_SECRET = os.environ["0EFNf3iVooYHSVC7gO9vN14PQeIjK2s6hq1LrFjIbOFLd"]

auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True)

def extract_tweet_id(tweet_url):
    m = re.search(r'status/(\d+)', tweet_url)
    return m.group(1) if m else None

def process_monthly_file(monthly_file, out_file, username="Trevorion"):
    with open(monthly_file, encoding="utf-8") as fin, open(out_file, "w", encoding="utf-8") as fout:
        for line in fin:
            m = re.search(r'\((https://x\.com/Trevorion/status/\d+)\)', line)
            if m:
                tweet_url = m.group(1)
                tweet_id = extract_tweet_id(tweet_url)
                tweet = api.get_status(tweet_id, tweet_mode="extended")
                media = tweet.entities.get("media", [])
                if not media and hasattr(tweet, "extended_entities"):
                    media = tweet.extended_entities.get("media", [])
                if media:
                    for m in media:
                        image_url = m.get("media_url_https") or m.get("media_url")
                        if image_url:
                            fout.write(f"{tweet_url} {image_url}\n")
                else:
                    fout.write(f"{tweet_url}\n")
    print(f"✅ Wrote images for {monthly_file} to {out_file}")

# Example: process just June 2025
process_monthly_file("monthly/2025-06.md", "gallery/2025-06.txt")
