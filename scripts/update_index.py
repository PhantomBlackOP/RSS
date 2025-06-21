import os
import re
import datetime
from pathlib import Path

POSTS_DIR = Path("_posts")
INDEX_FILE = Path("index.md")

# Front matter
header = """---
layout: page
title: Trevorion Weekly RSS Feed
permalink: /
show_title: true
page_type: index"
---
<img src="/assets/Banner.png" alt="Trevorion Weekly Digest Banner" style="width: 365px; height: auto; float: left; margin-bottom: 50px; margin-right: 24px;" />

Welcome to the official archive of [@Trevorion](https://x.com/Trevorion)'s AI Anime Daily Images.

Each week captures 7 unique daily posts — a blend of tech, fantasy, sci-fi, nostalgia, and slice-of-life.  
Built for long-term readers, indie web fans, and curious minds.

---
"""
def extract_post_info(filename):
    match = re.match(r"(\d{4})-(\d{2})-(\d{2})-week-(\d{2})\.md", filename)
    if not match:
        return None
    year, month, day, week = match.groups()
    date = datetime.date(int(year), int(month), int(day))
    url = f"/{year}/{month}/{day}/week-{week}.html"
    return int(week), url, date

# Collect the last post
posts = []
for file in POSTS_DIR.glob("*.md"):
    info = extract_post_info(file.name)
    if info:
        posts.append(info)

# Sort by week, descending
posts.sort(key=lambda x: x[2], reverse=True)

# Build archive content
lines = [header]

if posts:
    week, url, date = posts[0]
    lines.append(f"📅 **Latest Week**: [Week {week:02d} – Dailies & Highlights]({url})<br />")

bodypart = """📚 **Full Archive**: [View All Weeks](/archive/)<br/>
🗓️ **Monthly Recap**: [All Months](/monthly/)<br/>
📰 **RSS Feed**: [RSS is active](/feed.xml)<br/>
---"""

lines.append(bodypart)

from datetime import datetime
lines.append(f"\n_Last updated: {datetime.utcnow().strftime('%b %d, %Y %H:%M UTC')}_")

footer = """

Follow [@Trevorion](https://x.com/Trevorion)  

Stay lit. 🔥

"""
lines.append(footer)

# Write index.md
INDEX_FILE.write_text("\n".join(lines), encoding="utf-8")
print("✅ index.md updated successfully.")
