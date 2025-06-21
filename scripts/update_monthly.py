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

from datetime import datetime, timedelta, date

def prev_month(month):
    dt = datetime.strptime(month, "%Y-%m")
    prev = dt.replace(day=1) - timedelta(days=1)
    return prev.strftime("%Y-%m")

def next_month(month):
    dt = datetime.strptime(month, "%Y-%m")
    next_ = (dt.replace(day=28) + timedelta(days=4)).replace(day=1)
    return next_.strftime("%Y-%m")

months_sorted = sorted(posts_by_month.keys())
first_month = months_sorted[0]
last_month = months_sorted[-1]

for month, entries in sorted(posts_by_month.items()):
    all_lines = []
    tag_counter = Counter()

    from collections import Counter
    
    # For Top Words (excluding stopwords)
    stopwords = {"the", "of", "and", "a", "in", "to", "for", "on", "with", "at", "by", "an"}
    words = []
    for _, title, _ in entries:
        words += [w.lower() for w in re.findall(r'\w+', title) if w.lower() not in stopwords]
    word_freq = Counter(words)
    top_words = ", ".join(f"{w} ({c})" for w, c in word_freq.most_common(3))
    
    # For Top Tags
    top_tags = ", ".join(f"{tag} ({count})" for tag, count in tag_counter.most_common(3))
            
    for day_number, title, url in sorted(entries):
        all_lines.append(f"- {day_number:03d}: [{title}]({url})")

        tags = re.findall(r"#\w+", title)
        if tags:
            tag_counter.update(tags)
        else:
            fallback = re.findall(r"[A-Za-z]+", title)
            tag_counter.update([f"#{word.lower()}" for word in fallback if len(word) > 3])

    out_file = OUTPUT_DIR / f"{month}.md"
    
    header = (
        f"---\n"
        f"layout: page\n"
        f"title: Monthly\n"
        f"permalink: /monthly/{month}.html\n"
        f"show_title: false\n"
        f"page_type: monthly\n"
    )
    if month != first_month:
        header += f"prev_url: /monthly/{prev_month(month)}.html\n"
    if month != last_month:
        header += f"next_url: /monthly/{next_month(month)}.html\n"
    header += "---\n\n"

    header += f"# 📅 Monthly Digest – {date(int(month[:4]), int(month[5:]), 1):%B %Y}\n\n"

    tag_cloud = " ".join(sorted(tag_counter.keys()))
    total_words = sum(len(re.findall(r'\w+', title)) for _, title, _ in entries)
    
    file_content = (
        header +
        "\n".join(all_lines) + "\n\n" +
        f"🖼️ Total days: {len(all_lines)} 📜 Total words: {total_words} 🏷️ Tag count: {len(tag_counter)}\n\n" +
        (f"🏆 Top words: {top_words}\n" if top_words else "") +
        (f"🔥 Top tags: {top_tags}\n\n" if top_tags else "") +
        (f"☁️ Tag Cloud\n{tag_cloud}\n\n" if tag_cloud else "")
    )

    # Only overwrite file if contents would change
    if not out_file.exists() or out_file.read_text(encoding="utf-8") != file_content:
        out_file.write_text(file_content, encoding="utf-8")
        changed_months.append(month)

if changed_months:
    print("Updated monthly digests for:", ", ".join(changed_months))
else:
    print("No monthly digests changed.")
