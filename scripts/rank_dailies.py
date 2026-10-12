#!/usr/bin/env python3
"""Uniform, audit-friendly Daily scoring bound to the published Sitemap.

Every published Daily with a documented visual assessment is scored by the same
eight-criterion rubric. Four ratings are individually evaluated from published
artwork previews; the other four are REPRODUCIBLE ESTIMATES, not misrepresented
as independent fine-resolution human reviews.

Theme reach is estimated from *subject*, not views of an image, and is only a
tie-breaker for identical artistic merit.
"""
from __future__ import annotations
import html
import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data/daily_visual_reviews.json"
WEIGHTS = {
    "visual_impact": 20,
    "style": 15,
    "story": 15,
    "originality": 15,
    "execution": 15,
    "editorial_value": 10,
    "zine_identity": 5,
    "banner_suitability": 5,
}
DIMENSIONS = ("reach", "recognition", "cross_audience", "evergreen")
assert sum(WEIGHTS.values()) == 100
LABELS = {
    "visual_impact": "Visual impact",
    "style": "Style",
    "story": "Story",
    "originality": "Originality",
    "execution": "Execution estimate",
    "editorial_value": "Editorial value estimate",
    "zine_identity": "Zine identity estimate",
    "banner_suitability": "Banner suitability estimate",
}
DIRECT = frozenset(("visual_impact", "style", "story", "originality"))
GROUP_TERMS = {
    "myth": ("goddess", "mythology", "warhammer", "dragon", "paladin",
             "gundam", "batman", "goku", "knight", "elf", "wizard",
             "celestial", "spectral", "sorceress", "demon", "fantasy",
             "folklore", "fenrir", "jormungandr", "yggdrasil", "artemis",
             "kraken", "samurai", "kitsune", "revenant", "serpent", "sephiroth"),
    "history": ("ancient", "medieval", "victorian", "roman", "greek",
                "archaeology", "heritage", "ruins", "architecture",
                "renaissance", "palace", "temple", "basilica", "historical",
                "prehistoric", "fortress", "castle", "antique", "procession",
                "museum", "byzantine", "tradition", "gothic", "ritual",
                "ottoman", "maltese", "maltahistory", "sasanian"),
    "science": ("technology", "robot", "artificialintelligence",
                "space", "starship", "spacecraft", "science", "engineering",
                "mechanical", "machine", "aircraft", "helicopter", "physics",
                "biology", "astronomy", "asteroid", "nebula", "meteor",
                "computer", "cyberpunk", "mecha", "research", "medical",
                "laboratory", "grok", "rocket"),
    "nature": ("animal", "bird", "wildlife", "habitat", "nature", "plant",
               "flower", "garden", "woodland", "butterfly", "tiger", "lion",
               "iguana", "fish", "whale", "insect", "tree", "ecosystem",
               "waterfall", "river", "coast", "ocean", "sea", "botany",
               "mountain", "fauna", "flora", "capybara", "quokka", "bird"),
    "music": ("music", "song", "singer", "guitar", "violin", "piano",
              "concert", "stage", "performance", "choir", "dancer",
              "dance", "band", "opera", "festival", "flamenco", "fandango"),
    "personal": ("trevorion", "aurelia", "malta", "maltese", "gozo",
                 "birthday", "mother", "anniversary", "remembering",
                 "master of the rift", "zine"),
    "holiday": ("christmas", "santa", "advent", "easter", "halloween",
                "holiday", "rudolph", "nativity", "three kings", "new year"),
    "anime": ("anime", "manga", "gundam", "goku", "sephiroth",
              "chibi", "cosplay", "otaku"),
    "everyday": ("food", "dining", "cooking", "kitchen", "bread", "pizza",
                "spaghetti", "coffee", "tea", "hotel", "shop", "car",
                "bus", "road", "workshop", "home", "street", "town",
                "family", "birthday"),
}
# Images carry a real-story editorial description where a specific, already
# inspected winner has been reviewed in detail. Never mix with scoring weights.
WINNER_NOTES = {
    "430": "A formal tea party shared with skeletons makes a strikingly unusual gothic story. Its staging balances the macabre with humour.",
    "648": "A disciplined Dark Elf royal court, ceremonial guards, and monumental gothic architecture give a strong sense of hierarchy and worldbuilding.",
    "646": "The Zine's own band performs amid an electric rift-like stage spectacle, joining a distinct personal identity with dynamic group composition.",
    "460": "The dense celebratory street procession brings Maltese religious tradition, colour, movement and crowd storytelling together.",
    "643": "A figure amid a luminous forest waterfall creates a cohesive image of renewal, using water, light and gesture as narrative elements.",
    "649": "Artemis and the sacred stag stand within a sweeping moonlit wilderness, linking Greek mythology with atmosphere and character.",
    "562": "A ventriloquist commands an intent audience in a period interior, suggesting stagecraft, tension and an uncanny performance.",
    "236": "An enormous spectral wolf dwarfs a lone witness beneath auroral light, making mythological scale the image's central force.",
    "422": "An energetic festival dancer moves through a crowded celebration, giving the composition immediate rhythm and momentum.",
    "450": "A veteran adjusts a younger warrior's armour, turning preparation for an uncertain duty into an intimate narrative.",
    "530": "Two dancers animate a lively public performance, with gestures, costumes and a bustling street supplying rhythm and context.",
    "514": "An ancient apsara relief appears woven into the roots of a forest, blending archaeology, sculptural texture and nature.",
    "534": "A vast mythic sea-serpent cuts across a storm-torn ocean, using scale and weather to build atmosphere.",
    "413": "The luminous subterranean world is layered with crystal structures, waterfalls and a central light, creating an unusually rich fantasy landscape.",
    "369": "The monumental world-tree links waterfalls, roots and distant mountains into a vast, recognisable mythological setting.",
    "200": "A figure within a brilliantly lit stained-glass cathedral brings artistic creation and sacred architectural imagery together.",
    "435": "A storyteller holds a lantern-lit gathering's attention, with listeners and objects suggesting a larger tale beyond the frame.",
    "623": "A masked assassin approaches the royal figure in a candlelit hall, making a moment of jeopardy and suspense immediately legible.",
    "605": "Scheherazade is surrounded by an intricately furnished moonlit chamber, creating a visual setting for the stories of the Arabian Nights.",
    "226": "A solitary wanderer moves among vast ruined columns at sunset, combining a sense of journey with mysterious scale.",
    "300": "A solitary figure sits beside floating lanterns; the quiet light and setting turn a simple scene into an emotional milestone.",
    "371": "La Befana travels above a snowy village in a lively folklore scene, combining character, motion and winter atmosphere.",
    "429": "An unusual historical divination scene places a rooster amid observers and symbolic objects, telling the story of a rare practice.",
    "441": "A mounted knight and detailed armour stand within a believable historical crowd, with the destrier and equipment given weight.",
    "127": "An encounter across a candlelit table blends haunting intimacy and supernatural symbolism.",
    "128": "A lone silhouette enters a lantern-lit Kyoto street through rain and fog, suggesting a story of absence and return.",
    "207": "A railway farewell framed by period architecture uses restrained expressions to imply loss and separation.",
    "228": "A moss-covered circular gate occupies a luminous landscape, suggesting a portal and a journey beyond the visible world.",
}

