import os

RESUME_DIR = "/Users/a0j0gu8/.wibey/desktop/wibey-chat-files/2026-07-13/1783962896659/portfolio-site/resumes"

REPLACEMENTS = [
    # ── Summary: add dollar volume to 5-10B mention ──────────────────────────
    (
        "(Walmart US, 5–10B monthly units)",
        "(Walmart US, 5–10B monthly units, ~$15B+ monthly demand)"
    ),

    # ── Bullet 1: Bias Correction — add $ + in-stock + sMAPE ─────────────────
    (
        "Engineered a bias-correction and anomaly-detection pipeline across 5–10B monthly units (4,593 stores), "
        "triaging 50K+ weekly signals via automated ML scoring models and driving systematic forecast bias from −20% to near-neutral.",
        "Engineered a bias-correction and anomaly-detection pipeline across 5–10B monthly units (~$15B+ monthly demand, 4,593 stores); "
        "automated ML triage of 50K+ weekly signals corrected forecast bias from −20% to near-neutral, "
        "improving in-stock rates and sMAPE-based forecast accuracy across Food &amp; Grocery."
    ),

    # ── Bullet 3: Event/Seasonal — add sMAPE as the accuracy KPI name ────────
    (
        "achieved $292M reduction in forecast error and surfaced $7.6M in anomalous override exposure.",
        "achieved $292M in forecast error reduction (sMAPE-measured) and surfaced $7.6M in anomalous override exposure."
    ),

    # ── Bullet 4 (general): S&OP — add weekly inventory $ + in-stock KPI ─────
    (
        "translated model outputs into executive forecast risk reporting and compressed time-to-decision ~75% (from ~2 weeks to 3–4 days).",
        "translated model outputs into executive forecast risk reporting; compressed time-to-decision ~75% (from ~2 weeks to 3–4 days) "
        "across ~$5B+ in weekly inventory replenishment decisions, improving in-stock and bias outcomes at F&amp;G SBU scale."
    ),

    # ── Bullet 4 (leadership): S&OP — same dollar/KPI framing ───────────────
    (
        "presenting forecast risk and inventory strategy to VP-level stakeholders and compressing cross-functional decision cycles ~75% (from ~2 weeks to 3–4 days).",
        "presenting forecast risk and inventory strategy to VP-level stakeholders across ~$5B+ in weekly inventory replenishment decisions; "
        "compressed cross-functional decision cycles ~75% (from ~2 weeks to 3–4 days), improving in-stock and bias outcomes at F&amp;G SBU scale."
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
