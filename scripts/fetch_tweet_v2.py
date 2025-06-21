import os
import requests
import json

# Set your Bearer Token as an environment variable named 'TWITTER_BEARER_TOKEN'
BEARER_TOKEN = os.environ["TWITTER_BEARER_TOKEN"]

TWEET_ID = "1921296026188611814"

url = (
    "https://api.twitter.com/2/tweets"
    f"?ids={TWEET_ID}"
    "&tweet.fields=article,attachments,author_id,card_uri,community_id,"
    "context_annotations,conversation_id,created_at,display_text_range,edit_controls,"
    "edit_history_tweet_ids,entities,geo,id,in_reply_to_user_id,lang,media_metadata,"
    "non_public_metrics,note_tweet,organic_metrics,possibly_sensitive,promoted_metrics,"
    "public_metrics,referenced_tweets,reply_settings,scopes,source,text,withheld"
)

headers = {
    "Authorization": f"Bearer {BEARER_TOKEN}"
}

response = requests.get(url, headers=headers)
print("Status code:", response.status_code)

# Save the JSON to file
with open("testfile.txt", "w", encoding="utf-8") as f:
    json.dump(response.json(), f, indent=2, ensure_ascii=False)

print("Response saved to testfile.txt")
