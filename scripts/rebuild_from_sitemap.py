#!/usr/bin/env python3
"""Rebuild the legacy Trevorion RSS site from published Sitemap XML only.

Never fetches WordPress or X. Fail closed before touching existing output.
"""
from __future__ import annotations

import argparse
import calendar
import html
import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from rank_dailies import build_page

ROOT = Path(__file__).resolve().parents[1]
SITEMAP_ROOT = "https://sitemap.trevorion.io"
SM = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
META = "{https://sitemap.trevorion.io/ns/meta}"
IMAGE = "{http://www.google.com/schemas/sitemap-image/1.1}"
SECTIONS = ("archive", "news", "articles", "comics", "shop")
SECTION_HEADERS = {
    "archive": "Dailies",
    "news": "News",
    "articles": "Articles",
    "comics": "Comics",
    "shop": "Shop",
}
MIN_GALLERY_IMAGE_COVERAGE = 1.00
DATE_RE = re.compile(r"^\d{4}-\d{2}$")


@dataclass(frozen=True)
class Entry:
    url: str
    title: str
    date: datetime
    category: str
    image: str | None
    thumbnail: str | None
    mosaic: str | None
    tags: tuple[str, ...]


def read_xml(url: str) -> ET.Element:
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.netloc != "sitemap.trevorion.io":
        raise ValueError(f"Untrusted Sitemap URL: {url}")
    req = Request(url, headers={"User-Agent": "Trevorion-RSS-Sitemap-Consumer/2.0"})
    with urlopen(req, timeout=75) as response:
        data = response.read()
    return ET.fromstring(data)


def value(node: ET.Element, tag: str) -> str:
    return (node.findtext(tag) or "").strip()


def gather() -> list[Entry]:
    result: dict[str, Entry] = {}
    for section in SECTIONS:
        index = read_xml(f"{SITEMAP_ROOT}/zine/{section}.xml")
        if index.tag != SM + "sitemapindex":
            raise ValueError(f"Expected sitemap index for {section}")
        child_links = [
            value(node, SM + "loc") for node in index.findall(SM + "sitemap")
        ]
        if not child_links:
            raise ValueError(f"Missing monthly Sitemap children for {section}")
        for child in child_links:
            parsed = urlparse(child)
            if (
                parsed.scheme != "https"
                or parsed.netloc != "sitemap.trevorion.io"
                or not re.fullmatch(rf"/zine/{section}/\d{{4}}-\d{{2}}\.xml", parsed.path)
            ):
                raise ValueError(f"Unexpected {section} child Sitemap: {child}")
            document = read_xml(child)
            if document.tag != SM + "urlset":
                raise ValueError(f"Expected URL set in {child}")
            for node in document.findall(SM + "url"):
                link = value(node, SM + "loc")
                title = value(node, META + "title")
                published = value(node, META + "published")
                category = value(node, META + "category")
                image_url = value(node, META + "og_image")
                thumbnail_url = value(node, META + "thumbnail_image")
                mosaic_url = value(node, META + "mosaic_image")
                if not image_url:
                    image_node = node.find(IMAGE + "image")
                    if image_node is not None:
                        image_url = value(image_node, IMAGE + "loc")
                raw_tags = value(node, META + "tags")
                if not link.startswith("https://zine.trevorion.io/"):
                    raise ValueError(f"Invalid post URL in Sitemap: {link}")
                if not title or not published or not category:
                    raise ValueError(f"Missing post metadata in {child}: {link}")
                if image_url and not image_url.startswith("https://"):
                    raise ValueError(f"Non-HTTPS image for {link}")
                if thumbnail_url and not thumbnail_url.startswith("https://"):
                    raise ValueError(f"Non-HTTPS thumbnail for {link}")
                if mosaic_url and not mosaic_url.startswith("https://"):
                    raise ValueError(f"Non-HTTPS mosaic image for {link}")
                try:
                    published_dt = datetime.fromisoformat(published.replace("Z", "+00:00"))
                    if published_dt.tzinfo is None:
                        published_dt = published_dt.replace(tzinfo=timezone.utc)
                    tags = tuple(json.loads(raw_tags)) if raw_tags else ()
                    if not isinstance(tags, tuple) or any(not isinstance(t, str) for t in tags):
                        raise ValueError("Malformed tag metadata")
                except (ValueError, TypeError) as exc:
                    raise ValueError(f"Invalid metadata for {link}: {exc}") from exc
                entry = Entry(link, title, published_dt, category, image_url or None, thumbnail_url or None, mosaic_url or None, tags)
                prior = result.get(link)
                if prior and prior != entry:
                    raise ValueError(f"Conflicting duplicate post URL: {link}")
                result[link] = entry

    entries = sorted(result.values(), key=lambda e: (e.date, e.url))
    dailies = [e for e in entries if e.category == "Daily"]
    with_images = [e for e in dailies if e.image]
    if not dailies:
        raise ValueError("Sitemap contains no published Dailies; refusing to clear archives")
    ratio = len(with_images) / len(dailies)
    if ratio < MIN_GALLERY_IMAGE_COVERAGE:
        raise ValueError(
            f"Only {len(with_images)}/{len(dailies)} Dailies have Sitemap image "
            f"metadata ({ratio:.1%}). Waiting for Sitemap enrichment, not deleting archives."
        )
    if len(entries) < len(dailies):
        raise ValueError("Inconsistent Sitemap post inventory")
    print(f"Verified Sitemap entries: {len(entries)}; Dailies: {len(dailies)}; images: {len(with_images)}")
    if len(with_images) != len(dailies):
        print("Missing Daily images: " + ", ".join(e.url for e in dailies if not e.image), file=sys.stderr)
    return entries


