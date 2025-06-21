import re
import datetime
from pathlib import Path
from collections import defaultdict

MONTHLY_DIR = Path("monthly")
INDEX_FILE = Path("monthly_index.md")

months = []
month_re = re.compile(r"(\d{4})-(\d{2})\.md$")

for f in MONTHLY_DIR.glob("*.md"):
    m = month_re.match(f.name)
    if m:
        year, month = m.group(1), m.group(2)
        months.append((int(year), int(month)))

if not months:
    raise SystemExit("No monthly digest files found.")

months.sort(reverse=True)  # Latest year/month first

# Group by year
months_by_year = defaultdict(list)
for year, month in months:
    months_by_year[year].append(month)

with INDEX_FILE.open("w", encoding="utf-8") as f:
    f.write("""---
layout: page
title: Monthly AI Anime Digests
permalink: /monthly/
show_title: true
page_type: archive
---

🗓️ Welcome to the Monthly Digest Hub  
Each month distills daily AI anime images into a summary of:
- Weekly post links
- Word usage statistics
- A tag cloud snapshot

---
""")
    for year in sorted(months_by_year, reverse=True):
        f.write(f"\n## 📆 {year}\n")
        for month in sorted(months_by_year[year], reverse=True):
            f.write(f"- [{datetime.date(year, month, 1):%B %Y}](/monthly/{year}-{month:02d}.md)\n")
    f.write("""
---""")
print("✅ monthly_index.md updated.")
