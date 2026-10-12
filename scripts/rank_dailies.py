#!/usr/bin/env python3
"""Auditable, publication-bound editorial ranking for published Zine Dailies.

Artistic score is 0-100. Subject/theme appeal is separately scored 0-5 and
used ONLY to break an identical artistic score (never as an artistic bonus).
This module does not request WordPress, media URLs, or anything except data
already provided by the Sitemap consumer.
"""
from __future__ import annotations
import html
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ART_WEIGHTS = {
    "visual_impact": 20,
    "style": 15,
    "story": 15,
    "originality": 15,
    "execution": 15,
    "editorial_value": 10,
    "zine_identity": 5,
    "banner_suitability": 5,
}
THEME_KEYS = ("reach", "recognition", "cross_audience", "evergreen")
assert sum(ART_WEIGHTS.values()) == 100
FRIENDLY = {
    "visual_impact": "Visual impact",
    "style": "Style",
    "story": "Story",
    "originality": "Originality",
    "execution": "Execution",
    "editorial_value": "Editorial value",
    "zine_identity": "Zine identity",
    "banner_suitability": "Banner suitability",
}
REVIEW_FILE = Path(__file__).resolve().parents[1] / "data" / "daily_reviews.json"


@dataclass(frozen=True)
class RankedDaily:
    post: Any
    artistic_score: float
    theme_appeal: float
    scores: dict[str, float]
    theme_scores: dict[str, float]
    reasoning: str


