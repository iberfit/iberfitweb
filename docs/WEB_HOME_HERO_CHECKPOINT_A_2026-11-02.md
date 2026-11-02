# IBERFIT WEB · HOME HEADER/HERO CHECKPOINT A

Date: 2026-11-02
Status: CANDIDATE FOR USER REVIEW · NOT APPROVED · NOT DEPLOYABLE
Production baseline SHA: `424700ae15c6138c8a07f15f82f5b34d62c51a9f`
Design branch: `design/web-zero-cost-master-20261102`

## What is locked

- exact production Home copy
- exact production navigation
- exact production links
- exact production photography
- official IBERFIT isotipo
- canonical/schema/hreflang untouched
- no app/dashboard treatment
- no generated photography
- no invented claims
- no paid tooling

## Candidate direction

Header + hero only.

Key decisions:
- warm current IBERFIT cream/forest/gold palette preserved
- header remains light and friendly
- isotipo + wordmark treated as a more deliberate lockup
- hero uses one continuous editorial canvas rather than a text block beside a floating photo card
- the current real photograph blends gradually into the cream content field
- the real brand mark visible in the training photograph participates naturally in the composition
- no artificial oversized isotipo overlay
- CTA hierarchy preserved
- mobile returns to stacked content with the same real photo

## Internal iterations rejected

- dark app-like / product-marketing Home
- generated-image homepage concepts
- overly dark green hero
- barely distinguishable CSS-only V2
- large artificial isotipo watermark
- card-like photograph treatment

## QA

- exact production DOM/content preserved except one candidate CSS link
- bilingual architecture QA: SUCCESS
- system Chrome render: SUCCESS
- desktop 1440 DPR2: SUCCESS
- tablet 820 DPR2: SUCCESS
- mobile 390 DPR3: SUCCESS
- clean review render uses a non-deployable `__review__` page only to hide consent chrome for visual review

## Approval gate

Do not touch another public page or production based on this direction until this screen is reviewed.
If rejected, retain the master method but discard the visual candidate.
