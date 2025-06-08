import os
import re
import datetime
from collections import Counter
from pathlib import Path

POSTS_DIR = Path("_posts")
MONTHLY_DIR = Path("_monthly")
MONTHLY_DIR.mkdir(exist_ok=True)

def generate_digest(year, month):
    digest_path = MONTHLY_DIR / f"{year}-{month:02}.md"
    pattern = re.compile(rf"{year}-{month:02}-(\d{{2}})-week-(\d{{2}})\.md")
    posts = []

    for file in POSTS_DIR.glob(f"{year}-{month:02}-*-week-*.md"):
        match = pattern.match(file.name)
        if match:
            day, week = match.groups()
            url = f"/{year}/{month:02}/{day}/week-{week}.html"
            title = f"Week {int(week)} – Dailies & Highlights"
            posts.append((int(week), day, title, url))

    posts.sort()
    hashtag_counter = Counter()
    total_words = 0

    for week, day, _, _ in posts:
        file_path = POSTS_DIR / f"{year}-{month:02}-{day}-week-{week:02}.md"
        if file_path.exists():
            text = file_path.read_text(encoding="utf-8")
            hashtags = re.findall(r"#\w+", text)
            hashtag_counter.update(hashtags)
            total_words += len(re.findall(r"\b\w+\b", text))

    top_hashtags = ", ".join(f"`{tag}`" for tag, _ in hashtag_counter.most_common(3))
    lines = [
        "---",
        "layout: page",
        f"title: {datetime.date(1900, month, 1).strftime('%B')} {year} – Monthly Digest",
        f"permalink: /monthly/{year}-{month:02}/",
        "---",
        "",
        "## 📅 Weekly Highlights",
        ""
    ]

    for _, day, title, url in posts:
        lines.append(f"- {title} – [View]({url})")

    lines += [
        "",
        "---",
        "",
        "## 🔤 Word Stats",
        "",
        f"**Total words:** {total_words}",
        f"**Top hashtags:** {top_hashtags}",
        "",
        "---",
        "",
        "## 🌟 Closing Note",
        "",
        f"Thanks for following along through {datetime.date(1900, month, 1).strftime('%B')}!  \nSee you next month for more daily sparks from Trevorion.",
        "",
        f"_Last updated: {datetime.datetime.utcnow().strftime('%b %d, %Y')}_"
    ]

    digest_path.write_text("\n".join(lines), encoding="utf-8")

# Generate current month (autodetect)
today = datetime.date.today()
generate_digest(today.year, today.month)
