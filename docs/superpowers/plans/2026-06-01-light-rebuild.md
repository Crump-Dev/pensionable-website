# Light Version Rebuild Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `index-light.html` — a white + deep blue version of the dark `index.html` with identical content structure and all canvas animations recoloured for a light background.

**Architecture:** Copy `index.html` to `index-light.html`, then work through the file section by section: CSS variables first, then nav, hero, each content section in order, and finally the JS canvas colour constants. Each task ends with a screenshot verification.

**Tech Stack:** Vanilla HTML/CSS/JS, D3 (globe), Google Fonts (Plus Jakarta Sans, Inter, JetBrains Mono), Playwright for screenshots, python3 http.server for local dev.

---

## File Structure

- **Create:** `index-light.html` — the entire light rebuild lives here. No other files change.

---

## Colour Reference (use throughout)

```
--bg:            #ffffff
--bg-alt:        #f8fafc
--surface:       rgba(0,20,60,0.03)
--border:        #e2e8f0
--border-bright: #cbd5e1
--text:          #1e293b
--text-muted:    #64748b
--text-caption:  #94a3b8
--accent-start:  #3b82f6
--accent-mid:    #2563eb
--accent-end:    #1d4ed8
--glow:          rgba(37,99,235,0.12)
--navy:          #1e293b
--cta-bg:        #eff6ff
--cta-border:    #dbeafe
```

---

## Task 1: Create the file and update CSS variables

**Files:**
- Create: `index-light.html`

- [ ] **Step 1: Copy dark file as starting point**

```bash
cp index.html index-light.html
```

> **Note:** Keep the local dev server (`python3 -m http.server 55612`) running throughout all tasks. Do not stop and restart it — the file is served directly so edits are reflected on refresh.

- [ ] **Step 1b: Remove film grain overlay (if present)**

Search for a `<canvas>` element with `z-index: 9999` and `pointer-events: none` used for grain noise, and its associated JS IIFE. Delete both. Also remove any `<feTurbulence>` SVG filter used for grain texture. These are dark-theme-only effects.

- [ ] **Step 2: Update `:root` CSS variables**

In `index-light.html`, replace the entire `:root { ... }` block with:

```css
:root {
  --bg:           #ffffff;
  --surface:      rgba(0,20,60,0.03);
  --surface-el:   rgba(0,20,60,0.05);
  --border:       #e2e8f0;
  --border-bright:#cbd5e1;
  --text:         #1e293b;
  --text-muted:   #64748b;
  --text-caption: #94a3b8;
  --accent:       linear-gradient(90.01deg, #3b82f6 0%, #2563eb 50%, #1d4ed8 100%);
  --accent-start: #3b82f6;
  --accent-mid:   #2563eb;
  --accent-end:   #1d4ed8;
  --glow:         rgba(37,99,235,0.12);
  --glow-deep:    rgba(37,99,235,0.06);
  --purple:       #2563eb;
  --r-btn:        8px;
  --r-card:       12px;
  --r-panel:      16px;
  --r-pill:       999px;
  --font-head:    'Plus Jakarta Sans', sans-serif;
  --font-body:    'Inter', sans-serif;
  --font-mono:    'JetBrains Mono', monospace;
  /* spacing and type scale tokens unchanged */
  --f1:  0.25rem; --f2:  0.5rem;  --f3:  0.75rem; --f5:  1.25rem;
  --f8:  2rem;    --f13: 3.25rem; --f21: 5.25rem;  --f34: 8.5rem; --f55: 13.75rem;
  --t-xs: 0.618rem; --t-sm: 0.764rem; --t-base: 1rem; --t-md: 1.25rem;
  --t-lg: 1.618rem; --t-xl: 2.618rem; --t-2xl: 4.236rem;
}
```

- [ ] **Step 3: Update `body` background**

```css
body {
  background: var(--bg);
  color: var(--text);
  /* rest unchanged */
}
```

- [ ] **Step 4: Update scrollbar colours**

```css
::-webkit-scrollbar-thumb { background: rgba(0,20,60,0.08); }
::-webkit-scrollbar-thumb:hover { background: rgba(0,20,60,0.14); }
```

