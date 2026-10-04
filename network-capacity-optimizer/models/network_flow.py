"""Model 1 — Peak network & carrier allocation (MILP).

Decision: how many units each fulfillment node ships to each demand zone, by which carrier,
and how many surge-capacity blocks to open at each node for peak week.
Objective: minimize shipping cost + surge cost + lost margin on unmet demand.
Constraints: demand balance, node capacity (+ surge), carrier capacity per node,
delivery promise (only lanes that meet the promise are allowed).

All data is synthetic. Shape (nodes, zones, carriers, peak scenarios) mirrors a mid-size
e-commerce fulfillment network.
"""
import math
import re
import pulp


def sid(s):
    return re.sub(r'\W+', '_', s).strip('_')

NODES = {  # name: (lat, lon, base weekly capacity in units)
    'FC West (Reno)':        (39.5, -119.8, 34000),
    'FC South (Dallas)':     (32.8,  -96.8, 30000),
    'FC Southeast (Atlanta)': (33.7, -84.4, 28000),
    'FC Central (Chicago)':  (41.9,  -87.6, 30000),
    'FC East (Allentown)':   (40.6,  -75.5, 32000),
    'FC Mountain (Denver)':  (39.7, -105.0, 16000),
}
ZONES = {  # name: (lat, lon, base peak-week demand)
    'Pacific NW':   (47.6, -122.3, 12000), 'California':  (36.8, -119.4, 26000),
    'Southwest':    (33.4, -112.1, 11000), 'Mountain':    (40.8, -111.9, 7000),
    'Texas':        (31.0,  -97.5, 21000), 'Midwest':     (41.6,  -88.0, 22000),
    'Southeast':    (33.5,  -84.5, 17000), 'Florida':     (28.0,  -81.7, 15000),
    'Northeast':    (42.4,  -71.4, 19000), 'Mid-Atlantic': (39.9, -75.2, 20000),
}
CARRIERS = {  # name: (cost per unit = a + b*miles, transit days fn, share of node capacity it can carry)
    'Ground':   (3.0, 0.0040, lambda d: 1 + math.ceil(d / 450), 0.65),
    'Express':  (7.0, 0.0090, lambda d: max(1, math.ceil(d / 1100)), 0.30),
    'Regional': (3.5, 0.0030, lambda d: 1 if d < 300 else (2 if d < 650 else 99), 0.35),
}
SCENARIOS = {'Base peak': 1.00, 'High peak': 1.20, 'Stress peak': 1.38}
PROMISE_DAYS = 3
SURGE_BLOCK_UNITS, SURGE_BLOCK_COST, MAX_BLOCKS = 4000, 30000, 3
LOST_MARGIN = 22.0  # $ per unit of unmet demand


def miles(a, b):
    (la1, lo1), (la2, lo2) = a, b
    p = math.pi / 180
    h = math.sin((la2 - la1) * p / 2) ** 2 + math.cos(la1 * p) * math.cos(la2 * p) * math.sin((lo2 - lo1) * p / 2) ** 2
    return 3959 * 2 * math.asin(math.sqrt(h))


def lanes():
    out = {}
    for n, (nla, nlo, _) in NODES.items():
        for z, (zla, zlo, _) in ZONES.items():
            d = miles((nla, nlo), (zla, zlo))
            for c, (a, b, days, _) in CARRIERS.items():
                t = days(d)
                if t <= PROMISE_DAYS:
                    out[(n, z, c)] = dict(miles=round(d), days=t, cost=round(a + b * d, 2))
    return out


def solve(scenario='Base peak', solver=None, fixed_blocks=None):
    mult = SCENARIOS[scenario]
    L = lanes()
    demand = {z: v[2] * mult for z, v in ZONES.items()}
    m = pulp.LpProblem('peak_network', pulp.LpMinimize)
    x = pulp.LpVariable.dicts('ship', L.keys(), lowBound=0)
    if fixed_blocks is None:
        y = pulp.LpVariable.dicts('surge', NODES.keys(), lowBound=0, upBound=MAX_BLOCKS, cat='Integer')
    else:
        y = fixed_blocks
    u = pulp.LpVariable.dicts('unmet', ZONES.keys(), lowBound=0)

    m += (pulp.lpSum(L[k]['cost'] * x[k] for k in L)
          + pulp.lpSum(SURGE_BLOCK_COST * y[n] for n in NODES)
          + pulp.lpSum(LOST_MARGIN * u[z] for z in ZONES))
    for z in ZONES:
        m += pulp.lpSum(x[k] for k in L if k[1] == z) + u[z] == demand[z], f'demand_{sid(z)}'
    for n, (_, _, cap) in NODES.items():
        m += pulp.lpSum(x[k] for k in L if k[0] == n) <= cap + SURGE_BLOCK_UNITS * y[n], f'nodecap_{sid(n)}'
        for c, (_, _, _, share) in CARRIERS.items():
            m += pulp.lpSum(x[k] for k in L if k[0] == n and k[2] == c) <= share * cap, f'carrier_{sid(n)}_{c}'
    m.solve(solver or pulp.PULP_CBC_CMD(msg=False))

    val = lambda v: v.value() if hasattr(v, 'value') else v
    ship = {k: x[k].value() for k in L if x[k].value() and x[k].value() > 0.5}
    blocks = {n: round(val(y[n])) for n in NODES}
    unmet = {z: u[z].value() for z in ZONES}
    tot_d = sum(demand.values())
    res = dict(
        scenario=scenario, status=pulp.LpStatus[m.status], total_cost=pulp.value(m.objective),
        shipping_cost=sum(L[k]['cost'] * v for k, v in ship.items()),
        surge_cost=sum(SURGE_BLOCK_COST * b for b in blocks.values()),
        lost_margin=sum(LOST_MARGIN * v for v in unmet.values()),
        demand=tot_d, fill_rate=1 - sum(unmet.values()) / tot_d, surge_blocks=blocks,
        utilization={n: sum(v for k, v in ship.items() if k[0] == n) / (NODES[n][2] + SURGE_BLOCK_UNITS * blocks[n])
                     for n in NODES},
        carrier_mix={c: sum(v for k, v in ship.items() if k[2] == c) / max(1, sum(ship.values())) for c in CARRIERS},
        unmet={z: v for z, v in unmet.items() if v > 0.5},
    )
    if fixed_blocks is not None:  # LP: shadow price of node capacity = value of one more unit of capacity
        res['capacity_shadow_price'] = {n: -m.constraints[f'nodecap_{sid(n)}'].pi for n in NODES}
    return res


def run(solver=None):
    results = []
    for s in SCENARIOS:
        r = solve(s, solver)
        lp = solve(s, pulp.PULP_CBC_CMD(msg=False), fixed_blocks=r['surge_blocks'])  # LP re-solve with surge fixed; CBC returns duals
        r['capacity_shadow_price'] = lp.get('capacity_shadow_price')
        results.append(r)
    return results


if __name__ == '__main__':
    for r in run():
        print(r['scenario'], r['status'], f"cost ${r['total_cost']:,.0f}", f"fill {r['fill_rate']:.1%}", r['surge_blocks'])
        print('   shadow $/unit:', {k.split(' (')[0]: round(v or 0, 2) for k, v in r['capacity_shadow_price'].items()})
