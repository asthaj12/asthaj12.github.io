"""Run all three models, write results/*.json, charts in assets/, and the portfolio page index.html.
Usage:  python run_all.py            (CBC solver, bundled with PuLP)
        python run_all.py --highs    (HiGHS solver)"""
import json, os, sys, html
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pulp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'models'))
import network_flow as nf
import capacity_expansion as ce
import constrained_allocation as ca

SOLVER = pulp.HiGHS(msg=False) if '--highs' in sys.argv else pulp.PULP_CBC_CMD(msg=False)
os.makedirs(os.path.join(HERE, 'assets'), exist_ok=True)
os.makedirs(os.path.join(HERE, 'results'), exist_ok=True)
INK, BLUE, TEAL, ORANGE, GREY = '#1f2937', '#2a78d6', '#1f9d8b', '#e07b39', '#9ca3af'
plt.rcParams.update({'font.family': 'sans-serif', 'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False,
                     'axes.edgecolor': '#d1d5db', 'axes.labelcolor': INK, 'xtick.color': INK, 'ytick.color': INK})


def save(fig, name):
    fig.tight_layout(); fig.savefig(os.path.join(HERE, 'assets', name), dpi=160); plt.close(fig)


# ---------------- Model 1 ----------------
m1 = nf.run(SOLVER)
fig, ax = plt.subplots(figsize=(6.4, 3.4))
labels = [r['scenario'] for r in m1]
parts = [('shipping_cost', 'Shipping', BLUE), ('surge_cost', 'Surge capacity', TEAL), ('lost_margin', 'Lost margin (unmet demand)', ORANGE)]
bottom = [0] * len(m1)
for key, lab, col in parts:
    vals = [r[key] / 1e6 for r in m1]
    ax.bar(labels, vals, bottom=bottom, color=col, label=lab, width=0.55)
    bottom = [b + v for b, v in zip(bottom, vals)]
for i, r in enumerate(m1):
    ax.text(i, bottom[i] + 0.03, f"fill {r['fill_rate']:.0%}", ha='center', fontsize=9, color=INK)
ax.set_ylabel('Peak-week cost ($M)'); ax.legend(frameon=False, fontsize=8, loc='upper left')
save(fig, 'm1_cost_by_scenario.png')

stress = m1[-1]
fig, ax = plt.subplots(figsize=(6.4, 3.0))
names = [n.split(' (')[0] for n in nf.NODES]
ax.barh(names, [stress['capacity_shadow_price'][n] for n in nf.NODES], color=BLUE)
ax.set_xlabel('$ value of one more unit of node capacity (stress peak)'); ax.invert_yaxis()
save(fig, 'm1_shadow_prices.png')

# ---------------- Model 2 ----------------
m2 = ce.run(SOLVER)
opt = m2[0]
fig, ax = plt.subplots(figsize=(6.4, 3.4))
t = list(range(ce.T))
for k, col in (('Low', GREY), ('Base', INK), ('High', ORANGE)):
    ax.plot(t, opt['demand'][k], color=col, lw=1.6, ls='--' if k != 'Base' else '-', label=f'Demand — {k}')
ax.step(t, opt['capacity'], where='post', color=BLUE, lw=2.4, label='Capacity (optimal order plan)')
ax.axvspan(0, ce.LEAD, color='#eef2f7', zorder=0); ax.text(0.4, 103, 'locked by 9-month\nlead time', fontsize=8, color='#6b7280', va='bottom')
ax.set_xlabel('Month'); ax.set_ylabel('Capacity units'); ax.legend(frameon=False, fontsize=8, loc='upper left')
save(fig, 'm2_capacity_vs_demand.png')

fig, ax1 = plt.subplots(figsize=(6.4, 3.2))
sweep = m2[1:]
hx = [f"{r['headroom']:.0%}" for r in sweep]
ax1.bar(hx, [r['stranded_capital_expected'] / 1e6 for r in sweep], color=TEAL, width=0.55, label='Expected stranded capacity cost ($M)')
ax1.set_xlabel('Required headroom over base forecast'); ax1.set_ylabel('Stranded capacity ($M)')
ax2 = ax1.twinx(); ax2.plot(hx, [r['capacity_out_months_High'] for r in sweep], color=ORANGE, marker='o', lw=2, label='Capacity-out months (high case)')
ax2.set_ylabel('Capacity-out months'); ax2.spines['right'].set_visible(True)
h1, l1 = ax1.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
ax1.legend(h1 + h2, l1 + l2, frameon=False, fontsize=8, loc='lower center', bbox_to_anchor=(0.5, 1.0), ncol=2)
ax2.set_ylim(0, max(r['capacity_out_months_High'] for r in sweep) + 2)
save(fig, 'm2_headroom_tradeoff.png')