- [ ] **Step 5: Verify page loads without JS errors**

```bash
# Start server if not running
python3 -m http.server 55612 &>/dev/null &
npx playwright screenshot "http://localhost:55612/index-light.html" screenshots/tmp-light-t1.png --viewport-size="1440,900" --wait-for-timeout=1500
```

Expected: white background visible, text likely unreadable in places — that's fine, we fix section by section.

- [ ] **Step 6: Commit**

```bash
git add index-light.html
git commit -m "feat: init index-light.html with updated CSS variables"
```

---

## Task 2: Nav, buttons, and global utility classes

**Files:**
- Modify: `index-light.html` — nav and button CSS

- [ ] **Step 1: Update nav CSS**

Replace the `nav` block:
```css
nav {
  background: rgba(255,255,255,0.88);
  border-bottom: 1px solid var(--border);
  /* backdrop-filter, position, height unchanged */
}
nav::after {
  background: radial-gradient(ellipse at center, rgba(37,99,235,0.15) 0%, transparent 70%);
}
.nav-links {
  background: rgba(0,20,60,0.03);
  border: 1px solid var(--border);
}
.nav-links a { color: var(--text-muted); }
.nav-links a:hover { color: var(--text); background: rgba(0,20,60,0.04); }
```

- [ ] **Step 2: Update button styles**

```css
.btn-primary {
  background: #1e293b;
  border: 1px solid #1e293b;
  color: #ffffff;
  box-shadow: 0 1px 3px rgba(0,20,60,0.15);
}
.btn-primary:hover {
  background: #0f172a;
  border-color: #0f172a;
  box-shadow: 0 4px 12px rgba(0,20,60,0.2);
}
.btn-secondary {
  border: 1px solid var(--border-bright);
  color: var(--text-muted);
}
.btn-secondary:hover { color: var(--text); border-color: #94a3b8; }
```

- [ ] **Step 3: Update mobile menu**

```css
.mobile-menu {
  background: rgba(255,255,255,0.97);
  border-bottom: 1px solid var(--border);
}
.mobile-menu a { color: var(--text-muted); border-bottom: 1px solid var(--border); }
.mobile-menu a:hover { color: var(--text); }
```

- [ ] **Step 4: Update gradient text utility**

```css
.grad-text {
  background: var(--accent);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
```

- [ ] **Step 5: Update badge pill**

```css
.badge-pill {
  background: rgba(37,99,235,0.06);
  border: 1px solid rgba(37,99,235,0.2);
  color: var(--accent-mid);
}
.badge-pill .dot { background: var(--accent-mid); box-shadow: 0 0 6px var(--accent-mid); }
```

- [ ] **Step 6: Update section-header title gradient**

```css
.section-title {
  background: linear-gradient(180deg, #1e293b 0%, #475569 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.section-desc { color: var(--text-muted); }
```

- [ ] **Step 7: Update radial bleeds**

```css
.rb-hero {
  background: radial-gradient(ellipse at center,
    rgba(37,99,235,0.07) 0%, rgba(37,99,235,0.03) 35%,
    rgba(37,99,235,0.01) 60%, transparent 72%);
}
.rb-hero-inner {
  background: radial-gradient(ellipse at center,
    rgba(37,99,235,0.08) 0%, rgba(37,99,235,0.03) 50%, transparent 70%);
}
.rb-center, .rb-left, .rb-right {
  background: radial-gradient(ellipse at center, rgba(37,99,235,0.05) 0%, transparent 70%);
}
```

- [ ] **Step 8: Screenshot nav area**

```bash
npx playwright screenshot "http://localhost:55612/index-light.html" screenshots/tmp-light-nav.png --viewport-size="1440,900" --wait-for-timeout=1500
```

Expected: white nav, dark text links, navy CTA button visible.

- [ ] **Step 9: Commit**

```bash
git add index-light.html
git commit -m "feat: light nav, buttons, badge pills, section headers"
```

---

## Task 3: Hero section

**Files:**
- Modify: `index-light.html` — hero CSS and HTML

