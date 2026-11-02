# IBERFIT WEB · HOME HEADER/HERO CANDIDATE B · CERTIFIED REVIEW CHECKPOINT

Date: 2026-11-02
Status: USER REVIEW CANDIDATE · NOT APPROVED · NOT DEPLOYABLE
Production baseline SHA: `424700ae15c6138c8a07f15f82f5b34d62c51a9f`
Design branch: `design/web-zero-cost-master-20261102`
Final visual CSS commit: `84a238dfb542e3ba0c6ac6962c04e974264c7f11`
Final QA run: `41543534325` · SUCCESS

## Truth lock
- Production Home DOM/content is unchanged except for one candidate CSS link.
- Same navigation, H1, copy, CTAs, links, photography, canonical, hreflang and schema.
- Official IBERFIT isotipo only.
- No generated photography, copy, claims or app UI.
- Zero-cost tooling only.

## Visual decisions
- Warm cream / forest / restrained gold retained.
- Header remains warm/light.
- Photograph is preserved as real evidence, not treated as an app/product card.
- Desktop photo begins after a guaranteed content boundary.
- Horizontal desktop transition is capped at 8% of the photo and uses a low-opacity fade.
- Photograph saturation >= 0.94.
- At <=1180 px, hero genuinely recomposes vertically.
- Tablet/mobile photography becomes full bleed.
- Authentic brand integration uses the real header lockup and the real isotipo visible on the trainer's garment; artificial oversized watermark was rejected.

## Defects found and fixed during review
1. Fade originally covered 36% of the photo -> capped at 8%.
2. Copy/CTA entered the photo at desktop widths -> eliminated and gated.
3. Legacy CSS removed tablet/mobile gutters -> explicitly overridden and gated.
4. Legacy CSS narrowed stacked photo -> full-width override and gate added.
5. Mobile brand target was 32px high -> raised to >=44px.
6. Legacy 40px stacked gap remained on tablet -> removed and gate added.
7. Several CI false negatives (CSS decimal parsing / DevTools port) -> validators corrected without weakening visual thresholds.

## Certified geometry matrix
- Desktop 1440: PASS
- Desktop 1280: PASS
- Tablet 820: PASS
- Mobile 390: PASS
- Horizontal overflow: none
- Desktop content/photo overlap: none
- Tablet/mobile gutters: pass
- Tablet/mobile full-width photo: pass
- Mobile touch targets: >=44x44
- Stacked copy/photo gap: within configured maximum
- Image load: pass

## Approval gate
Do not proceed to another public screen, integration branch or PROD until the user explicitly approves this desktop direction.
