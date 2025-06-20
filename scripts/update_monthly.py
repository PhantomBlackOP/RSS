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

OUTPUT_DIR = Path("monthly")
OUTPUT_DIR.mkdir(exist_ok=True)

posts_by_month = defaultdict(list)

for day_key, entry in day_map.items():
    day_number = int(day_key.split()[1])
    entry_date = START_DATE + datetime.timedelta(days=day_number - 1)
    month_key = f"{entry_date.year}-{entry_date.month:02d}"
    title = entry["title"].strip("[]")
    url = entry["url"]
    posts_by_month[month_key].append((day_number, title, url))

changed_months = []

for month, entries in sorted(posts_by_month.items()):
    all_lines = []
    tag_counter = Counter()

    for day_number, title, url in sorted(entries):
        all_lines.append(f"- {day_number:03d}: [{title}]({url})")

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

    file_content = (
        header +
        f"Total words: {total_words} Tag count: {len(tag_counter)}\n\n" +
        (f"☁️ Tag Cloud\n{tag_cloud}\n\n" if tag_cloud else "") +
        "\n".join(all_lines)
    )

    # Only overwrite file if contents would change
    if not out_file.exists() or out_file.read_text(encoding="utf-8") != file_content:
        out_file.write_text(file_content, encoding="utf-8")
        changed_months.append(month)

if changed_months:
    print("Updated monthly digests for:", ", ".join(changed_months))
else:
    print("No monthly digests changed.")
