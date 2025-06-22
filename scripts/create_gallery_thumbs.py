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

print("Loaded from gallery:", list(gallery.items())[:3])

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

print("Loaded from day_map:", list(day_to_tweet.items())[:3])

# 3. Write new file
output = "gallery/2025-gallery-thumbs.md"
with open(output, "w", encoding="utf-8") as f:
    for day in sorted(gallery.keys()):
        title, img_url = gallery[day]

        day_key = f"Day {int(day):03d}"
        print(f"Trying to match day_key: {day_key} for image: {img_url}")
        tweet_url = day_to_tweet.get(day_key)

        if tweet_url:
            print(f"Writing line for {day_key} -> {tweet_url}")
            alt = f'{day}: {title}'
            f.write(f'[<img src="{img_url}" alt="{alt}" style="width: 50px; height: auto;">]({tweet_url})\n')
        else:
            print(f"NO TWEET URL FOR {day_key}")

print(f"✅ Wrote {output}")
