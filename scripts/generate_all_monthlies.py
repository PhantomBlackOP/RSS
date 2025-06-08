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

START_DATE = datetime.date(2025, 1, 1)

monthly_lines = defaultdict(list)
monthly_wordcount = defaultdict(int)
monthly_tags = defaultdict(Counter)

for file in POSTS_DIR.glob("*.md"):
    text = file.read_text(encoding="utf-8")
    lines = text.splitlines()
    for line in lines:
        day_match = re.match(r"-\s+Day\s+(\d{3}):\s+\[(.*?)\]", line)
        if day_match:
            day_num = int(day_match.group(1))
            caption = day_match.group(2)
            post_date = START_DATE + datetime.timedelta(days=day_num - 1)
            key = (post_date.year, f"{post_date.month:02d}")
            monthly_lines[key].append((post_date, caption))
            monthly_wordcount[key] += len(re.findall(r"\b\w+\b", caption))
            tags = re.findall(r"#\w+", caption)
            if tags:
                monthly_tags[key].update(tags)
            else:
                fallback_words = [f"#{w.lower()}" for w in re.findall(r"\b\w{4,}\b", caption) if w.lower() not in STOPWORDS]
                monthly_tags[key].update(fallback_words)

for (year, month), posts in sorted(monthly_lines.items()):
    digest_path = MONTHLY_DIR / f"{year}-{month}.md"
    posts.sort()
    lines = [
        "---",
        "layout: page",
        f"title: {datetime.date(int(year), int(month), 1).strftime('%B')} {year} – Monthly Digest",
        f"permalink: /monthly/{year}-{month}/",
        "---",
        "",
        "## 📅 Daily Highlights",
        ""
    ]

    for post_date, caption in posts:
        lines.append(f"- {post_date.strftime('%b %d')}: {caption}")

    lines += [
        "",
        "---",
        "",
        "## 🔤 Word Stats",
        "",
        f"**Total words:** {monthly_wordcount[(year, month)]}",
        f"**Tag count:** {len(monthly_tags[(year, month)])}",
        "",
        "---",
        "",
        "## ☁️ Tag Cloud",
        ""
    ]

    for tag, count in monthly_tags[(year, month)].most_common():
        size = min(2.5, 1.0 + (count / max(monthly_tags[(year, month)].values())) * 1.5)
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