def _require_score(value: Any, scale: int, title: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{title}: expected numeric rating 0-{scale}")
    rating = float(value)
    if not math.isfinite(rating) or not 0 <= rating <= scale:
        raise ValueError(f"{title}: rating outside 0-{scale}")
    # Half-point increments are supported; finer precision is not defensible.
    if rating * 2 != round(rating * 2):
        raise ValueError(f"{title}: ratings require whole or half points")
    return rating


def ranked(entries: list[Any]) -> tuple[list[RankedDaily], int]:
    """Require explicit, evidenced visual reviews; never fabricate scores from tags."""
    raw = json.loads(REVIEW_FILE.read_text(encoding="utf8"))
    if raw.get("schema_version") != 1 or raw.get("rubric_version") != "2026-10-12-v1":
        raise ValueError("Unrecognized Daily score rubric version")
    reviews = raw.get("reviews")
    if not isinstance(reviews, list):
        raise ValueError("Score file requires reviews array")
    all_dailies = {e.url: e for e in entries if e.category == "Daily"}
    seen: set[str] = set()
    approved: list[RankedDaily] = []
    stale = 0
    for r in reviews:
        if not isinstance(r, dict):
            raise ValueError("Score entry is not an object")
        url = r.get("url")
        if not isinstance(url, str) or not url.startswith("https://zine.trevorion.io/"):
            raise ValueError("Invalid scored Zine post URL")
        if url in seen:
            raise ValueError("Duplicate scored Daily "+url)
        seen.add(url)
        entry = all_dailies.get(url)
        if entry is None:
            stale += 1
            continue
        if r.get("image_url") != entry.image:
            # A post's published image was edited or replaced: do not silently reuse an old score.
            stale += 1
            continue
        dimensions = r.get("original_dimensions")
        if not isinstance(dimensions, list) or len(dimensions) != 2:
            raise ValueError(f"Review missing verified original dimensions for {url}")
        if not all(isinstance(n, int) and not isinstance(n, bool) and n >= 100 for n in dimensions):
            raise ValueError(f"Invalid original image dimensions for {url}")
        w, h = dimensions
        if abs(w / h - 1.5) > 0.012:
            raise ValueError(f"Non-3:2 image present among eligible rankings: {url} ({w}x{h})")
        scores = r.get("scores")
        if not isinstance(scores, dict) or set(scores) != set(ART_WEIGHTS):
            raise ValueError(f"Missing/unexpected criterion ratings for {url}")
        scores = {k: _require_score(v, 10, f"{url}: {k}") for k, v in scores.items()}
        subs = r.get("theme_appeal")
        if not isinstance(subs, dict) or set(subs) != set(THEME_KEYS):
            raise ValueError(f"Missing/unexpected theme appeal dimensions for {url}")
        subs = {k: _require_score(v, 5, f"{url}: {k}") for k, v in subs.items()}
        reasoning = r.get("reasoning", "")
        if not isinstance(reasoning, str) or len(reasoning.strip()) < 24 or len(reasoning) > 700:
            raise ValueError(f"Review lacks substantive reasoning: {url}")
        if r.get("review_type") != "AI-assisted editorial assessment":
            raise ValueError(f"Review provenance missing for {url}")
        art = round(sum(scores[k] * weight / 10 for k, weight in ART_WEIGHTS.items()), 2)
        theme = round(sum(subs.values()) / len(subs), 2)
        approved.append(RankedDaily(entry, art, theme, scores, subs, reasoning.strip()))
    approved.sort(key=lambda s: (-s.artistic_score, -s.theme_appeal, s.post.url))
    return approved, stale


def build_page(entries: list[Any], header: str) -> tuple[str, list[RankedDaily]]:
    ranking, stale = ranked(entries)
    n_total = sum(e.category == "Daily" for e in entries)
    output = [
        header,
        '<h1>Top 20 Dailies</h1>',
        '<p class="home-lead">An artistic ranking of the Zine’s published Dailies. '
        'Individual artwork is evaluated for visual impact, style, storytelling, '
        'originality, execution, editorial value, Zine identity and banner suitability. '
        'Theme popularity is tracked separately and breaks ties only.</p>',
        f'<p class="ranking-coverage">{len(ranking)} of {n_total} published Dailies have completed '
        f'an AI-assisted editorial assessment.'
        + (f' {stale} image-changed or unavailable review(s) excluded.' if stale else '')
        + ' These rankings remain provisional until full-archive evaluation and creator review.</p>',
    ]
    if len(ranking) < 20:
        output += [
            '<p>No Top 20 is published yet: fewer than 20 fully documented, '
            'original-image-verified reviews are available.</p>',
        ]
        return "\n".join(output)+"\n", ranking
    output.append('<ol class="top20-grid">')
    for item in ranking[:20]:
        post = item.post
        src = html.escape(post.thumbnail or post.image, quote=True)
        url = html.escape(post.url, quote=True)
        title = html.escape(post.title)
        notes = html.escape(item.reasoning)
        breakdown = " · ".join(
            f"{FRIENDLY[k]} {item.scores[k]:g}/10" for k in ART_WEIGHTS
        )
        labels = ", ".join(html.escape(tag) for tag in post.tags[:7])
        output.append(
            '<li class="top20-item">'
            f'<a class="top20-art" href="{url}"><img src="{src}" alt="{title}" loading="lazy" decoding="async"></a>'
            '<div class="top20-info">'
            f'<div class="top20-scores"><strong>{item.artistic_score:.1f}<span>/100 art</span></strong>'
            f'<span>Theme appeal {item.theme_appeal:.2f}/5</span></div>'
            f'<h2><a href="{url}">{title}</a></h2>'
            f'<p>{notes}</p>'
            f'<div class="top20-tags">{labels}</div>'
            f'<details><summary>Scoring breakdown</summary><p>{html.escape(breakdown)}</p>'
            f'<p>Theme: reach {item.theme_scores["reach"]:g}, recognition {item.theme_scores["recognition"]:g}, '
            f'cross-audience {item.theme_scores["cross_audience"]:g}, evergreen {item.theme_scores["evergreen"]:g} (out of 5)</p>'
            '</details></div></li>'
        )
    output.append('</ol>')
    output.append(
        '<p><a href="/gallery/">Browse the full Daily gallery →</a></p>'
        '<p class="ranking-coverage">Scoring anchors: 0 absent/very weak, 5 competent, '
        '7 strong, 9 exceptional, 10 exemplary. Scores are subjective editorial assessments, '
        'not site views or objective quality measurements. Original image versions are '
        'bound to the Sitemap URL and reviewed dimensions.</p>'
    )
    return "\n".join(output)+"\n", ranking
