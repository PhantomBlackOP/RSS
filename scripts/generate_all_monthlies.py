import re
import datetime
from pathlib import Path
from collections import defaultdict, Counter

POSTS_DIR = Path("_posts")
MONTHLY_DIR = Path("_monthly")
MONTHLY_DIR.mkdir(exist_ok=True)

pattern = re.compile(r"(\d{4})-(\d{2})-(\d{2})-week-(\d{2})\.md")
monthly_posts = defaultdict(list)

for file in POSTS_DIR.glob("*.md"):
    match = pattern.match(file.name)
    if match:
        year, month, day, week = match.groups()
        monthly_posts[(year, month)].append((int(week), day, file))

for (year, month), posts in sorted(monthly_posts.items()):
    digest_path = MONTHLY_DIR / f"{year}-{month}.md"
    posts.sort()
    lines = [
        "---",
        "layout: page",
        f"title: {datetime.date(int(year), int(month), 1).strftime('%B')} {year} – Monthly Digest",
        f"permalink: /monthly/{year}-{month}/",
        "---",
        "",
        "## 📅 Weekly Highlights",
        ""
    ]

    total_words = 0
    hashtag_counter = Counter()

    for week, day, file in posts:
        url = f"/{year}/{month}/{day}/week-{week}.html"
        title = f"Week {week} – Dailies & Highlights"
        lines.append(f"- {title} – [View]({url})")
        text = file.read_text(encoding="utf-8")
        hashtags = re.findall(r"#\w+", text)
        hashtag_counter.update(hashtags)
        total_words += len(re.findall(r"\b\w+\b", text))

    top_hashtags = ", ".join(f"`{tag}`" for tag, _ in hashtag_counter.most_common(3))

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
        f"Thanks for following along through {datetime.date(int(year), int(month), 1).strftime('%B')}!  \nSee you next month for more daily sparks from Trevorion.",
        "",
        f"_Last updated: {datetime.datetime.utcnow().strftime('%b %d, %Y')}_"
    ]

    digest_path.write_text("\n".join(lines), encoding="utf-8")
