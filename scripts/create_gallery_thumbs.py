import re

# 1. Parse gallery file
gallery_md = "gallery/2025-gallery.md"
gallery = {}  # day_num: (title, img_url)
with open(gallery_md, encoding="utf-8") as f:
    for line in f:
        m = re.match(r"- (\d{3}): \[(.+?)\]\((https://pbs\.twimg\.com/media/[^)]+)\)", line)
        if m:
            day, title, img_url = m.groups()
            gallery[day] = (title, img_url)

# 2. Parse day_url_map_full_with_titles.py
map_py = "scripts/day_url_map_full_with_titles.py"
day_to_tweet = {}  # day_num: tweet_url

# The file is a Python dict, so eval is risky, let's just use regex
with open(map_py, encoding="utf-8") as f:
    for line in f:
        m = re.match(r"\s*'Day (\d{3})': \{\s*'title': .+,\s*'url': '([^']+)'", line)
        if m:
            day, tweet_url = m.groups()
            day_to_tweet[day] = tweet_url

# 3. Write new file
output = "gallery/2025-gallery-thumbs.md"
with open(output, "w", encoding="utf-8") as f:
    for day in sorted(gallery.keys()):
        title, img_url = gallery[day]
        tweet_url = day_to_tweet.get(day)
        if tweet_url:
            alt = f'{day}: {title}'
            f.write(f'[<img src="{img_url}" alt="{alt}" style="width: 50px; height: auto;">]({tweet_url})\n')

print(f"✅ Wrote {output}")