def frontmatter(*, layout: str, title: str, permalink: str, date_value: str = "") -> str:
    fields = ["---", f"layout: {layout}", f"title: {json.dumps(title, ensure_ascii=False)}"]
    if date_value:
        fields.append(f"date: {date_value}")
    fields.extend((f"permalink: {permalink}", "show_title: false", "---", ""))
    return "\n".join(fields) + "\n"


def daily_label(entry: Entry) -> str:
    return entry.title


def format_link(entry: Entry) -> str:
    # Avoid Markdown link ambiguity from real article titles containing brackets.
    return f'<a href="{html.escape(entry.url, quote=True)}">{html.escape(entry.title)}</a>'


def month_label(key: str) -> str:
    year, month = map(int, key.split("-"))
    return f"{calendar.month_name[month]} {year}"


def gallery_html(entry: Entry) -> str:
    if not entry.image:
        return ""
    target = html.escape(entry.url, quote=True)
    src = html.escape(entry.mosaic or entry.thumbnail or entry.image, quote=True)
    alt = html.escape(entry.title, quote=True)
    return f'<a href="{target}"><img src="{src}" alt="{alt}" loading="lazy" style="width:50px;height:auto;"></a>'


def week_start(entry: Entry) -> tuple[int, int, date]:
    year, week, weekday = entry.date.isocalendar()
    return year, week, entry.date.date() - timedelta(days=weekday - 1)


