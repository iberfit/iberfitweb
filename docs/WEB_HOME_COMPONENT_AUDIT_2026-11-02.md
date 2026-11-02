# IBERFIT WEB · HOME COMPONENT AUDIT

Baseline: production SHA `424700ae15c6138c8a07f15f82f5b34d62c51a9f`  
Scope: Home only  
Method: component-by-component visual/commercial audit  
Status: no production changes

## Executive finding

The current Home has a strong information architecture and credible content journey. The primary opportunity is not restructuring. It is improving art direction and brand integration while preserving the existing human, editorial website character.

## Component matrix

| Component | Current value | Main weakness | Decision | Priority |
|---|---|---|---|---|
| Header/navigation | Complete, clear, bilingual | Slightly utilitarian; isotipo/wordmark can feel mechanically placed | Improve carefully | P1 |
| Hero | Strong proposition + real photography + two useful CTAs | Composition can feel standard; isotipo does not meaningfully participate in the scene | Redesign visual treatment only | P0 visual |
| IBERFIT en práctica | Strong before/during/after evidence | Visual rhythm can feel segmented; app proof competes with human photography | Improve composition | P1 |
| Sistema IBERFIT | Excellent conceptual structure | Four-stage rail can still feel functional rather than authored | Improve editorial hierarchy | P1 |
| IRI section | Strong product explanation and report evidence | Dense visual object; can feel like embedded UI | Refine, do not reinvent | P1 |
| Modalities | Clear and commercially honest | Repeated rows could gain stronger typographic identity | Light improvement | P2 |
| Brand philosophy | Strong institutional voice | Needs richer brand signature / isotipo integration | Improve | P1 |
| Reviews | Real trust evidence | Card treatment can feel conventional | Improve presentation | P2 |
| FAQ/AEO | Strong search/answer value | Visually secondary, which is correct | Preserve mostly | P3 |
| Final CTA | Clear and human | Can feel like a generic CTA panel | Improve brand finish | P2 |
| Footer | Functional and complete | Slightly dense | Refine spacing only | P3 |
| Consent | Correct controls | Mobile obstruction can be reduced without reducing choice | Improve mobile polish | P2 |

## 1. Header

### Preserve
- current navigation labels
- ES/EN switch
- CTA to IRI
- official isotipo
- compact institutional identity

### Improve
- better optical relationship between isotipo and wordmark
- more deliberate spacing
- less generic nav rhythm
- clearer active state without heavy decoration
- more coherent transition into hero

### Reject
- oversized logo
- dark header if it clashes with the warmer page
- floating/pill-heavy SaaS navigation

## 2. Hero

### Preserve
- H1: Entrenamiento personal con criterio.
- lead/support copy
- two CTAs
- real current photography
- coverage text
- website composition, not application composition

### Main opportunity
The hero should become the strongest expression of IBERFIT without replacing the current meaning.

### Best improvement axes
- better crop and image/text balance
- more deliberate relationship between hero and header
- subtle isotipo integration into background/negative space
- warmer cream/forest/gold palette
- more distinctive typography
- more graceful transition into the next section
- depth through layering and texture, not generic cards

### Isotipo concepts worth testing
1. ultra-low-opacity watermark cropped behind headline
2. partial isotipo used as a masked background texture
3. isotipo geometry used in section transition curve/rule
4. embossed/debossed mark on warm surface
5. subtle repeated micro-mark only in footer/system, never everywhere

## 3. IBERFIT en práctica

Keep human photography as the primary evidence.
The app screenshot must remain secondary proof.

Improve:
- asymmetric image rhythm
- captions integrated into image composition
- stronger before/during/after continuity
- fewer visual boundaries between the three stages

Do not:
- turn it into a dashboard
- enlarge app UI until it becomes the visual identity

## 4. Sistema IBERFIT

Keep 4 steps.
Improve:
- editorial numbering
- more generous negative space
- stronger connection between stages
- potentially one visual rule/path linking the sequence
- less card-like feel

## 5. IRI

Keep:
- real explanation
- report preview
- fictitious data disclosures
- initial assessment vs follow-up distinction

Improve:
- make report feel like a premium document, not a UI widget
- integrate official isotipo in document identity
- reduce visual density
- improve typographic hierarchy

## 6. Modalities

Keep:
- Presencial
- Híbrida
- Online
- current semantic differences

Improve:
- make rows feel like three chapters of the same service system
- stronger typography
- less box/card framing

## 7. Brand philosophy

This is the strongest place for deeper isotipo integration.

Potential:
- watermark crop
- subtle texture
- branded editorial rule
- warm paper / forest transition

Do not introduce founder-personality branding.

## 8. Reviews

Preserve real reviews and source.
Improve:
- quotation typography
- spacing
- source treatment
- reduce generic card appearance

## 9. FAQ

Preserve almost entirely.
Only refine:
- rhythm
- separators
- focus/hover states
- line length

## 10. Final CTA

Keep copy and action.
Improve:
- section transition
- brand signature
- stronger sense of conclusion
- avoid generic marketing panel

## 11. Immediate next design experiment

Do NOT redesign the whole Home.

First candidate to build:
**Hero + header only**, using the current production DOM, current text and current photograph.

The experiment must test only:
- warmer palette
- stronger premium typography
- more integrated official isotipo
- more coherent header→hero transition
- better photographic crop/edge treatment
- more distinct but friendly IBERFIT identity

Approval gate:
If the hero/header is not clearly superior side by side with production, discard it before touching any other component.