- [ ] **Step 1: Remove black hole video HTML**

Delete the entire `<!-- Black hole background -->` div block (the `.black-hole-wrap` element and everything inside it).

- [ ] **Step 2: Remove black hole CSS**

Delete all CSS rules for: `.black-hole-wrap`, `.black-hole-video-layer`, `.bh-rings`, `.bh-ring-group`, `.bh-ring`, `.bh-dot`, `.bh-stars`, `.bh-star`, `@keyframes bhRingRotate`, `@keyframes bhStarsRotate`, `@keyframes bhStarTwinkle`, `.bh-stars-visible`.

- [ ] **Step 3: Remove black hole JS**

Delete the `// Black hole — ping-pong video + star field` IIFE block entirely.

- [ ] **Step 4: Update hero headline gradient**

```css
.hero-headline .line {
  background: linear-gradient(180deg, #1e293b 0%, #475569 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.hero-headline .line-accent {
  background: var(--accent);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.hero-sub { color: #64748b; }
.hero-desc { color: var(--text-muted); }
```

- [ ] **Step 5: Update hero frame (audit trail)**

```css
.hero-frame {
  background: #ffffff;
  border: 1px solid var(--border);
  box-shadow:
    0 0 #0000,
    0 9px 20px rgba(0,20,60,0.06),
    0 37px 37px rgba(0,20,60,0.04),
    0 84px 50px rgba(0,20,60,0.02),
    0 0 80px rgba(37,99,235,0.08),
    inset 0 1px 0 rgba(255,255,255,0.8);
}
.frame-titlebar {
  background: #f8fafc;
  border-bottom: 1px solid var(--border);
}
.frame-title { color: var(--text-caption); }
```

- [ ] **Step 6: Update audit trail table colours**

```css
.audit-title { color: var(--text-caption); }
.audit-badge { color: #16a34a; background: rgba(22,163,74,0.06); border: 1px solid rgba(22,163,74,0.2); }
.audit-row:hover { background: rgba(0,20,60,0.02); }
.audit-row + .audit-row { border-top: 1px solid #f1f5f9; }
.audit-row.header { color: var(--text-caption); border-bottom: 1px solid var(--border); }
.audit-calc { color: var(--text); }
.audit-value { color: var(--text-muted); }
.audit-source { color: var(--accent-mid); }
.audit-source:hover { color: var(--accent-end); }
.audit-status.pass { color: #16a34a; background: rgba(22,163,74,0.06); border: 1px solid rgba(22,163,74,0.15); }
.audit-status.warn { color: #d97706; background: rgba(217,119,6,0.06); border: 1px solid rgba(217,119,6,0.15); }
```

- [ ] **Step 7: Update hero section background**

Add a subtle blue radial hint behind the frame in the hero CSS:
```css
#hero {
  background: radial-gradient(ellipse 80% 60% at 50% 100%, rgba(37,99,235,0.05) 0%, transparent 70%);
}
```

- [ ] **Step 8: Screenshot hero**

```bash
npx playwright screenshot "http://localhost:55612/index-light.html" screenshots/tmp-light-hero.png --viewport-size="1440,900" --wait-for-timeout=1500
```

Expected: clean white hero, dark headline, blue "Diorama." accent, audit trail frame with light styling.

- [ ] **Step 9: Commit**

```bash
git add index-light.html
git commit -m "feat: light hero — remove video, update frame and headline colours"
```

---

## Task 4: Proof strip and Paradigm Shift section

**Files:**
- Modify: `index-light.html`

- [ ] **Step 1: Update proof strip**

```css
#proof {
  background: #f8fafc;
  border-top: 1px solid var(--border);
  border-bottom: 1px solid var(--border);
}
.proof-lead strong { color: var(--text); }
.proof-tag {
  background: #ffffff;
  border: 1px solid var(--border);
  color: var(--text-caption);
}
.proof-tag::before { background: #16a34a; box-shadow: 0 0 6px #16a34a; }
.entropy-labels { color: var(--text-caption); }
```

- [ ] **Step 2: Update entropy canvas JS colour constant**

