# IBERFIT WEB · ZERO-COST MASTER DESIGN SYSTEM

Status: DESIGN / AUDIT ONLY  
Date: 2026-11-02  
Production baseline SHA: `424700ae15c6138c8a07f15f82f5b34d62c51a9f`  
Production URL: https://iberfit.cl  
Cost policy: **0 additional paid services**  
Deployment policy: **NO PROD without explicit screen-by-screen approval**

## 1. Objective

Elevate the real public IBERFIT website to a materially higher level in visual quality, brand expression, commercial clarity, usability, accessibility, performance and search/AI visibility, while preserving the strengths of the current site.

This is NOT a redesign into an app, dashboard or SaaS product.

The real public website is the primary reference. Any new proposal must be judged against the current live website and rejected if it does not create an obvious improvement.

## 2. Non-negotiable working rules

1. Start from the real production page, never from an invented mockup.
2. Preserve the existing information architecture unless evidence shows a real problem.
3. Preserve validated SEO content, canonical, hreflang, schema, sitemap and indexability.
4. Do not invent photography, clients, statistics, credentials, claims, locations, reviews or service features.
5. Do not invent or redraw the IBERFIT isotipo.
6. The official isotipo must feel integrated into the visual system, not pasted on top.
7. Do not convert the public website into an app UI.
8. Do not use generic SaaS cards, dashboards, glassmorphism, neon, excessive gradients or template-like UI.
9. Do not use AI-generated final website imagery unless explicitly approved for a specific decorative role.
10. Current real photography and current public assets remain the visual truth.
11. All improvements must be reversible and isolated until approved.
12. Every screen is reviewed one by one before integration.
13. Nothing reaches PROD before explicit approval.
14. All tooling must remain zero-cost beyond services already included in the current environment.

## 3. Brand direction

### Tone
- Premium, calm, human, technical, institutional.
- Editorial rather than interface-heavy.
- High confidence without aggression.
- Warm, approachable and sophisticated.

### Palette
Use the friendlier existing IBERFIT palette as the default:
- deep forest / dark green
- warm cream
- warm stone / soft neutral
- restrained gold

Avoid:
- cold blue-green cast
- neon
- harsh black/white contrast
- excessive dark surfaces that make the site feel severe
- unrelated color accents

### Typography
- Inter Variable for navigation, UI and operational copy.
- Source Serif 4 for editorial headlines where it adds authority.
- Avoid decorative typography that makes the brand theatrical.
- Improve optical hierarchy through scale, spacing, weight and line length.

### Isotipo
The official isotipo is a key brand asset and should appear with more sophistication:
- background watermark / ghost motif only when subtle
- crop or partial presence inside branded sections
- emboss / low-contrast texture
- section transition device
- subtle framing / masking device

Never:
- fake SVG/redrawn symbol
- generic initials
- repeated decorative stamping
- oversized logo that competes with content
- floating logo independent from the composition

## 4. Correct AI workflow

AI is an assistant, not the source of truth.

### Stitch
Use only for:
- component-level art direction
- alternative composition
- typography treatment
- isotipo integration concepts
- section transitions
- responsive recomposition

Do not ask Stitch to:
- redesign the whole website from scratch
- invent copy
- invent photography
- invent product features
- define SEO truth

### ChatGPT / Codex
Use for:
- implementation against real DOM/CSS
- exact diffs
- responsive CSS
- accessibility
- QA automation
- regression control
- performance work
- semantic/SEO preservation

### Penpot / Figma free
Optional visual workbench:
- tokens
- components
- layout comparison
- responsive composition
- manual final art direction

No paid plan may be required.

## 5. Zero-cost QA stack

- GitHub + GitHub Actions
- Playwright / system Chromium
- Lighthouse / Lighthouse CI
- axe-core
- Google Search Console
- Rich Results Test / Schema Validator
- Microsoft Clarity free tier if explicitly enabled
- Cloudflare Free
- Squoosh / ImageMagick / SVGO
- local image optimization
- Git diff / rollback

If a tool requires payment or credits, do not use it.

## 6. Acceptance framework

A proposed change survives only if it improves at least one of these without degrading the others:

1. visual quality
2. brand recognition
3. commercial clarity
4. content comprehension
5. mobile usability
6. accessibility
7. performance
8. SEO/indexability
9. credibility/trust
10. conversion path

Visual change alone is not enough if it creates regression elsewhere.

## 7. Visual comparison protocol

For every candidate:
- baseline = exact certified production SHA
- candidate = isolated branch
- render 390 / 820 / 1440 (and 1920 when useful)
- compare side by side
- text must remain unchanged unless an editorial task explicitly approves copy
- images must remain unchanged unless a media task explicitly approves a replacement
- no overflow
- no broken images
- no hidden SEO copy
- no navigation regression
- no touch target regression
- no contrast regression
- no Core Web Vitals regression

## 8. Page approval order

1. Home
2. Diagnóstico IRI
3. Online
4. Método
5. Presencial
6. Híbrido
7. Sobre IBERFIT
8. Contacto
9. Local pages
10. English mirror pages

Every screen is approved one by one.

## 9. Home strategy

The Home is not rebuilt. It is audited component by component.

Priority order:
1. header / navigation
2. hero
3. IBERFIT en práctica
4. Sistema IBERFIT
5. IRI report section
6. modalities
7. brand philosophy / origin
8. reviews
9. FAQ / AEO
10. final CTA
11. footer
12. privacy/consent chrome

The existing content journey remains the baseline.

## 10. Rejected directions

Explicitly rejected:
- app-like homepage
- dashboard/product marketing page
- invented UI mockups
- generated trainer/client photography
- dark-green-heavy visual direction that feels cold or clashes with the warmer current palette
- subtle changes that are visually indistinguishable from current production
- generated website imagery as the final homepage
- pasted-on isotipo treatment

These directions must not be reintroduced unless explicitly requested.

## 11. Success definition

IBERFIT should feel:
- recognizably the same company and website
- materially more premium
- more integrated
- more human
- more intentional
- more distinctive
- clearer commercially
- sharper on Retina/mobile
- easier to trust

The user should immediately perceive the upgrade without feeling that the website has become a different product.
