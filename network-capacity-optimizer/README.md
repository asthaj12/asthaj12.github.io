# Network & Capacity Optimizer

Three decisions supply and capacity planners make under constraint, built as optimization
models in **Python (PuLP)** and **Excel Solver**. Each model answers a planning question with a
cost, a risk, and a shadow price: the value of one more unit of capacity.

| Model | Type | Decision | Planning question |
|---|---|---|---|
| 1. Peak network & carrier allocation | MILP | Node → region → carrier flows; surge blocks per node | Where do we add peak capacity, and is space or carrier capacity the real constraint? |
| 2. Long-lead capacity expansion | Stochastic MILP | Capacity blocks ordered per month, 9-month lead time, one plan across 3 demand scenarios | How much do we commit before demand is known, and what does extra headroom buy? |
| 3. Constrained supply allocation | LP (+ Excel Solver) | Units per channel when supply is 30% short | Who gets short supply, and what does each fill commitment cost? |

**All data is synthetic.** The problem shapes come from planning work I've done (fulfillment
networks, contract-manufacturer allocation, supplier and line capacity), but no employer data,
systems, or figures are used.

## Run

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python run_all.py            # CBC solver (bundled with PuLP)
python run_all.py --highs    # same models on HiGHS
python excel/build_workbook.py
```

Outputs: `index.html` (portfolio page), `assets/*.png` (charts), `results/results.json`,
`excel/constrained_allocation_solver.xlsx` (Solver dialog pre-loaded; Data > Solver > Solve).

## How each model works

**1. Peak network & carrier allocation** (`models/network_flow.py`)
- Decisions: units shipped per node/region/carrier (continuous); surge blocks per node (integer).
- Objective: min shipping + surge cost + lost margin on unmet demand.
- Constraints: demand balance; node capacity + surge; carrier capacity per node; only lanes that
  meet a 3-day delivery promise.
- Shadow prices: LP re-solve with surge fixed. What one more unit of node capacity is worth.

**2. Long-lead capacity expansion** (`models/capacity_expansion.py`)
- Decisions: blocks ordered each month (integer); a single plan for all scenarios, because
  orders are committed before demand is observable.
- Objective: min capital + expected idle (stranded) cost + expected shortfall (capacity-out) cost.
- Constraints: capacity = installed + pipeline + orders placed ≥ 9 months earlier; per-scenario
  balance; optional headroom policy, swept 0–25%.

**3. Constrained supply allocation** (`models/constrained_allocation.py`, `excel/`)
- Decisions: units per channel. Objective: max margin.
- Constraints: total ≤ supply; channel ≤ demand; channel ≥ fill floor.
- Shadow price on supply = value of one more unit. Shadow price on each floor = what that
  commitment costs.

## Notes
- PuLP 2.x API (classic). CBC ships with PuLP; HiGHS via `highspy`. Duals are read from CBC.