Find the line in the entropy animation JS:
```js
const COLOR = '#ba9cff';
```
Change to:
```js
const COLOR = '#2563eb';
```

- [ ] **Step 3: Update paradigm section background**

```css
#paradigm { background: #ffffff; }
```

- [ ] **Step 4: Update paradigm/pipeline styles**

```css
.col-text p { color: var(--text-muted); }
.learn-more { color: var(--accent-mid); }
.pipeline {
  background: #f8fafc;
  border: 1px solid var(--border);
  box-shadow: 0 0 40px rgba(37,99,235,0.04);
}
.pipeline-connector {
  background: linear-gradient(to bottom, transparent, rgba(37,99,235,0.2) 20%, rgba(37,99,235,0.2) 80%, transparent);
}
.step-icon {
  background: rgba(37,99,235,0.06);
  border: 1px solid rgba(37,99,235,0.15);
}
.step-label strong { color: var(--text); }
.step-label span { color: var(--text-caption); }
.step-arrow { color: var(--accent-mid); }
```

- [ ] **Step 4: Screenshot these sections**

```bash
npx playwright screenshot "http://localhost:55612/index-light.html#proof" screenshots/tmp-light-proof.png --viewport-size="1440,900" --wait-for-timeout=2000
```

- [ ] **Step 5: Commit**

```bash
git add index-light.html
git commit -m "feat: light proof strip and paradigm section"
```

---

## Task 5: Radar section

**Files:**
- Modify: `index-light.html` — radar canvas JS colour constants

- [ ] **Step 1: Update radar canvas background fill**

In the radar JS, find:
```js
bx.fillStyle = '#030014';
bx.fillRect(0, 0, W, H);
```
Change to:
```js
bx.fillStyle = '#ffffff';
bx.fillRect(0, 0, W, H);
```

- [ ] **Step 2: Update ring stroke colours**

Find the rings array draw loop. Change the stroke colours:
```js
bx.strokeStyle = `rgba(37,99,235,${[0.18,0.09,0.04,0.02][ri]})`;
```

- [ ] **Step 3: Update spoke stroke colour**

```js
bx.strokeStyle = 'rgba(37,99,235,0.07)';
```

- [ ] **Step 4: Update baseline stroke**

```js
bx.strokeStyle = 'rgba(37,99,235,0.18)';
```

- [ ] **Step 5: Update vignette gradient to fade to white**

```js
const vigGrad = bx.createRadialGradient(ox, oy, maxR * 0.30, ox, oy, maxR * 1.08);
vigGrad.addColorStop(0,    'rgba(255,255,255,0)');
vigGrad.addColorStop(0.55, 'rgba(255,255,255,0)');
vigGrad.addColorStop(1,    'rgba(255,255,255,0.92)');
```

- [ ] **Step 6: Update centre orb gradient**

```js
const orbGrad = bx.createRadialGradient(ox, cy, 0, ox, oy, ORB_R);
orbGrad.addColorStop(0,    'rgba(147,197,253,1)');
orbGrad.addColorStop(0.38, 'rgba(37,99,235,0.96)');
orbGrad.addColorStop(0.75, 'rgba(29,78,216,0.70)');
orbGrad.addColorStop(1,    'rgba(15,23,42,0)');
```

- [ ] **Step 7: Update orb border and text colours**

```js
bx.strokeStyle = 'rgba(37,99,235,0.6)';  // orb ring
bx.fillStyle = 'rgba(255,255,255,0.95)'; // DIORAMA text
```

- [ ] **Step 8: Update sweep needle and trail colours**

Locate the trail drawing loop (iterates `TRAIL_STEPS` times). Every colour literal in this loop that references purple (e.g. `rgba(147,130,255,...)`) must be changed to blue. Then update the needle itself:

```js
// Inside trail loop — change every instance of rgba(147,130,255,...) to:
ctx.strokeStyle = `rgba(37,99,235,${alpha.toFixed(3)})`;

// Bright needle line:
ctx.strokeStyle = 'rgba(29,78,216,0.92)';

// Tip dot outer halo:
ctx.fillStyle = 'rgba(37,99,235,0.15)';

// Tip dot centre:
ctx.fillStyle = 'rgba(59,130,246,1)';
```

