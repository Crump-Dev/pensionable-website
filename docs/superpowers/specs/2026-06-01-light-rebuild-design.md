# pensionable.ai — Light Version Design Spec
**Date:** 2026-06-01  
**Output file:** `index-light.html`  
**Status:** Approved by user

---

## Overview

A white + deep blue rebuild of the existing dark `index.html`. Same content structure and sections throughout. Intended as an alternative brand expression — the dark version remains the primary site and a reusable template. Both live side by side.

---

## Palette

| Token | Value | Usage |
|---|---|---|
| `--bg` | `#ffffff` | Page background |
| `--bg-alt` | `#f8fafc` | Alternating sections (proof strip, about) |
| `--surface` | `rgba(0,20,60,0.03)` | Card/panel backgrounds |
| `--border` | `#e2e8f0` | All borders |
| `--border-bright` | `#cbd5e1` | Hover/active borders |
| `--text` | `#1e293b` | Primary text |
| `--text-muted` | `#64748b` | Secondary text |
| `--text-caption` | `#94a3b8` | Labels, captions, mono tags |
| `--accent-start` | `#3b82f6` | Gradient start |
| `--accent-mid` | `#2563eb` | Primary accent / buttons |
| `--accent-end` | `#1d4ed8` | Gradient end |
| `--glow` | `rgba(37,99,235,0.12)` | Subtle shadow/glow on cards |
| `--navy` | `#1e293b` | Primary button fill, deep text |
| `--cta-bg` | `#eff6ff` | Challenge/CTA section background |
| `--cta-border` | `#dbeafe` | CTA section top border |

---

## Typography

No change from dark version:
- **Headings:** Plus Jakarta Sans (700, 800)
- **Body:** Inter (400, 500)
- **Mono:** JetBrains Mono (400, 500)

Same Google Fonts link. Same type scale and spacing tokens.

---

## Sections

### 1. Nav
- Background: `rgba(255,255,255,0.88)` with `backdrop-filter: blur(16px)`
- Border bottom: `#e2e8f0`
- Logo: dark (`#1e293b`)
- Nav links: `#64748b` default, `#1e293b` on hover
- Nav pill container: white bg, `#e2e8f0` border
- CTA button: `#1e293b` fill, white text (primary); `#e2e8f0` border, `#64748b` text (secondary)
- Mobile menu: white bg

### 2. Hero
- Background: white, with a very subtle blue radial gradient behind the frame (`rgba(37,99,235,0.04)`)
- **Hero visual slot:** Structure is built and ready — user will supply their own hero asset. For now: clean headline + sub-line + audit trail frame only.
- Headline gradient: `#1e293b` → `#475569` (dark to mid-slate, no white gradient)
- Accent words ("Diorama."): `#2563eb` solid or subtle gradient `#3b82f6` → `#1d4ed8`
- Hero frame: white bg panel, `#e2e8f0` border, blue box-shadow `0 0 80px rgba(37,99,235,0.1)`, same 3D tilt
- Frame titlebar: `#f8fafc` bg, `#e2e8f0` border
- Audit trail table: light theme — `#1e293b` text, `#2563eb` source links, `#f0fdf4`/`#fef9c3` for pass/warn status cells
- Badge pills: white bg, `#dbeafe` border, `#2563eb` text, blue dot

### 3. Proof Strip
- Background: `#f8fafc`, border top/bottom `#e2e8f0`
- "System live" tag: white bg, `#e2e8f0` border, green dot
- Entropy canvas: recoloured — dots and lines in `#2563eb` at low opacity, same particle logic
- Labels: `#94a3b8`

### 4. Paradigm Shift (Architectural Shift)
- Background: white
- Radial bleeds: `rgba(37,99,235,0.06)` soft blue hints
- Section titles: `#1e293b`
- Body text: `#64748b`
- Pipeline panel: `#f8fafc` bg, `#e2e8f0` border, blue left connector line
- Step icons: `#dbeafe` bg, `#2563eb` border, `#2563eb` SVG stroke
- Step labels: `#1e293b` strong, `#94a3b8` span

### 5. Radar Section
- Background: white
- Canvas bg: white (`#ffffff`)
- Ring strokes: `rgba(37,99,235,0.12)` / `0.07` / `0.04`
- Sweep: blue (`rgba(37,99,235,0.85)`)
- Trail: blue fading
- Node dots: coloured (same hex per node)
- Node pills: white bg, coloured borders — same pill HTML but light-mode colours
- Centre orb: blue gradient (`#3b82f6` → `#1d4ed8`)
- "DIORAMA" label: white

### 6. Proof Node Graph
- Background: white
- SVG nebula: `rgba(37,99,235,0.06)` radial
- Orbital rings: `rgba(37,99,235,0.10)` etc.
- Spoke gradients: from `rgba(37,99,235,0.25)` at centre → each node colour at edge
- Node dots: same colours as dark version
- Centre pill: `#1e293b` bg, `#2563eb` border, white text
- Node cards: white bg, coloured border, dark text

### 7. Trust & Safety
- Background: white
- **Terminal panel: intentionally kept dark** (`#0a0a14` bg) as a deliberate contrast element — it reads as a product artefact, not a design inconsistency
- Section title, checklist items: `#1e293b`
- Numbered labels: `#2563eb`
- "Full safety brief" link: `#2563eb`
- Trust item cards: white bg, `#e2e8f0` border

### 8. About + Globe
- Background: `#f8fafc`
- Headline: `#1e293b`
- Globe dots: `rgba(37,99,235,0.6)` (dark blue on light)
- Flanking lines: `rgba(37,99,235,0.08)`

### 9. Challenge CTA
- Background: `#eff6ff` (blue-50)
- Top border: `#dbeafe`
- Badge pill: white bg, `#bfdbfe` border, `#2563eb` text
- Headline: `#1e293b`
- CTA button: `#1e293b` fill — stands out against the blue wash

### 10. Footer
- Background: white
- Border top: `#e2e8f0`
- Logo, links, text: `#94a3b8` default, `#64748b` hover

---

## What's Intentionally Removed vs Dark Version

| Element | Decision |
|---|---|
| Black hole video + orbit rings | Removed — hero slot left clean for user's own asset |
| Aurora blobs on CTA section | Replaced by flat `#eff6ff` wash |
| Film grain / noise filters | Removed — not appropriate for light theme |
| Radial glows (purple) | Replaced by soft blue box-shadows |

---

## What Stays Identical

- All copy (headings, labels, body text)
- All HTML section structure
- All JS animation logic (canvas recoloured, not rewritten)
- Spacing tokens (Fibonacci scale)
- Type scale
- Scroll animations (fade-up, pipeline stagger, ContainerScroll)
- Spotlight card effect on feature cards
- Globe, radar, entropy canvas JS (colours changed in JS constants only)

---

## Deliverable

Single file: `index-light.html` in the project root. No new dependencies. Same CDN links (Tailwind not used, D3 for globe stays).
