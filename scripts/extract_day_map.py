import re
from pathlib import Path

POSTS_DIR = Path("_posts")
OUTPUT_FILE = Path("scripts/day_url_map_full_with_titles.py")

day_map = {}

for md_file in POSTS_DIR.glob("*.md"):
    lines = md_file.read_text(encoding="utf-8").splitlines()
    for line in lines:
        match = re.match(r"- Day (\d{3}): \[(.+?)\]\((https://x.com/Trevorion/status/\d+)\)", line)
        if match:
            day_number = int(match.group(1))
            title = match.group(2).strip()
            url = match.group(3).strip()
            day_key = f"Day {day_number:03d}"
            day_map[day_key] = {"title": title, "url": url}

# Write the Python file
with OUTPUT_FILE.open("w", encoding="utf-8") as f:
    f.write("day_map = " + repr(day_map) + "\n")

print(f"✅ Extracted {len(day_map)} entries to {OUTPUT_FILE}")