- [ ] **Step 9: Update tip dot colours**

```js
ctx.fillStyle = 'rgba(37,99,235,0.15)'; // outer halo
ctx.fillStyle = 'rgba(59,130,246,1)';    // bright dot
```

- [ ] **Step 10: Update rnode-pill and rnode-sub for light bg**

```css
.rnode-pill {
  backdrop-filter: blur(8px);
  background: rgba(255,255,255,0.85);
}
.rnode-sub { color: rgba(37,99,235,0.4); }
.rnode.lit .rnode-sub { color: var(--nf); opacity: 0.8; }
```

- [ ] **Step 11: Screenshot radar**

```bash
npx playwright screenshot "http://localhost:55612/index-light.html#radar-section" screenshots/tmp-light-radar.png --viewport-size="1440,900" --wait-for-timeout=3000
```

- [ ] **Step 12: Commit**

```bash
git add index-light.html
git commit -m "feat: recolour radar canvas for light background"
```

---

## Task 6: Proof node graph

**Files:**
- Modify: `index-light.html` — ng-wrap SVG and CSS

- [ ] **Step 1: Update ng-center-pill**

```css
.ng-center-pill {
  background: #1e293b;
  border: 1px solid #1e293b;
  color: #ffffff;
  box-shadow: 0 0 24px rgba(30,41,59,0.2), 0 0 60px rgba(30,41,59,0.08);
}
```

- [ ] **Step 2: Update ng-node-card**

```css
.ng-node-card {
  background: rgba(255,255,255,0.9);
  color: var(--nf);
  border: 1px solid var(--nc);
  box-shadow: 0 0 16px var(--ns), 0 2px 8px rgba(0,20,60,0.06);
}
```

- [ ] **Step 3: Update SVG nebula radial gradient**

In the SVG `<defs>`, replace `ng-nebula`:
```html
<radialGradient id="ng-nebula" cx="460" cy="280" r="240" gradientUnits="userSpaceOnUse">
  <stop offset="0%"   stop-color="#dbeafe" stop-opacity="0.7"/>
  <stop offset="45%"  stop-color="#eff6ff" stop-opacity="0.3"/>
  <stop offset="100%" stop-color="#ffffff" stop-opacity="0"/>
</radialGradient>
```

- [ ] **Step 4: Update SVG centre orb gradient**

```html
<radialGradient id="ng-orb" cx="460" cy="268" r="44" gradientUnits="userSpaceOnUse">
  <stop offset="0%"   stop-color="#93c5fd"/>
  <stop offset="42%"  stop-color="#2563eb"/>
  <stop offset="100%" stop-color="#1d4ed8" stop-opacity="0.8"/>
</radialGradient>
```

- [ ] **Step 5: Update SVG spoke gradients**

