"""Model 2 — Long-lead capacity expansion under demand uncertainty (stochastic MILP).

Decision: how many capacity blocks to ORDER each month, knowing each order lands 9 months later,
before you know which demand scenario will happen. One order plan must serve all scenarios
(you commit before demand is observable).
Objective: minimize capital cost + expected idle-capacity cost (stranded capital) +
expected shortfall cost (capacity-outs that block customers / revenue).
Policy sweep: force a minimum headroom buffer (0-25%) over base demand and show the
trade-off between capacity-outs and stranded capacity.

All data is synthetic. The structure applies to any long-lead capacity: production lines,
tooling, warehouse space, or compute and network hardware.
"""
import pulp

T = 24                  # monthly planning horizon
LEAD = 9                # months from order to usable capacity
BLOCK = 10              # capacity units per block
CAPEX = 1_200_000       # $ per block
IDLE_COST = 12_000      # $ per idle unit-month (depreciation, power, space)
SHORT_COST = 90_000     # $ per short unit-month (blocked customers, lost revenue)
C0 = 120                # installed capacity today
PIPELINE = {3: 2, 6: 1}  # blocks already on order: arrive in month 3 and month 6

SCENARIOS = {  # name: (probability, monthly growth, step ramp at month 12)
    'Low':  (0.25, 0.015, 0),
    'Base': (0.50, 0.030, 10),
    'High': (0.25, 0.050, 25),
}


def demand_paths():
    paths = {}
    for k, (_, g, step) in SCENARIOS.items():
        d, path = 100.0, []
        for t in range(T):
            d *= (1 + g)
            path.append(d + (step if t >= 12 else 0))
        paths[k] = path
    return paths


def solve(headroom=None, solver=None):
    D = demand_paths()
    m = pulp.LpProblem('capacity_expansion', pulp.LpMinimize)
    order = pulp.LpVariable.dicts('order', range(T - LEAD), lowBound=0, upBound=6, cat='Integer')

    def cap(t):
        landed = pulp.lpSum(order[s] for s in range(T - LEAD) if s + LEAD <= t)
        pipe = sum(b for mth, b in PIPELINE.items() if mth <= t)
        return C0 + BLOCK * (pipe + landed)

    short = {(k, t): pulp.LpVariable(f'short_{k}_{t}', lowBound=0) for k in SCENARIOS for t in range(T)}
    idle = {(k, t): pulp.LpVariable(f'idle_{k}_{t}', lowBound=0) for k in SCENARIOS for t in range(T)}
    for k in SCENARIOS:
        for t in range(T):
            m += cap(t) - D[k][t] + short[k, t] - idle[k, t] == 0, f'bal_{k}_{t}'
    if headroom is not None:
        for t in range(LEAD, T):  # can only influence capacity after the first lead time
            m += cap(t) >= (1 + headroom) * D['Base'][t], f'headroom_{t}'

    p = {k: v[0] for k, v in SCENARIOS.items()}
    m += (CAPEX * pulp.lpSum(order.values())
          + pulp.lpSum(p[k] * (IDLE_COST * idle[k, t] + SHORT_COST * short[k, t]) for k in SCENARIOS for t in range(T)))
    m.solve(solver or pulp.PULP_CBC_CMD(msg=False))

    orders = [round(order[s].value()) for s in range(T - LEAD)]
    capacity = [pulp.value(cap(t)) for t in range(T)]
    out = dict(headroom=headroom, status=pulp.LpStatus[m.status], expected_cost=pulp.value(m.objective),
               blocks_ordered=sum(orders), orders=orders, capacity=capacity, demand=D)
    for k in SCENARIOS:
        out[f'capacity_out_months_{k}'] = sum(1 for t in range(T) if short[k, t].value() > 1e-6)
        out[f'short_unit_months_{k}'] = sum(short[k, t].value() for t in range(T))
        out[f'idle_unit_months_{k}'] = sum(idle[k, t].value() for t in range(T))
    out['stranded_capital_expected'] = sum(p[k] * IDLE_COST * out[f'idle_unit_months_{k}'] for k in SCENARIOS)
    return out


def run(solver=None):
    sweep = [solve(None, solver)] + [solve(h, solver) for h in (0.0, 0.05, 0.10, 0.15, 0.20, 0.25)]
    return sweep


if __name__ == '__main__':
    for r in run():
        h = 'optimal' if r['headroom'] is None else f"{r['headroom']:.0%} headroom"
        print(f"{h:>14} | {r['status']} | exp cost ${r['expected_cost']/1e6:,.1f}M | blocks {r['blocks_ordered']:>2} | "
              f"cap-out months H/B/L {r['capacity_out_months_High']}/{r['capacity_out_months_Base']}/{r['capacity_out_months_Low']} | "
              f"stranded ${r['stranded_capital_expected']/1e6:,.1f}M")