def generate(entries: list[Entry]) -> dict[Path, str]:
    outputs: dict[Path, str] = {}
    dailies = [e for e in entries if e.category == "Daily"]
    months: dict[str, list[Entry]] = defaultdict(list)
    years: dict[int, list[Entry]] = defaultdict(list)
    weeks: dict[tuple[int, int, date], list[Entry]] = defaultdict(list)
    for entry in dailies:
        months[entry.date.strftime("%Y-%m")].append(entry)
        years[entry.date.year].append(entry)
    for entry in entries:
        weeks[week_start(entry)].append(entry)

    # The header mosaic uses only canonical Daily thumbnails and refreshes every run.
    # Interleave a cross-archive selection with recent releases, including specials.
    spread = [dailies[round(i * (len(dailies) - 1) / 31)] for i in range(32)]
    newest = list(reversed(dailies[-32:]))
    chosen: list[Entry] = []
    seen: set[str] = set()
    for older, newer in zip(spread, newest):
        for item in (older, newer):
            if item.url not in seen and item.image:
                chosen.append(item)
                seen.add(item.url)
    for item in reversed(dailies):
        if len(chosen) >= 64:
            break
        if item.url not in seen and item.image:
            chosen.append(item)
            seen.add(item.url)
    outputs[Path("_includes/zine-hero.html")] = "\n".join(
        f'<div class="tile">'
        f'<img src="{html.escape(item.mosaic or item.thumbnail or item.image or "", quote=True)}" alt="" '
        f'loading="{"eager" if i < 16 else "lazy"}" decoding="async"></div>'
        for i, item in enumerate(chosen[:64])
    ) + "\n"

    # Each yearly gallery provides image links and the historical 50px thumbnail strip.
    for year, rows in sorted(years.items()):
        rows = sorted(rows, key=lambda e: (e.date, e.url))
        outputs[Path(f"gallery/{year}-gallery.md")] = (
            frontmatter(layout="page", title=f"Daily Images Gallery {year}", permalink=f"/gallery/{year}/")
            + f"# Daily Image Gallery {year}\n\n"
            + f"<p>{len(rows)} Daily artworks and special editions. Select any image to view its original Zine post.</p>\n\n"
            + '<div class="gallery-grid">\n'
            + "\n".join(gallery_html(e) for e in rows if e.image)
            + '\n</div>\n\n'
            + '<details class="archive-list"><summary>Browse all artwork titles</summary><ul>\n'
            + "\n".join(
                f'<li>{html.escape(daily_label(e))}: <a href="{html.escape(e.url, quote=True)}">View Daily</a>'
                + (f' | <a href="{html.escape(e.image, quote=True)}">Full artwork</a>' if e.image else "")
                + "</li>"
                for e in rows
            )
            + "\n</ul></details>\n"
        )
        outputs[Path(f"gallery/{year}-gallery-thumbs.md")] = (
            "\n".join(gallery_html(e) for e in rows if e.image) + "\n"
        )

    outputs[Path("gallery/gallery-thumbs.md")] = (
        "\n".join(gallery_html(e) for e in dailies if e.image) + "\n"
    )
    outputs[Path("gallery/index.md")] = (
        frontmatter(layout="page", title="Daily Images Gallery", permalink="/gallery/")
        + "# 🖼️ Daily Images Gallery\n\n"
        + "\n".join(
            f"- [{year} Daily artwork mosaic](/gallery/{year}/)"
            for year in sorted(years, reverse=True)
        )
        + "\n\n" + '<div class="gallery-grid">\n' + outputs[Path("gallery/gallery-thumbs.md")] + '</div>\n'
    )

    # Preserve the original monthly-digest structure and statistics.
    month_order = sorted(months)
    for month, rows in sorted(months.items()):
        rows = sorted(rows, key=lambda e: (e.date, e.url))
        tags = Counter(t for e in rows for t in e.tags)
        outputs[Path(f"monthly/{month}.md")] = (
            frontmatter(layout="page", title=f"Monthly Digest {month}", permalink=f"/monthly/{month}.html").replace(
                "show_title: false\n",
                "page_type: monthly\n"
                + (f"prev_url: /monthly/{month_order[month_order.index(month) - 1]}.html\n" if month_order.index(month) > 0 else "")
                + (f"next_url: /monthly/{month_order[month_order.index(month) + 1]}.html\n" if month_order.index(month) < len(month_order) - 1 else "")
                + "show_title: false\n",
            )
            + f"# 📅 Monthly Digest – {month_label(month)}\n\n"
            + "\n".join(f"- {format_link(e)}" for e in rows)
            + f"\n\n🖼️ Total days: {len(rows)} | 🏷️ Unique tags: {len(tags)}\n\n"
            + ("🔥 Top tags: " + ", ".join(f"{tag} ({n})" for tag, n in tags.most_common(8)) + "\n\n" if tags else "")
            + ("☁️ Tag cloud:\n" + " ".join(sorted(tags)) + "\n" if tags else "")
        )
    monthly_index = [frontmatter(layout="page", title="Monthly AI Anime Digests", permalink="/monthly/"),
                     "# 🗓️ Monthly Digests\n\n"]
    for year in sorted({x.split("-")[0] for x in months}, reverse=True):
        monthly_index.append(f"## {year}\n\n")
        for month in sorted((x for x in months if x.startswith(year + "-")), reverse=True):
            monthly_index.append(f"- [{month_label(month)}](/monthly/{month}.html)\n")
        monthly_index.append("\n")
    outputs[Path("monthly_index.md")] = "".join(monthly_index)

    # Weekly digests remain actual Jekyll posts so both existing feeds keep working.
    recent_weeks = []
    for (year, week, monday), rows in sorted(weeks.items(), reverse=True):
        rows = sorted(rows, key=lambda e: (e.date, e.url))
        name = f"Week {week:02d} – Dailies & Highlights"
        filename = f"_posts/{monday:%Y-%m-%d}-week-{week:02d}.md"
        public_url = f"/{monday:%Y/%m/%d}/week-{week:02d}.html"
        sections = []
        for key in SECTIONS:
            relevant = [e for e in rows if e.category == {
                "archive": "Daily", "news": "News", "articles": "Articles",
                "comics": "Comics", "shop": "Shop",
            }[key]]
            if not relevant:
                continue
            sections.append(f"## {SECTION_HEADERS[key]}\n\n")
            for entry in relevant:
                thumbnail = (gallery_html(entry) + " ") if entry.image else ""
                sections.append(f"- {thumbnail}{format_link(entry)}\n")
            sections.append("\n")
        outputs[Path(filename)] = (
            frontmatter(
                layout="post",
                title=name,
                date_value=f"{monday:%Y-%m-%d} 12:00:00 +0000",
                permalink=public_url,
            )
            + f"# {name}\n\n" + "".join(sections)
            + "---\n\nFrom the [Trevorion Zine](https://zine.trevorion.io/).\n"
        )
        recent_weeks.append((year, week, monday, public_url))

    recent_weeks.sort(reverse=True)
    if not recent_weeks:
        raise ValueError("No weeks generated")
    latest = recent_weeks[0]
    outputs[Path("archive.md")] = (
        frontmatter(layout="page", title="Archive", permalink="/archive/")
        + "# 📚 Weekly Archive\n\n"
        + "\n".join(
            f"- [{year} Week {week:02d} – Dailies & Highlights]({url}) ({monday:%b %d, %Y})"
            for year, week, monday, url in recent_weeks
        )
        + "\n"
    )
    # The RSS homepage uses the same Daily inventory as the main gallery.
    # This entire section is regenerated from Sitemap, not edited by hand.
    recent = list(reversed(dailies[-6:]))
    recent_html = "\n".join(
        f'<a href="{html.escape(e.url, quote=True)}">'
        f'<img src="{html.escape(e.thumbnail or e.image or "", quote=True)}" alt="" loading="lazy" decoding="async">'
        f'<span>{html.escape(e.title)}</span></a>'
        for e in recent
    )
    outputs[Path("index.md")] = (
        frontmatter(layout="page", title="Trevorion Zine RSS", permalink="/")
        + '<h1 class="home-heading">The Zine, one week at a time.</h1>\n'
        + '<p class="home-lead">Original Dailies, occasional special editions, '
          'news, articles and creative work. A weekly record of the Trevorion Zine, '
          'preserved and linked directly to each published post.</p>\n'
        + '<section class="feature" aria-labelledby="latest-title">\n'
        + '  <div><div class="kicker">Latest weekly digest</div>\n'
        + f'    <h2 id="latest-title">{latest[0]} · Week {latest[1]:02d}</h2>\n'
        + '    <p>Published Dailies, stories and highlights from this week.</p></div>\n'
        + f'  <a class="action" href="{latest[3]}">Read latest digest →</a>\n'
        + '</section>\n'
        + '<section class="portal-grid" aria-label="Browse the Zine RSS archive">\n'
        + '  <a class="portal-card" href="/archive/"><span class="card-icon">▤</span>'
          '<strong>Weekly archive</strong><span>Browse every digest, newest first.</span></a>\n'
        + '  <a class="portal-card" href="/monthly/"><span class="card-icon">▦</span>'
          '<strong>Monthly Dailies</strong><span>Artwork titles, dates, and subjects by month.</span></a>\n'
        + '  <a class="portal-card" href="/gallery/"><span class="card-icon">▧</span>'
          '<strong>Image gallery</strong><span>See your Dailies and special releases together.</span></a>\n'
        + '  <a class="portal-card" href="/top20/"><span class="card-icon">★</span>'
          '<strong>Top 20 Dailies</strong><span>Published artwork ranked by artistic merit.</span></a>\n'
        + '</section>\n'
        + '<section aria-labelledby="recent-title">\n'
        + ' <div class="section-header"><h2 id="recent-title">Latest Daily artwork</h2>'
          '<a href="/gallery/">All Dailies →</a></div>\n'
        + ' <div class="recent-art">\n' + recent_html + '\n</div>\n'
        + '</section>\n'
        + '<nav class="feed-strip" aria-label="RSS subscriptions">\n'
        + ' <strong>Subscribe:</strong> <a href="/feed.xml">Weekly RSS feed</a> '
          '<a href="/full-feed.xml">Complete feed</a> '
          '<a href="https://sitemap.trevorion.io/">Source sitemap ↗</a> '
          '<a href="https://zine.trevorion.io/">Visit the Zine ↗</a>\n'
        + '</nav>\n'
    )

    outputs[Path("top20/index.md")], _ranked = build_page(
        entries, frontmatter(layout="page", title="Top 20 Dailies", permalink="/top20/")
    )

    return outputs