For each `ng-lg0` through `ng-lg5`, change the first stop from `#9382ff` to `#3b82f6`:
```html
<stop offset="0%" stop-color="#3b82f6" stop-opacity="0.3"/>
```
(Keep each line's second stop colour — the node colours — unchanged.)

- [ ] **Step 6: Update orbital ring strokes in SVG**

```html
<circle cx="460" cy="280" r="96"  stroke="rgba(37,99,235,0.12)" .../>
<circle cx="460" cy="280" r="155" stroke="rgba(37,99,235,0.07)" .../>
<circle cx="460" cy="280" r="215" stroke="rgba(37,99,235,0.04)" .../>
```

- [ ] **Step 7: Screenshot node graph**

```bash
npx playwright screenshot "http://localhost:55612/index-light.html#halcyon" screenshots/tmp-light-ng.png --viewport-size="1440,900" --wait-for-timeout=2000
```

- [ ] **Step 8: Commit**

```bash
git add index-light.html
git commit -m "feat: recolour proof node graph for light background"
```

---

## Task 7: Trust & Safety section

**Files:**
- Modify: `index-light.html`

- [ ] **Step 1: Update trust section styles**

```css
#trust { background: #ffffff; }
.trust-num { color: var(--accent-mid); }
.trust-item {
  border: 1px solid var(--border);
  background: #ffffff;
}
.trust-item:hover { border-color: var(--border-bright); }
.trust-item-body strong { color: var(--text); }
.trust-item-body p { color: var(--text-muted); }
```

- [ ] **Step 2: Keep terminal intentionally dark**

The `.terminal` CSS block stays unchanged — `background: #0a0a14` — this is intentional per the spec as a product artefact contrast element.

- [ ] **Step 3: Update "Full safety brief" link colour**

The `.learn-more` CSS already uses `var(--accent-mid)` which is now blue. No change needed — verify it resolves correctly.

- [ ] **Step 4: Screenshot trust section**

```bash
npx playwright screenshot "http://localhost:55612/index-light.html#trust" screenshots/tmp-light-trust.png --viewport-size="1440,900" --wait-for-timeout=1500
```

Expected: white cards with numbered blue labels, dark terminal panel on the left as intentional contrast.

- [ ] **Step 5: Commit**

```bash
git add index-light.html
git commit -m "feat: light trust section — keep terminal dark intentionally"
```

---

## Task 8: About section and globe

**Files:**
- Modify: `index-light.html`

- [ ] **Step 1: Update about section styles**

```css
#about { background: #f8fafc; }
.about-headline {
  background: linear-gradient(180deg, #1e293b 0%, #475569 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.about-sub { color: var(--text-muted); }
.about-lines::before {
  background: linear-gradient(to bottom, transparent, rgba(37,99,235,0.1));
}
.about-lines::after {
  background: linear-gradient(to top, transparent, rgba(37,99,235,0.1));
}
```

- [ ] **Step 2: Update globe dot colour in JS**

Find in the globe canvas draw function:
```js
ctx.fillStyle = 'rgba(186,156,255,0.75)';
```
Change to:
```js
ctx.fillStyle = 'rgba(37,99,235,0.6)';
```

- [ ] **Step 3: Screenshot about section**

```bash
npx playwright screenshot "http://localhost:55612/index-light.html#about" screenshots/tmp-light-about.png --viewport-size="1440,900" --wait-for-timeout=3000
```

- [ ] **Step 4: Commit**

```bash
git add index-light.html
git commit -m "feat: light about section and globe recolour"
```

---

## Task 9: Challenge CTA and footer

**Files:**
- Modify: `index-light.html`

- [ ] **Step 1: Replace aurora CTA with light blue wash**

Remove all aurora CSS rules: `.aurora-bg`, `.aurora-pulse`, `.aurora-blob`, `.aurora-blob-1/2/3`, `.aurora-stars`, `.aurora-star`, `@keyframes blob1/2/3`, `@keyframes aurora-pulse`, `@keyframes twinkle`.

- [ ] **Step 2: Remove aurora HTML**

Delete the `<div class="aurora-bg" aria-hidden="true">...</div>` block inside `#challenge`.

- [ ] **Step 3: Remove aurora JS**

Delete the `// Aurora stars` IIFE block.

- [ ] **Step 4: Add light CTA styles**

```css
#challenge {
  background: #eff6ff;
  border-top: 1px solid #dbeafe;
}
.challenge-headline {
  background: linear-gradient(180deg, #1e293b 0%, #334155 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.challenge-body { color: var(--text-muted); }
```

- [ ] **Step 5: Verify and fix `.btn-nav-primary`**

Check whether `.btn-nav-primary` has its own colour rules in the CSS (separate from `.btn-primary`). If so, explicitly add:
```css
.btn-nav-primary {
  background: #1e293b;
  border: 1px solid #1e293b;
  color: #ffffff;
}
.btn-nav-primary:hover { background: #0f172a; }
```

- [ ] **Step 6: Update footer**

```css
footer {
  background: #ffffff;
  border-top: 1px solid var(--border);
}
.footer-logo { color: var(--text); }
.footer-links a { color: var(--text-caption); }
.footer-links a:hover { color: var(--text-muted); }
.footer-right { color: var(--text-caption); }
.live-dot { background: #16a34a; box-shadow: 0 0 6px #16a34a; }
```

- [ ] **Step 7: Screenshot CTA + footer**

```bash
npx playwright screenshot "http://localhost:55612/index-light.html#challenge" screenshots/tmp-light-cta.png --viewport-size="1440,900" --wait-for-timeout=1500
```

- [ ] **Step 8: Commit**

```bash
git add index-light.html
git commit -m "feat: light CTA section (blue wash) and footer"
```

---

## Task 10: Halcyon proof section header and full-page review

**Files:**
- Modify: `index-light.html`

- [ ] **Step 1: Update halcyon panel (if present) and proof cards**

First check: does `.halcyon-panel` exist in the HTML? The dark site replaced Halcyon stats with a proof grid in a recent commit, so it may be absent. If absent, skip to Step 2 (proof cards). If present, update:
```css
.halcyon-panel {
  background: #f8fafc;
  border: 1px solid var(--border);
  box-shadow: 0 0 80px rgba(37,99,235,0.06);
}
.halcyon-quote { color: var(--text); }
.halcyon-quote::before { color: rgba(37,99,235,0.15); }
.halcyon-source { color: var(--text-caption); }
.stat-num {
  background: var(--accent);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.stat-label { color: var(--text-muted); }
```

- [ ] **Step 2: Update proof-card styles**

```css
.proof-card {
  background: #ffffff;
  border: 1px solid var(--border);
}
.proof-card::before {
  background: linear-gradient(90deg, transparent, rgba(37,99,235,0.15), transparent);
}
.proof-card:hover {
  border-color: rgba(37,99,235,0.2);
  box-shadow: 0 8px 32px rgba(37,99,235,0.08);
}
.proof-card-type { color: var(--accent-mid); }
```

- [ ] **Step 3: Update scroll animations for light**

```css
.fade-up {
  opacity: 0;
  transform: translateY(24px);
  /* transition unchanged */
}
```
No change needed — class is already colour-neutral.

- [ ] **Step 4: Take full-page screenshot**

```bash
npx playwright screenshot "http://localhost:55612/index-light.html" screenshots/tmp-light-full.png --viewport-size="1440,900" --full-page --wait-for-timeout=3000
```

Review the full page. Check: no white-on-white text, no purple artefacts, all sections readable.

- [ ] **Step 5: Update page `<title>` and meta description**

Change `<title>` to same value — no change needed.
Confirm `og:image` still points to `/og-image.png` — update later when a light og-image is ready.

- [ ] **Step 6: Final commit**

```bash
git add index-light.html
git commit -m "feat: complete light rebuild — index-light.html"
```

---

## Task 11: Spot-check and fix-up pass

**Files:**
- Modify: `index-light.html` — any remaining issues found in review

- [ ] **Step 1: Screenshot every section in sequence**

```bash
for anchor in "" "#proof" "#paradigm" "#radar-section" "#halcyon" "#trust" "#about" "#challenge"; do
  label=$(echo $anchor | tr -d '#' | tr '/' '-')
  label=${label:-home}
  npx playwright screenshot "http://localhost:55612/index-light.html${anchor}" \
    screenshots/tmp-light-check-${label}.png --viewport-size="1440,900" --wait-for-timeout=2000
done
```

- [ ] **Step 2: Review each screenshot**

Read each screenshot with the Read tool. Look for:
- Any remaining dark backgrounds where white is expected
- White text on white background (invisible)
- Purple colours that should have been changed to blue
- Any hardcoded hex colours in CSS that weren't caught by the variable change

- [ ] **Step 3: Fix any issues found**

Apply targeted CSS fixes. Commit each meaningful fix.

- [ ] **Step 4: Mobile check**

```bash
npx playwright screenshot "http://localhost:55612/index-light.html" screenshots/tmp-light-mobile.png --viewport-size="390,844" --full-page --wait-for-timeout=2000
```

Check: no horizontal scroll, touch targets readable, text not too small.

- [ ] **Step 5: Final commit**

```bash
git add index-light.html
git commit -m "fix: light rebuild spot-check and cleanup"
```