def rating(x: Any, title: str) -> float:
    if isinstance(x, bool) or not isinstance(x, (int, float)):
        raise ValueError("Non-numeric rating: " + title)
    v = float(x)
    if not math.isfinite(v) or not 0 <= v <= 10 or v * 2 != round(v * 2):
        raise ValueError("Invalid 0–10 half-step rating: " + title)
    return v

def half(value: float) -> float:
    return max(0., min(10., round(value * 2) / 2.))

def topics(post: Any) -> set[str]:
    text = (post.title + " " + " ".join(post.tags)).lower()
    return {key for key, terms in GROUP_TERMS.items()
            if any(term in text for term in terms)}

def theme_scores(groups: set[str]) -> dict[str, float]:
    # Conceptual reach estimates. NOT image impressions, post views or analytics.
    if "holiday" in groups:
        values = [4.5, 4.5, 4.5, 4.5]
    elif "anime" in groups:
        values = [4.5, 4.5, 4., 4.]
    elif "music" in groups:
        values = [4., 3.5, 4.5, 4.5]
    elif "myth" in groups:
        values = [4.5, 4., 4., 4.5]
    elif "nature" in groups:
        values = [4., 3.5, 4.5, 5.]
    elif "history" in groups:
        values = [3.5, 3.5, 4., 4.5]
    elif "science" in groups:
        values = [4., 3.5, 4., 4.5]
    elif "everyday" in groups:
        values = [3.5, 3.5, 4.5, 4.5]
    else:
        values = [3., 3., 3.5, 4.]
    if len(groups) >= 3:
        values[2] = min(5, values[2] + .5)
    return dict(zip(DIMENSIONS, values))

