# Astha Jain — Job Search Toolkit

**Owner:** Astha Jain (`asthaj12`)  
**GitHub:** [github.com/asthaj12](https://github.com/asthaj12)  
**Live site:** [asthaj12.github.io](https://asthaj12.github.io)  
**Last updated:** August 2026

---

## What This Is

A complete job search toolkit: 6 targeted resume variants, a portfolio site, a private careers hub with job descriptions and interview prep, and 10 data dashboards — all live on GitHub Pages.

---

## Folder Structure

```
1783962896659/                    ← Project root (this folder)
│
├── portfolio-site/               ← MAIN GIT REPO → asthaj12.github.io
│   ├── index.html                ← Portfolio homepage
│   ├── photo.jpg                 ← Profile photo
│   └── resumes/                  ← All resume variants (CANONICAL)
│       ├── resume-industry-aj.html       ← Main: Cisco / Palo Alto / Marvell
│       ├── resume-npi-hardware.html      ← NPI: Zoox / Oracle
│       ├── resume-network-transport.html ← Network: Amazon
│       ├── resume-program-manager.html   ← PM: Google Pixel
│       ├── resume-ops-planning.html      ← Ops: Waymo
│       ├── resume-team-leader.html       ← Director: Nordstrom
│       ├── resume-consulting-strategy.html ← Consulting (bonus variant)
│       ├── resume-grad-school.html        ← Grad school (bonus variant)
│       ├── resume-leadership-director.html ← Director-level (bonus variant)
│       └── Resume-AJ-2026.docx           ← Word download (matches main HTML)
│
├── careers-astha/                ← PRIVATE CAREER HUB (separate repo)
│   ├── index.html                ← Hub home
│   ├── job-descriptions.html     ← 9 JDs with fit scores + resume links
│   ├── interview-questions.html  ← Comprehensive Q&A
│   ├── interview-prep.html       ← STAR answers, IBP explainer (local only)
│   └── resume-internal.html      ← Internal Walmart version
│
├── resumes/                      ← LOCAL ONLY — older/alternate drafts
│   │                               NOT pushed to GitHub, NOT canonical
│   ├── resume-industry-aj-internal.html  ← Internal version
│   ├── resume-interview-prep.html        ← Full interview prep (local only)
│   └── ...other older drafts
│
├── forecast-accuracy/            ← Portfolio project repos (local clones)
├── forecast-governance/          ←   for asthaj12/forecast-*
├── logitech-supply-planning/
├── npi-launch-planning/
├── pricing-demand-response/
├── replenishment-risk/
├── seasonal-planning/
├── shopify-demand-forecasting/
│
├── scripts/                      ← Utility Python scripts
│   ├── metric_fmt.py             ← Reformatted bullet metrics (units/$/%)
│   ├── kpi_fmt.py                ← Added in-stock / wMAPE / $20B to bullets
│   ├── kpi_trim.py               ← Trimmed text that caused 3-page overflow
│   ├── stable_inv.py             ← Added stable inventory + $20B language
│   └── wmape_fmt.py              ← Changed sMAPE → wMAPE format
│
├── make_resume_docx.py           ← Generates Resume-AJ-2026.docx from scratch
├── whitepaper.html               ← Supply chain whitepaper (local)
├── photo.jpg                     ← Profile photo backup
└── continuation.md               ← LIVE session handoff — read this first
```

---

## Resume Variants

| File | Target Role | Target Companies | S&OP Bullet |
|------|------------|-----------------|-------------|
| `resume-industry-aj.html` | Demand Planning Leader | Cisco, Palo Alto, Marvell | Position #4 |
| `resume-npi-hardware.html` | NPI / Hardware Supply | Zoox, Oracle | Position #4 |
| `resume-network-transport.html` | Network Demand Planner | Amazon | Position #4 |
| `resume-program-manager.html` | Category Supply / PM | Google Pixel | Position #1 |
| `resume-ops-planning.html` | Operations Planning | Waymo | Position #1 |
| `resume-team-leader.html` | Data & Analytics Leader | Nordstrom | Position #1 |

**Rule:** Leadership-focused roles have the S&OP / IBP bullet at position #1. Technical/forecasting roles keep it at #4.

---

## Key Design Decisions

- **No model names** on resume — practitioner voice, not tool names
- **2-page PDF layout**: Experience on page 1, Education + Portfolio on page 2
- **Page break**: `section.edu-section { page-break-before: always }` in print CSS
- **Base print font**: `8.5pt` (critical — keeps competency rows from wrapping and overflowing page 1)
- **wMAPE** (not sMAPE) — Walmart uses weighted MAPE as the accuracy KPI
- **KPI format**: "forecast accuracy (bias and wMAPE)" — readable to recruiter, precise for technical interviewer
- **Scale**: `~$20B+ monthly demand` = Walmart F&G ~$236B/yr ÷ 12. `~$5B+ weekly` = weekly replenishment at F&G scale. Both defensible from Walmart 10-K.

---

## How To Build & Deploy

### View resume in browser
```
open portfolio-site/resumes/resume-industry-aj.html
```

### Save as PDF
Click the "Save as PDF" button in the sticky nav bar (triggers browser print dialog). Chrome recommended.

### Regenerate Word doc
```bash
python3 make_resume_docx.py
# Output: portfolio-site/resumes/Resume-AJ-2026.docx
```

### Push to GitHub Pages
```bash
# IMPORTANT: unset GITHUB_TOKEN first on Walmart laptop (proxy conflict)
unset GITHUB_TOKEN
git -C portfolio-site push origin main
```

### Verify PDF page count (headless Chrome)
```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless --print-to-pdf=/tmp/check.pdf --no-pdf-header-footer --no-margins \
  "file://$(pwd)/portfolio-site/resumes/resume-industry-aj.html"

python3 -c "
import re
with open('/tmp/check.pdf','rb') as f: c=f.read()
print(re.findall(b'/Count (\d+)',c))
"
```
Expected output: `[b'2']` for all 6 variants.

---

## Tech Stack

| Layer | Tech |
|-------|------|
| Resumes | HTML/CSS (static, print-optimized) |
| DOCX | Python + raw Open XML (zipfile) |
| Charts/Dashboards | Chart.js 4.4.4 |
| Hosting | GitHub Pages (10 repos under asthaj12) |
| Font | system-ui (screen) / 8.5pt base (print) |

---

## GitHub Repos (under `asthaj12`)

| Repo | URL | Purpose |
|------|-----|---------|
| `asthaj12.github.io` | Portfolio + resumes | Main site + all resume HTML/DOCX |
| `careers-astha` | Private career hub | JDs, interview prep |
| `forecast-governance` | Dashboard | Forecast risk & inventory |
| `forecast-accuracy` | Dashboard | Accuracy modeling |
| `seasonal-planning` | Dashboard | Seasonal planning system |
| `replenishment-risk` | Dashboard | Replenishment analysis |
| `logitech-supply-planning` | Dashboard | Global supply planning |
| `npi-launch-planning` | Dashboard | NPI planning |
| `shopify-demand-forecasting` | Dashboard | Transportation forecasting |
| `pricing-demand-response` | Dashboard | Pricing & demand |

---

## Common Gotchas

| Problem | Fix |
|---------|-----|
| `git push` fails on Walmart laptop | `unset GITHUB_TOKEN` first |
| GitHub Pages 404 after rename | Settings → Pages → re-enable on each repo |
| Walmart proxy blocks asthaj12.github.io | Use personal WiFi |
| PDF is 3 pages | A competency row is wrapping (>118 chars). Trim it or reduce a bullet. |
| PDF is 1 page (everything squished) | Print CSS font set to 9pt+. Check if `body { font-size }` in `@media print` reverted to 9pt. Should be `8.5pt`. |
| DOCX looks different from HTML | Regenerate with `make_resume_docx.py` after any HTML changes |
| `page-break-inside: avoid` on `.job` | **DO NOT ADD** — causes whitespace gaps on page 1 |

---

## Print CSS Quick Reference

The print CSS lives in each HTML file's `<style>` block. All 6 files are identical in print CSS.

```css
@media print {
  body { font-size: 8.5pt; line-height: 1.46; }   /* 8.5pt is CRITICAL */
  section { margin-bottom: 13px; }
  .job { margin-bottom: 15px; }
  li { font-size: 8.5pt; margin-bottom: 5px; line-height: 1.46; }
  .competencies { font-size: 8.2pt; line-height: 1.60; }  /* 8.2pt prevents row wrapping */
  section.edu-section { page-break-before: always; }       /* Forces Education to page 2 */
}
```

To change spacing and verify it still renders as 2 pages:
```bash
# Edit the value, then run the headless Chrome page-count check above
# Safe budget: competency value text must be ≤ 95 chars (label "Planning & Operations:" = 23 chars extra)
```

---

## Session Handoff Files

| File | Purpose |
|------|---------|
| `continuation.md` | LIVE — current state, pending tasks, gotchas |
| `continuation-2026-08-04-210805.md` | Prior session snapshot |
| `continuation-2026-08-04-232802.md` | Prior session snapshot |

Always update `continuation.md` before ending a work session.

---

## Pending Work (as of August 2026)

- [ ] **Interview questions page** (`careers-astha/interview-questions.html`) — comprehensive Q&A covering behavioral, technical, JD-specific, Amazon LP, Google Googleyness
- [ ] **DOCX** — regenerate after recent bullet/summary changes
- [ ] **Dashboard fixes** — tab switching on Waterfall + Item Health (Forecast Governance)
- [ ] **Mobile overlaps** on dashboards
- [ ] **Sub-dashboard snavs** — rism_impact_tracker, price_change_tracker
