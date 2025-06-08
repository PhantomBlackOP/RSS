import re
import datetime
from pathlib import Path
from collections import defaultdict, Counter

POSTS_DIR = Path("_posts")
MONTHLY_DIR = Path("monthly")
MONTHLY_DIR.mkdir(exist_ok=True)

STOPWORDS = [
    "the", "this", "that", "and", "with", "from", "into", "over", "your",
    "have", "has", "was", "were", "been", "are", "for", "out", "all", "but",
    "you", "not", "just", "very", "some", "more", "than", "then", "once"
]

pattern = re.compile(r"(\d{4})-(\d{2})-(\d{2})-week-(\d{2})\.md")
monthly_posts = defaultdict(list)

for file in POSTS_DIR.glob("*.md"):
    match = pattern.match(file.name)
    if match:
        year, month, day, week = match.groups()
        monthly_posts[(year, month)].append((int(week), day, file))

def extract_tags(text, filename):
    tags = re.findall(r"#\w+", text)
    if tags:
        print(f"[{filename}] ✅ Found hashtags: {tags}")
        return tags
    titles = re.findall(r"-\s+Day\s+\d+:\s+\[([^\]]+)\]", text)
    print(f"[{filename}] 📋 Day titles extracted: {titles}")
    words = []
    for title in titles:
        extracted = re.findall(r"\b\w{4,}\b", title)
        print(f"[{filename}] ➕ Extracted words: {extracted}")
        words += extracted
    result = [f"#{w.lower()}" for w in words if w.lower() not in STOPWORDS]
    print(f"[{filename}] 🏷️ Final fallback tags: {result}")
    return result

for (year, month), posts in sorted(monthly_posts.items()):
    digest_path = MONTHLY_DIR / f"{year}-{month}.md"
    posts.sort()
    lines = [
        "---",
        "layout: page",
        f"title: {datetime.date(int(year), int(month), 1).strftime('%B')} {year} – Monthly Digest",
        f"permalink: /monthly/{year}-{month}.md",
        "---",
        "",
        "## 📅 Weekly Highlights",
        ""
    ]

    total_words = 0
    tag_counter = Counter()

    for week, day, file in posts:
        url = f"/{year}/{month}/{day}/week-{week}.html"
        title = f"Week {week} – Dailies & Highlights"
        lines.append(f"- {title} – [View]({url})")
        text = file.read_text(encoding="utf-8")
        tags = extract_tags(text, file.name)
        if tags:
            tag_counter.update(tags)
        total_words += len(re.findall(r"\b\w+\b", text))

    lines += [
        "",
        "---",
        "",
        "## 🔤 Word Stats",
        "",
        f"**Total words:** {total_words}",
        f"**Tag count:** {len(tag_counter)}",
        "",
        "---",
        "",
        "## ☁️ Tag Cloud",
        ""
    ]

    for tag, count in tag_counter.most_common():
        size = min(2.5, 1.0 + (count / max(tag_counter.values())) * 1.5)
        lines.append(f"<span style=\"font-size: {size:.1f}em; margin-right: 0.5em;\">{tag}</span>")

    lines += [
        "",
        "---",
        "",
        "## 🌟 Closing Note",
        "",
        f"Thanks for following along through {datetime.date(int(year), int(month), 1).strftime('%B')}!  \nSee you next month for more daily sparks from Trevorion.",
        "",
        f"_Last updated: {datetime.datetime.utcnow().strftime('%b %d, %Y')}_"    
    ]

    digest_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"✅ Wrote monthly digest: {digest_path}")
