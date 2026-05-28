#!/usr/bin/env python3
"""
generate_intelligence.py
========================
Fetches live UK pension data from four sources, generates HTML article pages
in /intelligence/, and prepends new cards to intelligence/index.html.

Sources
-------
  TPR   — The Pensions Regulator RSS feed (press releases)
  PPF   — Pension Protection Fund 7800 Index (scraped monthly release page)
  ONS   — Consumer Prices Index including OOH (CPIH) via ONS API
  BoE   — Bank of England Bank Rate via BoE IADB API

Usage
-----
  python tools/generate_intelligence.py          # run from repo root
  python tools/generate_intelligence.py --dry-run  # generate but don't push

Environment variables (required for auto-push)
-----------------------------------------------
  GIT_USER_EMAIL   email for the commit author
  GIT_USER_NAME    name for the commit author
"""

import os, re, sys, json, hashlib, subprocess, traceback, ssl
import urllib.request, urllib.error
from datetime import datetime, timezone

# Allow unverified SSL when certs aren't installed locally (CI uses verified certs)
_SSL_CTX = ssl.create_default_context()
try:
    import certifi
    _SSL_CTX = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    _SSL_CTX.check_hostname = False
    _SSL_CTX.verify_mode = ssl.CERT_NONE
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────────────
ROOT       = Path(__file__).resolve().parent.parent
INTEL_DIR  = ROOT / "intelligence"
MANIFEST   = INTEL_DIR / "manifest.json"
INDEX_HTML = INTEL_DIR / "index.html"

DRY_RUN = "--dry-run" in sys.argv

# ── Manifest (tracks slugs already generated) ────────────────────────────────
def load_manifest():
    if MANIFEST.exists():
        return json.loads(MANIFEST.read_text())
    return {"generated": []}

def save_manifest(m):
    MANIFEST.write_text(json.dumps(m, indent=2))

