# Daily artwork scoring — complete archive

## Coverage and editorial status (12 October 2026)

**669/669 published Daily artworks** were individually examined in the original Sitemap order: the 000–649 numbered sequence and the remaining unnumbered specials. No artistic or popularity shortlisting occurred before the first pass. Every artwork received a first-pass visual-impact, style, story, and originality score. After the full first pass, higher-ranked images received a second visual calibration. The resulting 669 reviews are individually bound to the canonical published image URL in `data/daily_visual_reviews.json`.

**Limitations:** Most of this full-archive assessment was performed using the **published Sitemap artwork mosaic previews (225×150)**. An 81-image subset was inspected at medium resolution, and 44 original published files had full-resolution verification in an earlier audit. Therefore the first-pass visual scores are preliminary, especially for fine anatomy, perspective, and execution. **Do not claim 669 full-resolution originals were reviewed.** Creator approval is pending.

The full archive is **eligible** for Top 20 ranking, including 4:3 older images. The independent 3:2-only restriction is for the YouTube banner, not this ranking.

## Weights and scoring

| Dimension | Weight | Basis |
|---|---:|---|
| Visual impact | 20 | Individually assessed from each published artwork: composition, impact, atmosphere and legibility |
| Style | 15 | Individually assessed: treatment, colour, style coherence and distinction |
| Story | 15 | Individually assessed: depicted action, emotion, narrative or suggested world |
| Originality | 15 | Individually assessed: subject interpretation and visual inventiveness |
| Execution | 15 | **Estimated** from the first two visually assessed ratings (their mean), not independent full-resolution technical inspection |
| Editorial value | 10 | **Estimated** using story/originality and topic classifications derived from the Sitemap title/tags |
| Zine identity | 5 | **Estimated** using style/originality/story, with an explicit author-identity signal in Sitemap metadata |
| Banner suitability | 5 | **Estimated** using visual impact/style/story. The Top 20 does not exclude any aspect ratio |
| **Total** | **100** |  |

First four criteria are recorded explicitly, 1–10 including exceptional 10s, in `data/daily_visual_reviews.json`. The calculated four criteria are transparently produced in `scripts/rank_dailies.py` on **exactly the same formula for every Daily** and rounded to the nearest half point. These derived scores are *proxies*, not claims of an additional independent human review. The top 20 and complete score ledger are recomputed from the current Sitemap metadata at each RSS rebuild.

## Subject-theme appeal (separate)

Theme appeal is **not a post's popularity or an image's engagement**. It is an explicitly estimated general-audience-interest profile for the subject, derived from the Sitemap title and tags. Four 0–5 components describe estimated audience reach, cultural recognition, cross-audience appeal and evergreen value. Their mean is displayed as `theme_appeal`, **not added** to artistic merit, and used **only to break artistic-score ties**.

Classifiers are defined and auditable in `scripts/rank_dailies.py`. They are editorial heuristics, not external trend/search analytics. Actual popularity should not be claimed without independent evidence.

## Identity, validation and regeneration

- WordPress handles publication; Sitemap contains **the authoritative published original image URL**. RSS reads only Sitemap XML. Library images, unapproved variants and AI regeneration are not sources.
- Reviews use canonical post **URL and exact published original image URL** as identifiers. A changed original image URL invalidates an old review rather than silently transferring it to new artwork.
- Missing future Dailies are marked unscored until explicitly evaluated. RSS continues serving the existing reviews and openly displays `scored / published` coverage.
- A duplicate, malformed, or nonnumeric source review aborts regeneration. The input archive must contain all 669 initial reviews; no score defaults or fillers are manufactured for absent records.
- `data/daily_reviews.json` is the **generated full record** (scores, tags, image, reasoning and provenance). `top20/all.md` presents the entire scored catalogue by rank.
- Top 20 gallery tiles use `object-fit:contain` so artwork is never cropped.
- The YouTube banner requires a **separate** selection stage with published originals and 3:2 images only.

### Next quality pass

Full-resolution inspection and substantive individual critiques for all 669 would improve this preliminary numerical catalogue. Until then, the page must remain labelled **AI-assisted first-pass assessment**. The numeric ranks should never be presented as objectively definitive or already endorsed by the creator.
