# Trevorion Zine Daily rankings

## Status

These are **provisional AI-assisted editorial assessments**, not creator-approved final rankings or measures of post engagement.

All **669** published Dailies (including the special releases) were visually screened at thumbnail size on 12 October 2026. An 81-image shortlist was inspected using the WordPress-sized images referenced in the Sitemap. The **44** finalists in `data/daily_reviews.json` were also checked against their **actual published originals**, all 1536 × 1024 (3:2). Only these 44 have detailed scorecards. The other Dailies are unscored, not scored zero. No weak or missing image is to be assigned a fabricated rating.

## Artistic scoring — 100 points

| Criterion | Weight | Evaluate |
|---|---:|---|
| Visual impact | 20 | Immediate visual force, lighting, composition, memorability |
| Style | 15 | Consistent aesthetic language, distinctive treatment, palette and texture |
| Story | 15 | Emotion, implication, action, mystery, visual sequence or character relationships |
| Originality | 15 | Fresh concept and interpretation, avoidance of generic formula |
| Execution | 15 | Perspective, anatomy, anatomy-dependent detail, finish and technical consistency |
| Editorial value | 10 | Cultural, educational, historical, scientific, symbolic or thematic substance |
| Zine identity | 5 | Fit with Trevorion’s creative collection and distinctive authorial identity |
| Banner suitability | 5 | Readability at reduced size and visual clarity, **without cropping or editing** |

Each rating is from 0 to 10 in increments of 0.5. Anchors: 0–2 weak/absent; 3–4 below standard; 5–6 competent; 7–8 strong; 9 exceptional; 10 exemplary. Weighted artistic score = sum of (rating × weight / 10).

## Theme popularity — separate 0–5 rating

This describes the inherent audience reach of the **theme**, not the performance of the image. Rate each of `reach`, `recognition`, `cross_audience`, `evergreen` from 0–5 in half points; average them. Theme popularity is displayed next to artistic merit and used **only for an exact artistic-score tie**, never added to the artistic score. These are editorial estimates informed by the subject and Sitemap tags, not invented analytics. Do not claim actual audience views.

## Source-of-truth safeguards

1. The only metadata input to the RSS generator is Sitemap XML. The generator does not download WordPress images, use Library assets, or regenerate artwork.
2. Each review stores the Zine post URL, published original image URL, actual checked original dimensions, individual ratings, and specific rationale.
3. If a published image URL changes, its old review is automatically excluded as stale. If the original ratio is not 3:2, the image must not enter this eligible set.
4. Missing, incomplete, malformed, duplicate, or nonfinite scores abort the regeneration.
5. The **Top 20** is the top 20 **among explicitly reviewed, eligible Dailies**, not an assertion that every Daily received an individual score. Coverage and provisional status are visible on the page.
6. New Dailies remain unscored until visually assessed. Rebuilding RSS does not fabricate new scores or automatically improve old scores.

## Publishing

Edit `data/daily_reviews.json` with documented reviews and the actual published original image URL. The `Rebuild RSS from Sitemap` workflow regenerates `top20/index.md` from these reviews and the live Sitemap, updating titles, tags, links and display images automatically. The page uses `object-fit: contain` to show 3:2 artworks without cropping. The ranking remains provisional until broader archival evaluation and Trevorion’s approval.

`python scripts/rebuild_from_sitemap.py` validates both sources before writing outputs.