# ── HTTP helper ───────────────────────────────────────────────────────────────
def fetch(url, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent": "pensionable-intelligence/1.0"})
    with urllib.request.urlopen(req, timeout=timeout, context=_SSL_CTX) as r:
        return r.read().decode("utf-8", errors="replace")

# ── Slug generation ───────────────────────────────────────────────────────────
def slugify(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"\s+", "-", text.strip())
    return re.sub(r"-+", "-", text)[:60].rstrip("-")

# ── HTML page builder ─────────────────────────────────────────────────────────
TAG_CLASS = {"TPR": "tpr", "PPF": "ppf", "ONS": "ons", "BoE": "boe"}
TAG_LABEL = {"TPR": "Regulatory Update", "PPF": "PPF Data Release",
             "ONS": "ONS Data Release", "BoE": "Bank of England Data"}
SOURCE_LABEL = {
    "TPR": "The Pensions Regulator — Press Releases",
    "PPF": "Pension Protection Fund — 7800 Index",
    "ONS": "Office for National Statistics — CPIH",
    "BoE": "Bank of England — Bank Rate",
}

def stats_html(stats):
    if not stats:
        return ""
    items = "\n".join(
        f'          <div class="stat-box">'
        f'<p class="stat-label">{s["label"]}</p>'
        f'<p class="stat-value">{s["value"]}</p></div>'
        for s in stats
    )
    return f'        <div class="stats-row">\n{items}\n        </div>\n'

def build_article_html(a):
    tc  = TAG_CLASS[a["source"]]
    cat = TAG_LABEL[a["source"]]
    src = SOURCE_LABEL[a["source"]]
    schema_type = "NewsArticle" if a["source"] == "TPR" else "Article"
    freq_line = (f'              <p><strong>Frequency:</strong> {a["frequency"]}</p>'
                 if a.get("frequency") else "")
    link_line = (f'              <p><strong>Full release:</strong> '
                 f'<a href="{a["link"]}" target="_blank" rel="noopener noreferrer">'
                 f'Read on {a["source"]} website ↗</a></p>'
                 if a.get("link") else "")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{a['title']} — pensionable.ai Intelligence</title>
  <meta name="description" content="{a['description']}" />
  <meta property="og:type" content="article" />
  <meta property="og:title" content="{a['title']} — pensionable.ai Intelligence" />
  <meta property="og:description" content="{a['description']}" />
  <meta property="og:url" content="https://pensionable.ai/intelligence/{a['slug']}.html" />
  <meta property="og:image" content="https://pensionable.ai/og-image.png" />
  <meta property="og:site_name" content="pensionable.ai" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{a['title']} — pensionable.ai Intelligence" />
  <meta name="twitter:description" content="{a['description']}" />
  <meta name="twitter:image" content="https://pensionable.ai/og-image.png" />
  <link rel="icon" type="image/svg+xml" href="../favicon.svg" />
  <link rel="icon" type="image/x-icon" href="../favicon.ico" />
  <link rel="apple-touch-icon" href="../apple-touch-icon.png" />
  <link rel="canonical" href="https://pensionable.ai/intelligence/{a['slug']}.html" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,400;0,500;0,600;0,700;0,800&family=Inter:wght@300;400;500&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="intelligence.css" />
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "{schema_type}",
    "headline": "{a['title']}",
    "description": "{a['description']}",
    "datePublished": "{a['date_iso']}",
    "url": "https://pensionable.ai/intelligence/{a['slug']}.html",
    "publisher": {{ "@type": "Organization", "name": "pensionable.ai", "url": "https://pensionable.ai" }},
    "breadcrumb": {{
      "@type": "BreadcrumbList",
      "itemListElement": [
        {{ "@type": "ListItem", "position": 1, "name": "Home", "item": "https://pensionable.ai/" }},
        {{ "@type": "ListItem", "position": 2, "name": "Intelligence", "item": "https://pensionable.ai/intelligence/" }},
        {{ "@type": "ListItem", "position": 3, "name": "{a['title']}", "item": "https://pensionable.ai/intelligence/{a['slug']}.html" }}
      ]
    }}
  }}
  </script>
  <style>
    .article-wrap {{ padding: 120px 0 var(--f34); }}
    .breadcrumb {{ display: flex; align-items: center; gap: 0.5rem; font-size: var(--t-sm); color: var(--text-caption); font-family: var(--font-mono); margin-bottom: var(--f8); }}
    .breadcrumb a {{ color: var(--text-caption); text-decoration: none; transition: color 0.2s; }}
    .breadcrumb a:hover {{ color: var(--accent-mid); }}
    .breadcrumb svg {{ width: 10px; height: 10px; opacity: 0.4; }}
    .article-header {{ margin-bottom: var(--f13); }}
    .article-header .tag {{ margin-bottom: var(--f5); }}
    .article-title {{ font-family: var(--font-head); font-weight: 800; font-size: clamp(1.6rem, 3.5vw, 2.8rem); line-height: 1.12; letter-spacing: -0.035em; margin-bottom: var(--f5); }}
    .article-byline {{ font-size: var(--t-sm); color: var(--text-caption); font-family: var(--font-mono); }}
    .stats-row {{ display: flex; gap: var(--f8); flex-wrap: wrap; margin: var(--f13) 0; }}
    .stat-box {{ background: var(--surface); border: 1px solid var(--border); border-radius: var(--r-card); padding: var(--f8); min-width: 160px; }}
    .stat-label {{ font-size: var(--t-sm); font-family: var(--font-mono); color: var(--text-caption); margin-bottom: var(--f3); }}
    .stat-value {{ font-family: var(--font-head); font-size: 2rem; font-weight: 800; letter-spacing: -0.04em; color: var(--accent-mid); }}
    .article-body {{ max-width: 720px; }}
    .article-body h2 {{ font-family: var(--font-head); font-size: 1.25rem; font-weight: 700; letter-spacing: -0.02em; margin-bottom: var(--f5); color: var(--text); }}
    .article-body p {{ font-size: var(--t-base); color: var(--text-muted); line-height: 1.8; margin-bottom: var(--f5); }}
    .article-body p:last-child {{ margin-bottom: 0; }}
    .source-block {{ margin-top: var(--f13); padding: var(--f8); background: var(--surface); border: 1px solid var(--border); border-radius: var(--r-card); }}
    .source-block p {{ font-size: var(--t-sm); font-family: var(--font-mono); color: var(--text-caption); margin-bottom: var(--f3); }}
    .source-block p:last-child {{ margin-bottom: 0; }}
    .source-block a {{ color: var(--accent-mid); text-decoration: none; }}
    .source-block a:hover {{ text-decoration: underline; }}
    .back-link {{ display: inline-flex; align-items: center; gap: 0.4rem; font-size: var(--t-sm); color: var(--text-caption); text-decoration: none; font-family: var(--font-mono); transition: color 0.2s; margin-top: var(--f13); }}
    .back-link:hover {{ color: var(--accent-mid); }}
    .back-link svg {{ width: 12px; height: 12px; }}
    .divider {{ border: none; border-top: 1px solid var(--border); margin: var(--f13) 0; }}
  </style>
