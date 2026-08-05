import os

RESUME_DIR = "/Users/a0j0gu8/.wibey/desktop/wibey-chat-files/2026-07-13/1783962896659/portfolio-site/resumes"

REPLACEMENTS = [
    # ── Bias bullet: "improving sMAPE" → natural "forecast accuracy (bias and wMAPE)" ─
    (
        "maintaining stable in-stock positions and improving sMAPE across Food &amp; Grocery.",
        "improving forecast accuracy (bias and wMAPE) and maintaining stable in-stock positions."
    ),

    # ── Event/Seasonal bullet: "(sMAPE-measured)" → "(bias and wMAPE)" ──────────
    (
        "$292M in forecast error reduction (sMAPE-measured)",
        "$292M in forecast error reduction (bias and wMAPE)"
    ),

    # ── S&OP general bullet: "in-stock, bias, and sMAPE" → cleaner phrase ───────
    (
        "improving in-stock, bias, and sMAPE.",
        "improving in-stock rates and forecast accuracy (bias and wMAPE)."
    ),

    # ── S&OP leadership bullet: same cleanup ─────────────────────────────────────
    (
        "improving in-stock, bias, and sMAPE",
        "improving in-stock rates and forecast accuracy (bias and wMAPE)"
    ),

    # ── Any remaining bare sMAPE references → wMAPE ──────────────────────────────
    ("sMAPE", "wMAPE"),
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
    for old, new in REPLACEMENTS:
        content = content.replace(old, new)
    if content != orig:
        with open(path, 'w') as f:
            f.write(content)
        print(f"UPDATED {fname}")
    else:
        print(f"no change: {fname}")