# ---------------- Model 3 ----------------
m3 = ca.run(SOLVER)
b3 = m3['base']
fig, ax = plt.subplots(figsize=(6.4, 3.2))
ch = list(ca.CHANNELS)
ax.bar(ch, [ca.CHANNELS[c][0] for c in ch], color='#e5e7eb', width=0.6, label='Demand')
ax.bar(ch, [b3['allocation'][c] for c in ch], color=BLUE, width=0.6, label='Allocated')
ax.scatter(ch, [ca.CHANNELS[c][0] * ca.CHANNELS[c][2] for c in ch], color=ORANGE, zorder=3, marker='_', s=600, label='Fill floor')
ax.set_ylabel('Units'); ax.legend(frameon=False, fontsize=8); plt.setp(ax.get_xticklabels(), rotation=12, ha='right')
save(fig, 'm3_allocation.png')

json.dump(dict(model1=m1, model2=[{k: v for k, v in r.items() if k != 'demand'} for r in m2] + [{'demand': m2[0]['demand']}], model3=m3),
          open(os.path.join(HERE, 'results', 'results.json'), 'w'), indent=1, default=float)

# ---------------- page ----------------
base, high, st = m1[0], m1[1], m1[2]
hi_opt = m2[0]; hi25 = m2[-1]
e = html.escape
page = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Network &amp; Capacity Optimizer — Astha Jain</title>
<meta name="description" content="Three supply chain decisions solved as optimization models in Python (PuLP) and Excel Solver: peak network allocation, long-lead capacity expansion, and constrained supply allocation.">
<style>
:root{{--ink:#1f2937;--mute:#6b7280;--line:#e5e7eb;--blue:#2a78d6;--bg:#f8fafc}}
*{{box-sizing:border-box;margin:0;padding:0}} body{{font-family:system-ui,-apple-system,'Segoe UI',Helvetica,Arial,sans-serif;color:var(--ink);background:var(--bg);line-height:1.55}}
header{{background:#0f172a;color:#f8fafc;padding:48px 24px 40px}} .wrap{{max-width:980px;margin:0 auto}}
header a{{color:#93c5fd;text-decoration:none;font-size:14px}} h1{{font-size:32px;margin:10px 0 8px;letter-spacing:-.01em}}
header p{{color:#cbd5e1;max-width:760px}} .chips{{margin-top:16px;display:flex;flex-wrap:wrap;gap:8px}}
.chip{{font-size:12px;border:1px solid #334155;border-radius:999px;padding:3px 10px;color:#e2e8f0}}
.note{{background:#fff7ed;border:1px solid #fed7aa;color:#9a3412;border-radius:8px;padding:10px 14px;font-size:13px;margin:24px 0}}
.card{{background:#fff;border:1px solid var(--line);border-radius:14px;padding:26px;margin:22px 0}}
.card h2{{font-size:21px;margin-bottom:4px}} .kicker{{color:var(--blue);font-weight:700;font-size:12px;letter-spacing:.08em;text-transform:uppercase}}
.grid3{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin:16px 0}} .grid3 div{{background:var(--bg);border-radius:10px;padding:12px 14px;font-size:14px}}
.grid3 b{{display:block;font-size:12px;color:var(--mute);text-transform:uppercase;letter-spacing:.06em;margin-bottom:4px}}
.kpis{{display:flex;flex-wrap:wrap;gap:12px;margin:14px 0}} .kpi{{border:1px solid var(--line);border-radius:10px;padding:10px 14px;min-width:150px}}
.kpi span{{display:block;font-size:22px;font-weight:800;color:var(--blue)}} .kpi small{{color:var(--mute);font-size:12px}}
.figs{{display:grid;grid-template-columns:1fr 1fr;gap:14px}} img{{width:100%;border:1px solid var(--line);border-radius:10px;background:#fff}}
details{{margin-top:12px;font-size:14px}} summary{{cursor:pointer;color:var(--blue);font-weight:600}} details ul{{margin:8px 0 0 18px}}
pre{{background:#0f172a;color:#e2e8f0;border-radius:10px;padding:14px;font-size:13px;overflow:auto;margin-top:10px}}
footer{{color:var(--mute);font-size:13px;padding:30px 24px 50px;text-align:center}}
@media(max-width:760px){{.grid3,.figs{{grid-template-columns:1fr}} h1{{font-size:26px}}}}
</style></head><body>
<header><div class="wrap">
<a href="https://asthaj12.github.io">&larr; Portfolio</a>
<h1>Network &amp; Capacity Optimizer</h1>
<p>Three decisions supply and capacity planners make under constraint, built as optimization models in Python (PuLP) and Excel Solver. Each one answers a planning question with a cost, a risk, and the value of one more unit of capacity.</p>
<div class="chips"><span class="chip">Network &amp; Capacity Planning</span><span class="chip">Optimization Modeling</span><span class="chip">Python · PuLP · CBC / HiGHS</span><span class="chip">Excel Solver</span><span class="chip">Scenario Planning</span><span class="chip">Constrained Allocation</span></div>
</div></header>
<main class="wrap" style="padding:0 24px">
<div class="note">Independent portfolio project. All data is synthetic. The problem shapes come from planning work I've done (fulfillment networks, contract-manufacturer allocation, supplier and line capacity), but no employer data, systems, or figures are used.</div>

<section class="card" id="network">
<div class="kicker">Model 1 · Mixed-integer program</div><h2>Peak network &amp; carrier allocation</h2>
<div class="grid3"><div><b>What it decides</b>Which fulfillment node serves each region by which carrier, and where to open surge capacity for peak week.</div>
<div><b>Why it matters</b>Peak capacity is booked weeks ahead. Too little means missed delivery promises and lost sales; too much is paid-for space that sits idle.</div>
<div><b>What it found</b>Under stress demand, carrier capacity runs out before building capacity, so adding surge space alone cannot hold fill.</div></div>
<div class="kpis"><div class="kpi"><span>{base['fill_rate']:.0%}</span><small>fill, base peak</small></div><div class="kpi"><span>{st['fill_rate']:.0%}</span><small>fill, stress peak (+38%)</small></div>
<div class="kpi"><span>{sum(st['surge_blocks'].values())}</span><small>surge blocks opened, stress</small></div><div class="kpi"><span>${max(st['capacity_shadow_price'].values()):.0f}</span><small>top value of +1 unit node capacity</small></div></div>
<div class="figs"><img src="assets/m1_cost_by_scenario.png" alt="Peak-week cost by scenario split into shipping, surge capacity and lost margin, with fill rate"><img src="assets/m1_shadow_prices.png" alt="Value of one more unit of capacity at each fulfillment node in the stress scenario"></div>
<details><summary>How it's modeled</summary><ul>
<li><b>Decisions:</b> units shipped per node → region → carrier (continuous); surge blocks per node (integer, 0–{nf.MAX_BLOCKS}).</li>
<li><b>Objective:</b> minimize shipping cost + surge cost (${nf.SURGE_BLOCK_COST:,} per {nf.SURGE_BLOCK_UNITS:,}-unit block) + ${nf.LOST_MARGIN:.0f} lost margin per unmet unit.</li>
<li><b>Constraints:</b> every region's demand is met or counted as unmet; node capacity plus surge; carrier capacity per node; only lanes that meet a {nf.PROMISE_DAYS}-day delivery promise are allowed.</li>
<li><b>Shadow prices:</b> re-solved as a linear program with surge fixed, to read what one more unit of capacity is worth at each node.</li></ul></details>
</section>

<section class="card" id="capacity">
<div class="kicker">Model 2 · Stochastic mixed-integer program</div><h2>Long-lead capacity expansion</h2>
<div class="grid3"><div><b>What it decides</b>How many capacity blocks to order each month when every order lands {ce.LEAD} months later, before you know which demand scenario will play out.</div>
<div><b>Why it matters</b>Order too late and customers hit a capacity-out; order too early and capital sits stranded. One order plan has to work across low, base, and high growth.</div>
<div><b>What it found</b>The first {ce.LEAD} months are already decided by past orders. A bigger buffer over the base forecast adds stranded capital but barely protects the high case, which argues for staged, cancellable commitments.</div></div>
<div class="kpis"><div class="kpi"><span>{hi_opt['blocks_ordered']}</span><small>blocks ordered, optimal plan</small></div><div class="kpi"><span>${hi_opt['expected_cost']/1e6:,.1f}M</span><small>expected total cost</small></div>
<div class="kpi"><span>{hi_opt['capacity_out_months_Base']}</span><small>capacity-out months, base case</small></div><div class="kpi"><span>{hi_opt['capacity_out_months_High']} → {hi25['capacity_out_months_High']}</span><small>high-case capacity-out months, 0% → 25% headroom</small></div></div>
<div class="figs"><img src="assets/m2_capacity_vs_demand.png" alt="Capacity from the optimal order plan against low, base and high demand over 24 months"><img src="assets/m2_headroom_tradeoff.png" alt="Trade-off between required headroom, stranded capacity cost and high-case capacity-out months"></div>
<details><summary>How it's modeled</summary><ul>
<li><b>Decisions:</b> blocks ordered per month (integer); one plan for all scenarios, because orders are committed before demand is known.</li>
<li><b>Objective:</b> minimize capital (${ce.CAPEX/1e6:.1f}M per {ce.BLOCK}-unit block) + probability-weighted idle cost (${ce.IDLE_COST:,} per unit-month) + shortfall cost (${ce.SHORT_COST:,} per unit-month).</li>
<li><b>Constraints:</b> capacity in month t = installed + pipeline + orders placed {ce.LEAD}+ months earlier; balance of capacity, demand, shortfall and idle per scenario; optional headroom policy over base demand.</li>
<li><b>Scenarios:</b> low / base / high growth (25% / 50% / 25%), with a step ramp in month 12.</li></ul></details>
</section>

<section class="card" id="allocation">
<div class="kicker">Model 3 · Linear program · also in Excel Solver</div><h2>Constrained supply allocation</h2>
<div class="grid3"><div><b>What it decides</b>How to split supply that is 30% below demand across channels with different margins and contractual fill floors.</div>
<div><b>Why it matters</b>Shortage calls usually end up as negotiations. A model makes the trade-off explicit, so each team can see what its commitment costs.</div>
<div><b>What it found</b>One more unit of supply is worth ${b3['supply_shadow_price']:.0f}. Honoring every fill floor costs ${m3['cost_of_commitments']:,.0f} in margin, and the Education floor alone costs ${b3['floor_cost']['Education B2B']:.0f} per unit.</div></div>
<div class="kpis"><div class="kpi"><span>${b3['margin']:,.0f}</span><small>margin, all floors honored</small></div><div class="kpi"><span>${b3['supply_shadow_price']:.0f}</span><small>value of +1 unit of supply</small></div>
<div class="kpi"><span>${m3['value_of_500_more']:,.0f}</span><small>value of +500 units</small></div><div class="kpi"><span>${m3['cost_of_commitments']:,.0f}</span><small>cost of all fill floors</small></div></div>
<div class="figs"><img src="assets/m3_allocation.png" alt="Demand, allocation and fill floor by channel"><div class="kpi" style="font-size:14px"><b>Excel version</b><br>Download <a href="excel/constrained_allocation_solver.xlsx">constrained_allocation_solver.xlsx</a>. The Solver dialog comes pre-loaded (objective, changing cells, constraints, Simplex LP): open it, go to Data &gt; Solver &gt; Solve, and compare with the PuLP answer in column I. Tick the Sensitivity report to see the same shadow prices.</div></div>
</section>

<section class="card"><div class="kicker">Run it</div><h2>Reproduce the results</h2>
<pre>python -m venv .venv &amp;&amp; source .venv/bin/activate
pip install "pulp&gt;=2.9,&lt;3" highspy matplotlib openpyxl
python run_all.py            # CBC solver (bundled with PuLP)
python run_all.py --highs    # same models on HiGHS
python excel/build_workbook.py</pre></section>
</main>
<footer>Astha Jain · <a href="https://asthaj12.github.io">asthaj12.github.io</a> · Synthetic data, independent project.</footer>
</body></html>"""
open(os.path.join(HERE, 'index.html'), 'w', encoding='utf-8').write(page)
print('Model 1:', [(r['scenario'], f"{r['fill_rate']:.1%}") for r in m1])
print('Model 2: optimal blocks', hi_opt['blocks_ordered'], 'high cap-out', hi_opt['capacity_out_months_High'], '->', hi25['capacity_out_months_High'])
print('Model 3: margin', round(b3['margin']), 'shadow', b3['supply_shadow_price'])
print('wrote index.html, assets/, results/results.json')
