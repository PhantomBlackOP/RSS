import os
import re
import datetime
from pathlib import Path
from collections import defaultdict, Counter
import sys

START_DATE = datetime.date(2025, 1, 1)  # Day 001 = Jan 1, 2025

# Load Day-to-Tweet map
sys.path.insert(0, "scripts")
from day_url_map_full_with_titles import day_map

POSTS_DIR = Path("_posts")
OUTPUT_DIR = Path("monthly")
OUTPUT_DIR.mkdir(exist_ok=True)

# Clear out old monthly digests to force a full rebuild
for f in OUTPUT_DIR.glob("*.md"):
    f.unlink()

posts_by_month = defaultdict(list)

for day_key, entry in day_map.items():
    day_number = int(day_key.split()[1])  # Extracts N from "Day NNN"
    entry_date = START_DATE + datetime.timedelta(days=day_number - 1)
    month_key = f"{entry_date.year}-{entry_date.month:02d}"
    title = entry["title"].strip("[]")
    url = entry["url"]
    posts_by_month[month_key].append((day_number, title, url))

print("All months found:", sorted(posts_by_month.keys()))
for month, entries in sorted(posts_by_month.items()):
    all_lines = []
    tag_counter = Counter()

    for day_number, title, url in sorted(entries):
        all_lines.append(f"- {day_number:03d}: [{title}]({url})")

        # Extract hashtags or fallback words
        tags = re.findall(r"#\w+", title)
        if tags:
            tag_counter.update(tags)
        else:
            fallback = re.findall(r"[A-Za-z]+", title)
            tag_counter.update([f"#{word.lower()}" for word in fallback if len(word) > 3])

    out_file = OUTPUT_DIR / f"{month}.md"
    header = f"# 📅 Monthly Digest – {datetime.date(int(month[:4]), int(month[5:]), 1):%B %Y}\n\n"

    tag_cloud = " ".join(sorted(tag_counter.keys()))
    total_words = sum(len(re.findall(r'\w+', entry['title'])) for entry in day_map.values() if entry["title"])

    with out_file.open("w", encoding="utf-8") as f:
        f.write(header)
        f.write(f"Total words: {total_words} Tag count: {len(tag_counter)}\n\n")
        if tag_cloud:
            f.write("☁️ Tag Cloud\n" + tag_cloud + "\n\n")
        f.write("\n".join(all_lines))

print("✅ Monthly digests updated with real tweet URLs.")
