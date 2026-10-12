# Trevorion Zine RSS

**https://rss.trevorion.io/**

This repository republishes the Trevorion Zine's published work as a weekly RSS digest, monthly Daily archives, and an image gallery.

## Canonical source

All post metadata comes **exclusively from** the public [Trevorion Sitemap](https://sitemap.trevorion.io/index.xml), maintained in [PhantomBlackOP/Sitemap](https://github.com/PhantomBlackOP/Sitemap).

- The Sitemap handles WordPress retrieval, anti-bot clearance, post titles, publication dates, tags and image extraction.
- Per-post Sitemap XML carries `meta:og_image`, standard `image:image/image:loc` (original media) and `meta:thumbnail_image` (WordPress-sized alternative where available). RSS uses the latter for artwork mosaics and retains original image links.
- The RSS repository **never calls WordPress or X**. It fetches only Sitemap XML.
- Published gallery thumbnails link to the canonical **Zine posts**, not to a suspended X account.

## Published outputs

- [Weekly RSS](https://rss.trevorion.io/feed.xml), latest 20 weekly digests
- [Full RSS](https://rss.trevorion.io/full-feed.xml), complete weekly history
- [Weekly archive](https://rss.trevorion.io/archive/)
- [Monthly Daily digests](https://rss.trevorion.io/monthly/)
- [Daily gallery and thumbnail mosaics](https://rss.trevorion.io/gallery/)
- [Top 20 Dailies](https://rss.trevorion.io/top20/), based on a **complete 669-artwork first-pass assessment**, using 100-point artistic scoring and separately displayed subject-theme appeal
- [Full rankings](https://rss.trevorion.io/top20/all/), all scored Dailies with no preliminary shortlist exclusion
- [Public scoring methodology](https://rss.trevorion.io/top20/methodology/) (HTML) and [all individual scores](https://rss.trevorion.io/top20/scores.xml) (XML)

Generated source files live in `_posts/`, `monthly/`, `gallery/`, plus `index.md`, `archive.md`, `monthly_index.md`, and `top20/index.md` and `top20/all.md`. The 669 original four-category preview assessments are recorded in `data/daily_visual_reviews.json`. Full computed scorecards are regenerated in `data/daily_reviews.json` using [the public HTML methodology](https://rss.trevorion.io/top20/methodology/). All 669 initial published Dailies and specials were assessed; scores remain provisional and creator review is pending. Original X-derived content was replaced from the Zine's canonical post inventory; Git history retains the previous versions.

## Scheduled rebuilding

`.github/workflows/rebuild-rss.yml` executes at **06:00 UTC daily**, after the Sitemap's **03:00 UTC** update. Manual workflow dispatch is also available.

The build performs full validation of all referenced Sitemap monthly XML and audited ranking records before it writes anything. It **requires image metadata for every indexed Daily** and fails closed if a feed is missing, corrupt, inaccessible or incomplete. Rebuilt files are only changed when their content changes.

```bash
python scripts/rebuild_from_sitemap.py --check  # validate, no writes
python scripts/rebuild_from_sitemap.py          # regenerate and clean old archives
```

No Twitter/X credentials or WordPress credentials are needed.

## Credits

Created and curated by **Trevor Grech (@Trevorion)**.