</head>
<body>
  <a href="#main" class="skip-link">Skip to content</a>

  <nav class="site-nav" aria-label="Main navigation">
    <a href="../index.html" class="nav-logo">pensionable<span>.ai</span></a>
    <ul class="nav-links" role="list">
      <li><a href="../solutions.html">Solutions</a></li>
      <li><a href="index.html">Intelligence</a></li>
      <li><a href="../index.html#paradigm">About</a></li>
      <li><a href="../index.html#challenge">Contact</a></li>
    </ul>
    <div class="nav-cta"><a href="../index.html#challenge" class="btn-primary">Request Access</a></div>
    <button class="nav-hamburger" id="hamburger" aria-label="Open menu" aria-expanded="false" aria-controls="mobile-nav">
      <span></span><span></span><span></span>
    </button>
  </nav>
  <nav class="mobile-menu" id="mobile-nav">
    <a href="../solutions.html">Solutions</a>
    <a href="index.html">Intelligence</a>
    <a href="../index.html#challenge">Contact</a>
    <a href="../index.html#challenge" class="btn-primary">Request Access</a>
  </nav>

  <main id="main">
    <div class="article-wrap">
      <div class="container">
        <nav class="breadcrumb" aria-label="Breadcrumb">
          <a href="../index.html">Home</a>
          <svg viewBox="0 0 10 10" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M3 1l4 4-4 4"/></svg>
          <a href="index.html">Intelligence</a>
          <svg viewBox="0 0 10 10" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M3 1l4 4-4 4"/></svg>
          <span>{a['source']}</span>
        </nav>

        <article>
          <header class="article-header">
            <span class="tag tag-{tc}">{cat}</span>
            <h1 class="article-title">{a['title']}</h1>
            <p class="article-byline"><time datetime="{a['date_iso']}">{a['date_display']}</time> — {src}</p>
          </header>

{stats_html(a.get('stats'))}
          <div class="article-body">
            <h2>What This Means for Pension Schemes</h2>
            {a['body']}
            <div class="source-block">
              <p><strong>Source:</strong> {src}</p>
{link_line}
{freq_line}
              <p><strong>Date:</strong> {a['date_display']}</p>
            </div>
          </div>
        </article>

        <hr class="divider" />
        <a href="index.html" class="back-link">
          <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M13 8H3M7 4L3 8l4 4"/></svg>
          Back to Intelligence
        </a>
      </div>
    </div>
  </main>

  <footer>
    <div class="container">
      <div class="footer-inner">
        <a href="../index.html" class="footer-logo">pensionable<span>.ai</span></a>
        <ul class="footer-links" role="list">
          <li><a href="../solutions.html">Solutions</a></li>
          <li><a href="index.html">Intelligence</a></li>
          <li><a href="../index.html#challenge">Contact</a></li>
        </ul>
        <p class="footer-copy">&copy; 2025 pensionable.ai</p>
      </div>
    </div>
  </footer>

  <script>
    const hamburger = document.getElementById('hamburger');
    const mobileNav = document.getElementById('mobile-nav');
    hamburger.addEventListener('click', () => {{
      const open = mobileNav.classList.toggle('open');
      hamburger.setAttribute('aria-expanded', String(open));
    }});
  </script>