@dataclass(frozen=True)
class RankedDaily:
    post: Any
    artistic_score: float
    theme_appeal: float
    scores: dict[str, float]
    theme_scores: dict[str, float]
    reasoning: str
    inspected_basis: str
    theme_labels: tuple[str, ...]

def ranked(entries: list[Any]) -> tuple[list[RankedDaily], int]:
    raw = json.loads(INPUT.read_text(encoding="utf8"))
    if raw.get("schema_version") != 2 or raw.get("rubric_version") != "2026-10-12-v2":
        raise ValueError("Unrecognized full-archive Daily visual review rubric")
    reviews = raw.get("reviews")
    if not isinstance(reviews, list) or len(reviews) < 669:
        raise ValueError("Refusing incomplete initial Daily review coverage")
    known = {e.url: e for e in entries if e.category == "Daily"}
    seen: set[str] = set()
    rated: list[RankedDaily] = []
    stale = 0
    for record in reviews:
        if not isinstance(record, dict):
            raise ValueError("Non-object review record")
        url = record.get("url")
        if not isinstance(url, str) or not url.startswith("https://zine.trevorion.io/"):
            raise ValueError("Invalid review permalink")
        if url in seen:
            raise ValueError("Duplicate Daily review "+url)
        seen.add(url)
        post = known.get(url)
        if post is None or post.image != record.get("image_url"):
            # The post/image changed: never reuse a score for a different artwork.
            stale += 1
            continue
        direct = record.get("ratings")
        if not isinstance(direct, dict) or set(direct) != DIRECT:
            raise ValueError("Missing any of the four direct visual criteria for "+url)
        scores = {k: rating(direct[k], k + " " + url) for k in DIRECT}
        vi, st, story, orig = (scores[k] for k in ("visual_impact", "style", "story", "originality"))
        groups = topics(post)
        scores["execution"] = half((vi + st) / 2)
        editorial = 6.5 + .20 * (story - 6) + .16 * (orig - 6)
        for category, bonus in (
            ("history", 1.2), ("science", 1.0), ("nature", .65),
            ("myth", .55), ("music", .75), ("personal", .75),
            ("holiday", .35)
        ):
            if category in groups:
                editorial += bonus
        scores["editorial_value"] = half(editorial)
        scores["zine_identity"] = half(.40 * st + .35 * orig + .25 * story +
                                      (.5 if "personal" in groups else 0))
        scores["banner_suitability"] = half(.55 * vi + .30 * st + .15 * story)
        artistic = round(sum(scores[k] * weight / 10 for k, weight in WEIGHTS.items()), 2)
        themed = theme_scores(groups)
        appeal = round(sum(themed.values()) / len(themed), 2)
        numbered = re.match(r"^(\d{3}):", post.title)
        story_note = WINNER_NOTES.get(numbered.group(1)) if numbered else None
        if story_note:
            note = story_note
        else:
            subject = " and ".join(sorted(groups)[:2]) if groups else "general creative art"
            note = (
                f"Whole-archive visual review: impact {vi:g}/10, style {st:g}/10, "
                f"story {story:g}/10, originality {orig:g}/10. "
                f"Related subjects: {subject}. Other dimensions are rubric-based estimates."
            )
        rated.append(RankedDaily(post, artistic, appeal, scores, themed, note,
                                 str(record.get("visual_review_basis") or "published Sitemap artwork preview"),
                                 tuple(sorted(groups))))
    rated.sort(key=lambda r: (-r.artistic_score, -r.theme_appeal, r.post.url))
    return rated, stale

