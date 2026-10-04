"""Model 3 — Constrained supply allocation (LP).

Decision: how to split short supply (30% below demand) across channels.
Objective: maximize contribution margin.
Constraints: total allocation <= supply; each channel <= its demand; each channel >= a
contractual / strategic fill floor.
The shadow price on the supply constraint says what one more unit of supply is worth;
the shadow price on each floor says what that commitment costs.

Same model ships as an Excel Solver workbook (excel/constrained_allocation_solver.xlsx).
All data is synthetic.
"""
import pulp

SUPPLY = 7000
CHANNELS = {  # name: (demand, margin $/unit, fill floor)
    'Flagship Retail':  (3000, 42, 1.00),
    'Big-Box Retail':   (2500, 35, 0.85),
    'Online Direct':    (2000, 48, 0.50),
    'Education B2B':    (1500, 30, 0.50),
    'Distributors':     (1000, 22, 0.00),
}


def solve(supply=SUPPLY, floors=True, solver=None):
    m = pulp.LpProblem('allocation', pulp.LpMaximize)
    key = {c: c.replace(' ', '_').replace('-', '_') for c in CHANNELS}
    x = {c: pulp.LpVariable(f'alloc_{key[c]}', lowBound=0, upBound=CHANNELS[c][0]) for c in CHANNELS}
    m += pulp.lpSum(CHANNELS[c][1] * x[c] for c in CHANNELS)
    m += pulp.lpSum(x.values()) <= supply, 'supply'
    if floors:
        for c, (d, _, f) in CHANNELS.items():
            m += x[c] >= f * d, f'floor_{key[c]}'
    m.solve(solver or pulp.PULP_CBC_CMD(msg=False))
    return dict(
        status=pulp.LpStatus[m.status], margin=pulp.value(m.objective),
        allocation={c: x[c].value() for c in CHANNELS},
        fill={c: x[c].value() / CHANNELS[c][0] for c in CHANNELS},
        supply_shadow_price=m.constraints['supply'].pi,
        floor_cost={c: -(m.constraints[f'floor_{key[c]}'].pi or 0) for c in CHANNELS} if floors else {},
    )


def run(solver=None):
    base = solve(solver=pulp.PULP_CBC_CMD(msg=False))  # CBC returns duals (shadow prices)
    check = solve(solver=solver)
    assert abs(check['margin'] - base['margin']) < 1e-6, 'solvers disagree'
    no_floor = solve(floors=False, solver=solver)
    plus = solve(supply=SUPPLY + 500, solver=solver)
    return dict(base=base, no_floors=no_floor, plus_500=plus,
                cost_of_commitments=no_floor['margin'] - base['margin'],
                value_of_500_more=plus['margin'] - base['margin'])


if __name__ == '__main__':
    r = run()
    b = r['base']
    print(b['status'], f"margin ${b['margin']:,.0f}", {k: f"{v:.0%}" for k, v in b['fill'].items()})
    print('value of 1 more unit $', round(b['supply_shadow_price'], 2), '| floor cost $/unit', {k: round(v, 2) for k, v in b['floor_cost'].items()})
    print('cost of commitments $', round(r['cost_of_commitments']), '| value of +500 units $', round(r['value_of_500_more']))