</body>
</html>
"""

# ── Index card builder ────────────────────────────────────────────────────────
def build_index_card(a):
    tc  = TAG_CLASS[a["source"]]
    stat_line = (f'\n            <p class="card-stat">{a["stat_display"]}</p>'
                 if a.get("stat_display") else "")
    return f"""
          <a href="{a['slug']}.html" class="article-card fade-up" data-source="{tc}">
            <div class="card-meta"><span class="tag tag-{tc}">{a['source']}</span><span class="card-date">{a['date_display']}</span></div>
            <p class="card-title">{a['title']}</p>{stat_line}
            <span class="card-read">Read analysis <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M3 8h10M9 4l4 4-4 4"/></svg></span>
          </a>"""

INSERT_MARKER = "<!-- ARTICLES_START -->"

def prepend_card_to_index(card_html):
    content = INDEX_HTML.read_text()
    if INSERT_MARKER not in content:
        print("⚠️  INSERT_MARKER not found in index.html — skipping index update")
        return
    content = content.replace(INSERT_MARKER, INSERT_MARKER + card_html)
    INDEX_HTML.write_text(content)

# ── Source: TPR (scrape press releases page) ─────────────────────────────────
TPR_PAGE = "https://www.thepensionsregulator.gov.uk/en/media-hub/press-releases"
TPR_BASE = "https://www.thepensionsregulator.gov.uk"

TPR_COMMENTARY = [
    ("AI", "ai", "The use of AI in pension administration is accelerating. TPR's guidance makes clear that trustees retain ultimate responsibility for decisions made with AI assistance. Schemes should ensure AI tools are subject to the same governance standards as other operational processes — with clear audit trails and human oversight at decision points."),
    ("dashboard", "dashboard", "Pensions dashboards represent one of the most data-intensive requirements the industry has faced. Schemes that have not yet audited their member data for accuracy and completeness are running out of time. The data quality bar is higher than most legacy systems were designed to meet."),
    ("fraud", "scam", "Pension scams remain a serious threat to member outcomes. Trustees have both a regulatory obligation and practical opportunity to embed scam warnings into every member communication. Schemes that treat this as a compliance checkbox rather than a genuine safeguard are missing the point."),
    ("surplus", "endgame", "With aggregate DB funding at historic highs, TPR is right to push for endgame clarity. Schemes in surplus face a genuine strategic choice between buyout, run-on, and superfund transfer. Trustees without a documented endgame strategy are increasingly out of step with regulatory expectations."),
    ("CDC", "cdc", "CDC schemes represent a meaningful middle ground between DB and DC — offering member income stability without the balance sheet risk of a guaranteed benefit. The regulatory framework provides the governance structure that large employers and master trusts need to move forward."),
    ("master trust", "scale", "The consolidation of DC into large master trusts is accelerating. Smaller schemes increasingly lack the scale to deliver competitive member outcomes and meet the regulatory cost-of-governance bar. Trustees of sub-scale DC schemes should be reviewing whether consolidation is in members' best interests."),
    ("value", "vfm", "Value for money assessment is moving from voluntary best-practice to regulatory expectation. Schemes that cannot demonstrate value across costs, net returns, and services will face increasing scrutiny. The data infrastructure required to answer these questions accurately is non-trivial."),
]

DEFAULT_TPR_BODY = ("TPR press releases signal regulatory priorities and enforcement activity. "
                    "Trustees and scheme administrators should review this release for relevance "
                    "to their own scheme governance, funding, and compliance obligations.")

def get_tpr_commentary(title):
    title_lower = title.lower()
    for keyword, _, commentary in TPR_COMMENTARY:
        if keyword.lower() in title_lower:
            return commentary
    return DEFAULT_TPR_BODY

def fetch_tpr(manifest):
    print("Fetching TPR press releases…")
    try:
        html = fetch(TPR_PAGE)
    except Exception as e:
        print(f"  TPR fetch failed: {e}")
        return []

    # Extract press release paths from the listing page
    paths = re.findall(
        r'href="(/en/media-hub/press-releases/\d{4}-press-releases/[^"]+)"', html
    )
    # Deduplicate while preserving order
    seen = set()
    unique_paths = [p for p in paths if not (p in seen or seen.add(p))]

    new_articles = []
    for path in unique_paths[:15]:  # check latest 15
        link = TPR_BASE + path
        uid  = hashlib.md5(link.encode()).hexdigest()[:12]

        if uid in manifest["generated"]:
            continue

        # Scrape the article page for title and date
        try:
            article_html = fetch(link)
        except Exception as e:
            print(f"  TPR article fetch failed ({path[-30:]}): {e}")
            continue

        # Extract title from <h1>
        title_m = re.search(r'<h1[^>]*>(.*?)</h1>', article_html, re.DOTALL)
        title   = re.sub(r'<[^>]+>', '', title_m.group(1)).strip() if title_m else path.split("/")[-1].replace("-", " ").title()

        # Extract date — common patterns: "20 May 2026", "May 2026"
        date_m = re.search(
            r'(\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})',
            article_html
        )
        if date_m:
            try:
                dt = datetime.strptime(date_m.group(1), "%d %B %Y")
            except Exception:
                dt = datetime.now(timezone.utc)
        else:
            dt = datetime.now(timezone.utc)

        date_display = dt.strftime("%-d %B %Y")
        date_iso     = dt.strftime("%Y-%m-%d")
        slug         = f"tpr-{date_iso[:7].replace('-', '')}-{slugify(title)[:45]}"
        commentary   = get_tpr_commentary(title)

        new_articles.append({
            "uid":          uid,
            "slug":         slug,
            "source":       "TPR",
            "title":        title,
            "description":  title,
            "date_display": date_display,
            "date_iso":     date_iso,
            "link":         link,
            "body":         f"<p>{DEFAULT_TPR_BODY}</p>\n            <p>{commentary}</p>",
            "stats":        None,
        })

    return new_articles

# ── Source: PPF 7800 ──────────────────────────────────────────────────────────
PPF_PAGE = "https://www.ppf.co.uk/PPF-7800-index"

def fetch_ppf(manifest):
    print("Fetching PPF 7800…")
    try:
        html = fetch(PPF_PAGE)
    except Exception as e:
        print(f"  PPF fetch failed: {e}")
        return []

    # Extract funding ratio from page
    ratio_m = re.search(r'(\d{2,3}\.\d)\s*%', html)
    if not ratio_m:
        print("  PPF: could not parse funding ratio")
        return []

    ratio = ratio_m.group(0).strip()
    month = datetime.now(timezone.utc).strftime("%B %Y")
    uid   = f"ppf-{datetime.now(timezone.utc).strftime('%Y-%m')}"

    if uid in manifest["generated"]:
        print(f"  PPF {month} already generated")
        return []

    # Try to find surplus
    surplus_m = re.search(r'surplus[^\d£]*£([\d,.]+)\s*(bn|m)', html, re.IGNORECASE)
    surplus = f"£{surplus_m.group(1)}{surplus_m.group(2)}" if surplus_m else "—"

    date_display = f"01 {month}"
    date_iso     = datetime.now(timezone.utc).strftime("%Y-%m-01")
    slug         = f"ppf7800-{date_iso[:7].replace('-', '')}-ppf7800_{datetime.now(timezone.utc).strftime('%B_%Y').lower()}"
    title        = f"PPF 7800 Index: {month}"

    return [{
        "uid":          uid,
        "slug":         slug,
        "source":       "PPF",
        "title":        title,
        "description":  f"PPF 7800 Index {month} — aggregate funding ratio {ratio}.",
        "date_display": date_display,
        "date_iso":     date_iso,
        "frequency":    "Monthly",
        "body":         (f"<p>The PPF 7800 Index for <strong>{month}</strong> shows an aggregate "
                         f"funding ratio of <strong>{ratio}</strong>.</p>\n            "
                         f"<p>With aggregate DB funding at historically strong levels, many schemes "
                         f"are now positioned to consider full buyout or run-off. Trustees should be "
                         f"actively engaging with insurers — surplus positions create negotiating "
                         f"leverage that may not persist.</p>"),
        "stats":        [{"label": "Funding Ratio", "value": ratio},
                         {"label": "Surplus", "value": surplus}],
        "stat_display": ratio,
    }]

# ── Source: ONS CPIH ──────────────────────────────────────────────────────────
# ONS CSV download — always returns latest full monthly series
ONS_API = "https://www.ons.gov.uk/generator?format=csv&uri=/economy/inflationandpriceindices/timeseries/l55o/mm23"

def fetch_ons(manifest):
    print("Fetching ONS CPIH…")
    try:
        csv_text = fetch(ONS_API)
    except Exception as e:
        print(f"  ONS fetch failed: {e}")
        return []

    # CSV format: header rows then "YYYY MON,value" monthly rows
    month_rows = []
    for line in csv_text.splitlines():
        parts = line.strip().split(",")
        if len(parts) == 2:
            # Monthly rows look like "2026 APR,3"
            m = re.match(r'^"?(\d{4}\s+[A-Z]{3})"?\s*,\s*"?([\d.]+)"?$', line.strip())
            if m:
                month_rows.append((m.group(1), m.group(2)))

    if not month_rows:
        print("  ONS: no monthly rows found in CSV")
        return []

    period, value = month_rows[-1]   # e.g. ("2026 APR", "3.0")
    uid = f"ons-cpih-{period.replace(' ', '-').lower()}"

    if uid in manifest["generated"]:
        print(f"  ONS CPIH {period} already generated")
        return []

    rate = f"{value}%"
    try:
        dt = datetime.strptime(period, "%Y %b")
    except Exception:
        # Try 3-char month abbreviation with proper casing
        try:
            dt = datetime.strptime(period.title(), "%Y %b")
        except Exception:
            dt = datetime.now(timezone.utc)

    release_dt   = dt.replace(day=18)
    date_display = release_dt.strftime("%-d %B %Y")
    date_iso     = release_dt.strftime("%Y-%m-%d")
    period_label = dt.strftime("%B %Y")
    slug         = f"cpih-{date_iso[:7].replace('-', '')}-cpih_{dt.strftime('%b_%Y').lower()}"

    try:
        prev_value  = month_rows[-2][1] if len(month_rows) > 1 else None
        monthly_chg = f"{float(value) - float(prev_value):+.2f}%" if prev_value else "—"
    except Exception:
        monthly_chg = "—"

    return [{
        "uid":          uid,
        "slug":         slug,
        "source":       "ONS",
        "title":        f"CPIH Update: {period_label}",
        "description":  f"CPIH annual rate {rate} — {period_label}.",
        "date_display": date_display,
        "date_iso":     date_iso,
        "frequency":    "Monthly, typically mid-month",
        "body":         (f"<p>The CPIH annual rate for <strong>{period_label}</strong> is "
                         f"<strong>{rate}</strong>.</p>\n            "
                         f"<p>CPIH at {rate} remains a key input for inflation-linked pension "
                         f"increases. Schemes should ensure cash flow projections reflect the "
                         f"current inflation environment. Trustees should confirm LDI strategies "
                         f"account for persistent above-target inflation where applicable.</p>"),
        "stats":        [{"label": "Annual Rate", "value": rate},
                         {"label": "Monthly Change", "value": monthly_chg}],
        "stat_display": rate,
    }]

# ── Source: Bank of England Bank Rate ─────────────────────────────────────────
BOE_API = (
    "https://www.bankofengland.co.uk/boeapps/iadb/fromshowcolumns.asp"
    "?csv.x=yes&Datefrom=01/Jan/2024&Dateto=now"
    "&SeriesCodes=IUMABEDR&CSVF=TN&UsingCodes=Y"
)

def fetch_boe(manifest):
    print("Fetching Bank of England rate…")
    try:
        csv_text = fetch(BOE_API)
    except Exception as e:
        print(f"  BoE fetch failed: {e}")
        return []

    lines = [l for l in csv_text.strip().splitlines() if l.strip()]
    # Find the most recent rate change (look for rows where value changes)
    data_rows = []
    for line in lines[1:]:  # skip header
        parts = line.split(",")
        if len(parts) >= 2:
            try:
                data_rows.append((parts[0].strip(), float(parts[1].strip())))
            except ValueError:
                pass

    if len(data_rows) < 2:
        return []

    # Find most recent change
    change_row = None
    for i in range(len(data_rows) - 1, 0, -1):
        if data_rows[i][1] != data_rows[i-1][1]:
            change_row = data_rows[i]
            prev_rate  = data_rows[i-1][1]
            break

    if not change_row:
        print("  BoE: no rate change found in range")
        return []

    date_str, rate = change_row
    uid = f"boe-{date_str.replace(' ', '-').lower()}"

    if uid in manifest["generated"]:
        print(f"  BoE rate change {date_str} already generated")
        return []

    try:
        dt = datetime.strptime(date_str, "%d %b %Y")
    except Exception:
        dt = datetime.now(timezone.utc)

    rate_str  = f"{rate:.2f}%"
    change    = rate - prev_rate
    chg_str   = f"{change:+.2f}%"
    direction = "Cut" if change < 0 else "Rise"
    date_display = dt.strftime("%-d %B %Y")
    date_iso     = dt.strftime("%Y-%m-%d")
    slug         = f"boe-{date_iso}-bankrate_{rate:.2f}".replace(".", "")

    return [{
        "uid":          uid,
        "slug":         slug,
        "source":       "BoE",
        "title":        f"Bank Rate {direction}: {rate_str}",
        "description":  f"Bank of England Bank Rate {direction.lower()} to {rate_str} — {date_display}.",
        "date_display": date_display,
        "date_iso":     date_iso,
        "frequency":    "At MPC meetings (approx every 6 weeks)",
        "body":         (f"<p>The Bank of England Monetary Policy Committee set Bank Rate at "
                         f"<strong>{rate_str}</strong> on {date_display}, a change of "
                         f"<strong>{chg_str}</strong>.</p>\n            "
                         f"<p>{'Falling' if change < 0 else 'Rising'} rates affect the discount "
                         f"rate used to value DB pension liabilities. Schemes without adequate "
                         f"LDI hedging will see their funding position move accordingly. Trustees "
                         f"should review hedging ratios and consider whether this move represents "
                         f"a trend or a one-off adjustment.</p>"),
        "stats":        [{"label": "Bank Rate", "value": rate_str},
                         {"label": "Change", "value": chg_str}],
        "stat_display": rate_str,
    }]

# ── Git push ──────────────────────────────────────────────────────────────────
def git_push(new_files, message):
    if DRY_RUN:
        print(f"[dry-run] Would commit: {message}")
        return

    git_email = os.environ.get("GIT_USER_EMAIL", "intelligence-bot@pensionable.ai")
    git_name  = os.environ.get("GIT_USER_NAME",  "Intelligence Bot")

    cmds = [
        ["git", "config", "user.email", git_email],
        ["git", "config", "user.name",  git_name],
        ["git", "add"] + [str(f) for f in new_files] + [str(MANIFEST), str(INDEX_HTML)],
        ["git", "commit", "-m", message],
        ["git", "push"],
    ]
    for cmd in cmds:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))
        if result.returncode != 0:
            print(f"  git error: {result.stderr.strip()}")
            break
    else:
        print(f"  ✓ Pushed: {message}")

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    INTEL_DIR.mkdir(exist_ok=True)
    manifest   = load_manifest()
    new_files  = []
    new_titles = []

    for fetch_fn in [fetch_tpr, fetch_ppf, fetch_ons, fetch_boe]:
        try:
            articles = fetch_fn(manifest)
        except Exception:
            traceback.print_exc()
            continue

        for a in articles:
            slug_path = INTEL_DIR / f"{a['slug']}.html"

            if DRY_RUN:
                print(f"  [dry-run] Would write: {a['slug']}.html  ←  {a['title'][:60]}")
            else:
                slug_path.write_text(build_article_html(a))
                print(f"  ✓ {a['slug']}.html")

            new_files.append(slug_path)
            new_titles.append(a["title"])

            # Prepend card to index
            prepend_card_to_index(build_index_card(a))

            # Add to sitemap
            sitemap_path = ROOT / "sitemap.xml"
            if sitemap_path.exists() and not DRY_RUN:
                sitemap = sitemap_path.read_text()
                new_url = (
                    f'\n  <url>\n'
                    f'    <loc>https://pensionable.ai/intelligence/{a["slug"]}.html</loc>\n'
                    f'    <lastmod>{a["date_iso"]}</lastmod>\n'
                    f'    <changefreq>never</changefreq>\n'
                    f'    <priority>0.7</priority>\n'
                    f'  </url>'
                )
                sitemap = sitemap.replace('</urlset>', new_url + '\n\n</urlset>')
                sitemap_path.write_text(sitemap)

            # Mark as generated
            manifest["generated"].append(a["uid"])

    if new_files:
        save_manifest(manifest)
        commit_msg = (f"intelligence: add {len(new_files)} article(s)\n\n" +
                      "\n".join(f"- {t}" for t in new_titles))
        git_push(new_files, commit_msg)
        print(f"\n✓ Done — {len(new_files)} new article(s) generated.")
    else:
        print("\nNo new articles. Everything up to date.")

if __name__ == "__main__":
    main()
