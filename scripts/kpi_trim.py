import os

RESUME_DIR = "/Users/a0j0gu8/.wibey/desktop/wibey-chat-files/2026-07-13/1783962896659/portfolio-site/resumes"

# Trim the KPI bullet additions back to the minimum that keeps all metrics visible
# while staying within the 2-page layout for all 6 variants.
REPLACEMENTS = [
    # ── Bias bullet: trim the verbose new ending to a concise version ──────────
    # Current (too long):
    (
        "across 5–10B monthly units (~$15B+ monthly demand, 4,593 stores); "
        "automated ML triage of 50K+ weekly signals corrected forecast bias from −20% to near-neutral, "
        "improving in-stock rates and sMAPE-based forecast accuracy across Food &amp; Grocery.",

        # Trimmed: reuse original structure, add $ + KPIs at end only
        "across 5–10B monthly units (~$15B+ monthly demand, 4,593 stores), "
        "triaging 50K+ weekly signals; corrected systematic forecast bias from −20% to near-neutral, "
        "improving in-stock and sMAPE."
    ),

    # ── S&OP general: trim verbose ending, keep $5B+ + KPIs ──────────────────
    (
        "translated model outputs into executive forecast risk reporting; "
        "compressed time-to-decision ~75% (from ~2 weeks to 3–4 days) "
        "across ~$5B+ in weekly inventory replenishment decisions, "
        "improving in-stock and bias outcomes at F&amp;G SBU scale.",

        "drove executive-level forecast risk reporting; "
        "compressed ~$5B+ in weekly inventory decisions ~75% (from ~2 weeks to 3–4 days), "
        "improving in-stock, bias, and sMAPE."
    ),

    # ── S&OP leadership: trim to concise form with $5B+ + KPIs ───────────────
    (
        "presenting forecast risk and inventory strategy to VP-level stakeholders "
        "across ~$5B+ in weekly inventory replenishment decisions; "
        "compressed cross-functional decision cycles ~75% (from ~2 weeks to 3–4 days), "
        "improving in-stock and bias outcomes at F&amp;G SBU scale.",

        "presenting forecast risk on ~$5B+ in weekly inventory decisions to VP-level stakeholders; "
        "compressed decision cycles ~75% (from ~2 weeks to 3–4 days), "
        "improving in-stock, bias, and sMAPE."
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
        print(f"TRIMMED {fname}: {hits} replacements")
    else:
        print(f"no change: {fname}")
