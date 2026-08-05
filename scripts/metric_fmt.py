import os

RESUME_DIR = "/Users/a0j0gu8/.wibey/desktop/wibey-chat-files/2026-07-13/1783962896659/portfolio-site/resumes"

REPLACEMENTS = [
    # S&OP leadership bullet — add ~75% (14 days → 3.5 days avg = 75% cycle reduction)
    (
        "compressing cross-functional decision cycles from ~2 weeks to 3–4 days.",
        "compressing cross-functional decision cycles ~75% (from ~2 weeks to 3–4 days)."
    ),
    # S&OP general bullet
    (
        "compressed time-to-decision from ~2 weeks to 3–4 days.",
        "compressed time-to-decision ~75% (from ~2 weeks to 3–4 days)."
    ),
    # Shopify stockout — bracket the dollars after the %
    (
        "reduced merchant stockouts 15% and generated $2M in incremental sales.",
        "reduced merchant stockouts 15% ($2M in incremental sales)."
    ),
    # Logitech supply — units first, then dollars in bracket
    (
        "Managed supply planning for a ~$400M global consumer electronics portfolio (400+ SKUs);",
        "Managed supply planning for 400+ SKUs (~$400M global portfolio);"
    ),
    # Cummins — add 63% before time metric (16-6)/16 = 62.5% -> 63%
    (
        "compressed disruption recovery time from 16 to 6 weeks.",
        "compressed disruption recovery 63% (from 16 to 6 weeks)."
    ),
    # SNAP bullet — bracket the dollars cleanly
    (
        "delivering inventory positioning signals 6+ weeks ahead and informing $400M+ in pre-emptive inventory decisions.",
        "delivering inventory positioning signals 6+ weeks ahead of impact ($400M+ in pre-emptive inventory decisions)."
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
    hits = []
    for old, new in REPLACEMENTS:
        if old in content:
            content = content.replace(old, new)
            hits.append(old[:50])
    if content != orig:
        with open(path, 'w') as f:
            f.write(content)
        print(f"UPDATED {fname}: {len(hits)} replacements")
        for h in hits:
            print(f"  + {h}...")
    else:
        print(f"no change: {fname}")
