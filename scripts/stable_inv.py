import os, re

RESUME_DIR = "/Users/a0j0gu8/.wibey/desktop/wibey-chat-files/2026-07-13/1783962896659/portfolio-site/resumes"

REPLACEMENTS = [
    # ── Bump $15B+ → $20B+ (Walmart F&G is ~$236B/yr = ~$20B/mo, defensible) ─
    ("~$15B+ monthly demand", "~$20B+ monthly demand"),

    # ── Main summary: add stable inventory language ───────────────────────────
    # industry-aj summary ends with "...VP-level stakeholder decisions. MIT-credentialed..."
    (
        "translating model outputs into executive-ready inventory strategy and VP-level stakeholder decisions.",
        "translating model outputs into executive-ready inventory strategy and VP-level stakeholder decisions — "
        "maintaining stable in-stock positions and reducing bias and sMAPE across the portfolio."
    ),

    # ── Bias bullet: swap "improving in-stock and sMAPE" for fuller KPI phrase ─
    (
        "corrected systematic forecast bias from −20% to near-neutral, improving in-stock and sMAPE.",
        "corrected systematic forecast bias from −20% to near-neutral — "
        "maintaining stable in-stock positions and improving sMAPE across Food &amp; Grocery."
    ),
]

FILES = [
    "resume-industry-aj.html", "resume-npi-hardware.html", "resume-network-transport.html",
    "resume-program-manager.html", "resume-ops-planning.html", "resume-team-leader.html"
]

for fname in FILES:
    path = os.path.join(RESUME_DIR, fname)
    with open(path) as f:
        content = f.read()
    orig = content
    hits = 0
    for old, new in REPLACEMENTS:
        if old in content:
            content = content.replace(old, new)
            hits += 1
    if content != orig:
        with open(path, 'w') as f:
            f.write(content)
        print(f"UPDATED {fname}: {hits} replacements")
    else:
        print(f"no change: {fname}")
