import os
import re
import datetime
from pathlib import Path

POSTS_DIR = Path("_posts")
ARCHIVE_FILE = Path("archive.md")

# Front matter
header = """---
layout: page
title: Archive
permalink: /archive/
---

# 📚 Archive

Explore all past weekly digests (newest first):

"""

def extract_post_info(filename):
    match = re.match(r"(\d{4})-(\d{2})-(\d{2})-week-(\d{2})\.md", filename)
    if not match:
        return None
    year, month, day, week = match.groups()
    date = datetime.date(int(year), int(month), int(day))
    url = f"/{year}/{month}/{day}/week-{week}.html"
    return int(week), url, date

# Collect all posts
posts = []
for file in POSTS_DIR.glob("*.md"):
    info = extract_post_info(file.name)
    if info:
        posts.append(info)

# Sort by week descending
posts.sort(key=lambda x: x[2], reverse=True)

# Build archive content
lines = [header]
for week, url, date in posts:
    lines.append(f"- 📅 [Week {week:02d} – Dailies & Highlights]({url}) ({date.strftime('%b %d, %Y')})")

from datetime import datetime
lines.append(f"\n_Last updated: {datetime.utcnow().strftime('%b %d, %Y %H:%M UTC')}_")

footer = """---
Follow [@Trevorion](https://x.com/Trevorion)

Stay lit. 🔥

"""
lines.append([footer])

# Write archive.md
ARCHIVE_FILE.write_text("\n".join(lines), encoding="utf-8")
print("✅ archive.md updated successfully.")
