import os
import tweepy
from pathlib import Path

# Read credentials from environment (set in workflow)
API_KEY = os.environ["TWITTER_API_KEY"]
API_SECRET = os.environ["TWITTER_API_SECRET"]
ACCESS_TOKEN = os.environ["TWITTER_ACCESS_TOKEN"]
ACCESS_SECRET = os.environ["TWITTER_ACCESS_SECRET"]

# Authenticate
auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True)

# Settings
USERNAME = "Trevorion"   # Your handle, without '@'
COUNT = 200  # Number of tweets to fetch (max per API call is 200)

gallery_dir = Path("gallery")
gallery_dir.mkdir(exist_ok=True)
output_file = gallery_dir / "tweet_media_urls.txt"

with open(output_file, "w", encoding="utf-8") as f:
    for tweet in tweepy.Cursor(api.user_timeline, screen_name=USERNAME, tweet_mode="extended", count=COUNT, exclude_replies=True, include_rts=False).items(COUNT):
        tweet_url = f"https://x.com/{USERNAME}/status/{tweet.id}"
        # Check for media
        media = tweet.entities.get("media", [])
        if not media and hasattr(tweet, "extended_entities"):
            media = tweet.extended_entities.get("media", [])
        if media:
            for m in media:
                image_url = m.get("media_url_https") or m.get("media_url")
                if image_url:
                    f.write(f"{tweet_url} {image_url}\n")
        else:
            # No image, still write tweet URL for reference
            f.write(f"{tweet_url}\n")

print(f"✅ Wrote tweet media URLs to {output_file}")