def build_page(entries: list[Any], header: str) -> tuple[str, list[RankedDaily]]:
    items, stale = ranked(entries)
    published_count = sum(e.category == "Daily" for e in entries)
    n = len(items)
    lines = [
        header, "<h1>Top 20 Dailies</h1>",
        '<p class="home-lead">A ranking of the Zine’s published artworks based on '
        'a consistent eight-criterion artistic rubric, including style, story, '
        'originality and visual impact. Subject-theme appeal is a separate estimate '
        'used only to break artistic-score ties.</p>',
        f'<p class="ranking-coverage"><strong>{n} of {published_count} published Dailies evaluated.</strong> '
        'Complete archive first-pass assessment; scores remain provisional and '
        'await creator review. Four visual criteria were judged individually from '
        'published preview images, with the four remaining criteria calculated '
        'consistently from those observations and Sitemap metadata. '
        'Original-resolution detail has not been inspected for every entry.'
        + (f' {stale} stale or unavailable review(s) excluded.' if stale else '')
        + ' <a href="/top20/all/">See every scored Daily →</a></p>',
    ]
    if n < 20:
        lines.append("<p>Insufficient current published-image-bound reviews for a Top 20.</p>")
    else:
        lines.append('<ol class="top20-grid">')
        for item in items[:20]:
            post = item.post
            link, src = (html.escape(post.url, quote=True),
                         html.escape(post.thumbnail or post.image, quote=True))
            title = html.escape(post.title)
            detail = " · ".join(f"{LABELS[key]} {item.scores[key]:g}/10" for key in WEIGHTS)
            topics_label = " ".join(html.escape(t) for t in post.tags[:6])
            lines.append(
                '<li class="top20-item">'
                f'<a class="top20-art" href="{link}"><img src="{src}" alt="{title}" loading="lazy" decoding="async"></a>'
                '<div class="top20-info">'
                f'<div class="top20-scores"><strong>{item.artistic_score:.2f}<span>/100 art</span></strong>'
                f'<span>Theme appeal {item.theme_appeal:.2f}/5</span></div>'
                f'<h2><a href="{link}">{title}</a></h2>'
                f'<p>{html.escape(item.reasoning)}</p>'
                f'<div class="top20-tags">{topics_label}</div>'
                '<details><summary>Individual scoring breakdown</summary>'
                f'<p>{html.escape(detail)}</p>'
                f'<p>Theme reach {item.theme_scores["reach"]:g}/5, recognition {item.theme_scores["recognition"]:g}/5, '
                f'cross-audience {item.theme_scores["cross_audience"]:g}/5, evergreen {item.theme_scores["evergreen"]:g}/5.</p>'
                '</details></div></li>'
            )
        lines.append('</ol>')
    lines.append(
        '<p><a href="/top20/all/">Complete scored ranking →</a> · '
        '<a href="https://github.com/PhantomBlackOP/RSS/blob/main/docs/daily-rankings.md">'
        'Rubric and limitations ↗</a></p>'
    )
    return "\n".join(lines) + "\n", items

def full_catalog(ranking: list[RankedDaily], header: str) -> str:
    lines = [
        header, "# Full Daily Scores",
        "Every reviewed Daily, without genre, date, or aspect-ratio exclusions. "
        "The artistic score is out of 100; theme appeal is a separate subject-interest estimate out of 5. "
        "The rankings are provisional AI-assisted first-pass assessments. "
        "[Top 20 artwork view](/top20/).",
        "",
        "| Rank | Published Daily | Artistic merit | Theme appeal |",
        "|---:|---|---:|---:|",
    ]
    for i, entry in enumerate(ranking, 1):
        post = entry.post
        label = post.title.replace("|", r"\|").replace("\n", " ")
        lines.append(f"| {i} | [{label}]({post.url}) | {entry.artistic_score:.2f} | {entry.theme_appeal:.2f} |")
    lines.append(
        "\n[View complete criterion-by-criterion evaluation JSON]"
        "(https://github.com/PhantomBlackOP/RSS/blob/main/data/daily_reviews.json)."
    )
    return "\n".join(lines) + "\n"

def audit_json(ranking: list[RankedDaily], n_published: int) -> str:
    payload = {
        "schema_version": 3,
        "rubric_version": "2026-10-12-v2",
        "assessment_status": "Provisional AI-assisted whole-archive visual review; creator approval pending.",
        "published_daily_count": n_published,
        "reviewed_daily_count": len(ranking),
        "review_limitations": (
            "Four visual criteria judged at published small-preview scale. "
            "Execution, editorial value, Zine identity and banner suitability "
            "are reproducible estimates, not independent high-resolution reviews. "
            "Theme appeal is a subject-interest estimate, never actual engagement."
        ),
        "weights": WEIGHTS,
        "rankings": [
            {
                "rank": i, "url": x.post.url,
                "title": x.post.title, "image_url": x.post.image,
                "tags": list(x.post.tags), "date": x.post.date.isoformat(),
                "artistic_merit": x.artistic_score,
                "theme_appeal": x.theme_appeal,
                "scores": x.scores, "theme_scores": x.theme_scores,
                "theme_classes": list(x.theme_labels),
                "directly_reviewed_criteria": sorted(DIRECT),
                "reasoning": x.reasoning,
                "visual_review_basis": x.inspected_basis,
            }
            for i, x in enumerate(ranking, 1)
        ],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
