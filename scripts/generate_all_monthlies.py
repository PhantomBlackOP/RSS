import os
import re
import datetime
from pathlib import Path
from collections import defaultdict, Counter
import json
import sys

# Load Day-to-Tweet map
sys.path.insert(0, "scripts")
from day_url_map_full_with_titles import day_map

POSTS_DIR = Path("_posts")
OUTPUT_DIR = Path("monthly")
OUTPUT_DIR.mkdir(exist_ok=True)

def extract_month_key(filename):
    match = re.match(r"(\d{4})-(\d{2})-(\d{2})-week-(\d{2})\.md", filename)
    if match:
        year, month = match.group(1), match.group(2)
        return f"{year}-{month}"
    return None

posts_by_month = defaultdict(list)

for file in POSTS_DIR.glob("*.md"):
    key = extract_month_key(file.name)
    if key:
        posts_by_month[key].append(file)

for month, files in sorted(posts_by_month.items()):
    all_lines = []
    tag_counter = Counter()

    for file in sorted(files, key=lambda f: f.name):
        lines = file.read_text(encoding="utf-8").splitlines()
        for line in lines:
            match = re.match(r"- Day\s+(\d{3}):", line)
            if match:
                day_key = f"Day {int(match.group(1)):03d}"
                if day_key in day_map:
                    title = day_map[day_key]["title"].strip("[]")
                    url = day_map[day_key]["url"]
                    all_lines.append(f"- {day_key[4:]}: [{title}]({url})")

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