def write_outputs(outputs: dict[Path, str]) -> None:
    if len(outputs) < 10:
        raise ValueError("Suspiciously few output files; refusing to clean old archives")
    for path, content in outputs.items():
        if "x.com/Trevorion" in content or "pbs.twimg.com" in content:
            raise ValueError(f"Legacy X link in generated output {path}")
        if not content.strip():
            raise ValueError(f"Empty output {path}")

    targets = {ROOT / path for path in outputs}
    old_generated: set[Path] = set()
    for folder, glob in (
        ("_posts", "*-week-*.md"),
        ("monthly", "????-??.md"),
        ("gallery", "*gallery*.md"),
    ):
        old_generated.update((ROOT / folder).glob(glob))
    # Remove obsolete X-derived archives only after successful full validation.
    old_generated.add(ROOT / "gallery/2025-gallery-200th-day.md")
    stale = old_generated - targets
    updated = 0
    for path, content in sorted(outputs.items()):
        target = ROOT / path
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists() or target.read_text(encoding="utf-8") != content:
            target.write_text(content, encoding="utf-8")
            updated += 1
    for path in sorted(stale):
        if path.exists():
            path.unlink()
    print(f"Generated {len(outputs)} outputs ({updated} updated); cleared {len(stale)} obsolete archive files")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Validate Sitemap input only; do not write")
    args = parser.parse_args()
    entries = gather()
    if args.check:
        print("Sitemap passed validation; dry run complete.")
    else:
        write_outputs(generate(entries))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError, ET.ParseError) as exc:
        print(f"RSS rebuild aborted: {exc}", file=sys.stderr)
        raise SystemExit(1)
