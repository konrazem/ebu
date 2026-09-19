"""Exact rational checks of explicitly written teaching states, never a model run.

This file imports only standard-library arithmetic. It neither imports EBU
runtime modules nor applies a model action, step, tick, campaign, or trajectory.
All before/after vectors below are literals copied from the manuscript.
"""

from fractions import Fraction as Q


checks = []


def rational_vector(values):
    return tuple(Q(value) for value in values)


def potential(state, reference, scales):
    x, ref, scale = map(rational_vector, (state, reference, scales))
    assert len(x) == len(ref) == len(scale)
    assert all(s > 0 for s in scale)
    return sum(((a - b) / s) ** 2 / 2 for a, b, s in zip(x, ref, scale))


def field_difference(before, after, reference, scales):
    return potential(before, reference, scales) - potential(after, reference, scales)


def attribution(baseline, child, group, reference, scales):
    z, child, group, ref, scales = map(
        rational_vector, (baseline, child, group, reference, scales)
    )
    return sum(
        -(a - b) * d / s**2 - d * g / (2 * s**2)
        for a, b, s, d, g in zip(z, ref, scales, child, group)
    )


def check(name, actual, expected):
    expected = Q(expected)
    assert actual == expected, (name, actual, expected)
    checks.append((name, str(actual)))


base_ref = (10, 10)
base_scales = (2, 2)
base = (18, 2)
check("base mass", sum(base), 20)
check("base potential", potential(base, base_ref, base_scales), 16)
for label, state, expected in (
    ("q0", (18, 2), 16),
    ("q1", (17, 3), "12.25"),
    ("q2", (16, 4), 9),
    ("q3", (15, 5), "6.25"),
    ("q4", (14, 6), 4),
    ("q5", (13, 7), "2.25"),
    ("q6", (12, 8), 1),
    ("q8", (10, 10), 0),
    ("q12", (6, 14), 4),
    ("q16", (2, 18), 16),
    ("q17", (1, 19), "20.25"),
    ("one away", (11, 9), "0.25"),
    ("endpoint", (0, 20), 25),
):
    check(f"potential {label}", potential(state, base_ref, base_scales), expected)
    check(f"conservation {label}", sum(state), 20)

for q, expected in ((0, 0), (1, "3.75"), (2, 7), (3, "9.75"), (4, 12),
                    (5, "13.75"), (6, 15), (8, 16), (12, 12), (16, 0),
                    (17, "-4.25")):
    check(f"finite formula q{q}", 4 * Q(q) - Q(q) ** 2 / 4, expected)

check("changed scales initial", potential(base, base_ref, (4, 2)), 10)
check("changed scales after", potential((14, 6), base_ref, (4, 2)), "2.5")
check("changed scales field", field_difference(base, (14, 6), base_ref, (4, 2)), "7.5")
check("narrow source scale", potential(base, base_ref, (1, 2)), 40)
check("reference 12,8 initial", potential(base, (12, 8), base_scales), 9)
check("reference 12,8 after", potential((14, 6), (12, 8), base_scales), 1)
check("reference 14,6 initial", potential(base, (14, 6), base_scales), 4)
check("three equal stocks", potential((8, 8, 8), (10, 6, 8), (2, 2, 2)), 1)
check("three unequal scales", potential((8, 8, 8), (10, 6, 8), (4, 2, 2)), "0.625")
check("external first improvement", field_difference((18, 2), (17, 3), base_ref, base_scales), "3.75")
check("post-forcing actor", field_difference((17, 3), (13, 7), base_ref, base_scales), 10)
check("new baseline q2", field_difference((16, 4), (14, 6), base_ref, base_scales), 5)
check("new baseline q4", field_difference((16, 4), (12, 8), base_ref, base_scales), 8)
check("reference departure", field_difference((10, 10), (8, 12), base_ref, base_scales), -1)
check("last unit live", field_difference((15, 5), (14, 6), base_ref, base_scales), "2.25")
check("midpoint unequal-scale", (Q("2.5") - Q(5, 16) * 2) * 4, "7.5")

route_ref, route_scales = (6, 0, 6), (2, 2, 2)
route_start, route_hub, route_final = (10, 0, 2), (5, 5, 2), (5, 1, 6)
check("route initial", potential(route_start, route_ref, route_scales), 4)
check("route hub", potential(route_hub, route_ref, route_scales), "5.25")
check("route final", potential(route_final, route_ref, route_scales), "0.25")
e1 = field_difference(route_start, route_hub, route_ref, route_scales)
e2 = field_difference(route_hub, route_final, route_ref, route_scales)
check("route first receipt", e1, "-1.25")
check("route second receipt", e2, 5)
check("route telescope", e1 + e2, "3.75")
check("route burdens .2,.3", e1 + e2 - Q(".2") - Q(".3"), "3.25")
check("route variant final", potential((5, 2, 5), route_ref, route_scales), ".75")
check("route variant second", field_difference(route_hub, (5, 2, 5), route_ref, route_scales), "4.5")
check("route variant total", field_difference(route_start, (5, 2, 5), route_ref, route_scales), "3.25")
check("route alternate intermediate", potential((6, 4, 2), route_ref, route_scales), 4)
check("route alternate endpoint", potential((6, 0, 6), route_ref, route_scales), 0)
check("route intervening external", potential((6, 4, 2), route_ref, route_scales) - potential(route_hub, route_ref, route_scales), "-1.25")
check("route external actor sum", e1 + field_difference((6, 4, 2), (6, 0, 6), route_ref, route_scales), "2.75")

check("equal group child", attribution(base, (-2, 2), (-4, 4), base_ref, base_scales), 6)
check("one-unit group child", attribution(base, (-1, 1), (-2, 2), base_ref, base_scales), "3.5")
check("one-plus-three child A", attribution(base, (-1, 1), (-4, 4), base_ref, base_scales), 3)
check("one-plus-three child B", attribution(base, (-3, 3), (-4, 4), base_ref, base_scales), 9)
check("opposing child A", attribution(base, (-2, 2), (0, 0), base_ref, base_scales), 8)
check("opposing child B", attribution(base, (2, -2), (0, 0), base_ref, base_scales), -8)
check("opposing standalone B", field_difference(base, (20, 0), base_ref, base_scales), -9)

group_z, group_ref, group_scales = (18, 2, 10), (10, 10, 10), (2, 2, 2)
check("unequal group endpoint", potential((12, 6, 12), group_ref, group_scales), 3)
check("unequal group total", field_difference(group_z, (12, 6, 12), group_ref, group_scales), 13)
check("unequal standalone A", field_difference(group_z, (14, 6, 10), group_ref, group_scales), 12)
check("unequal standalone B", field_difference(group_z, (16, 2, 12), group_ref, group_scales), 3)
check("unequal path A", attribution(group_z, (-4, 4, 0), (-6, 4, 2), group_ref, group_scales), 11)
check("unequal path B", attribution(group_z, (-2, 0, 2), (-6, 4, 2), group_ref, group_scales), 2)
check("unequal split child", attribution(group_z, (-2, 2, 0), (-6, 4, 2), group_ref, group_scales), "5.5")
check("A first then B", field_difference((14, 6, 10), (12, 6, 12), group_ref, group_scales), 1)
check("B first then A", field_difference((16, 2, 12), (12, 6, 12), group_ref, group_scales), 10)
check("group process sum", 13 - Q(".5") - Q(".25"), "12.25")

check("reconstruction potential", potential(("13.5", "6.5"), base_ref, base_scales), "3.0625")
check("reconstruction value", field_difference((17, 3), ("13.5", "6.5"), base_ref, base_scales), "9.1875")
check("unperformed half unit", field_difference(("13.5", "6.5"), (13, 7), base_ref, base_scales), ".8125")
check("half unit derivative", Q("1.75") * Q(".5") - Q(".5") ** 2 / 4, ".8125")
check("complete signed account", 4 + 12 - 16, 0)
check("energy conversion", Q(".3") + Q(".7"), 1)
check("energy delivery", Q(".24") + Q(".06"), ".3")
check("final heat account", Q(".7") + Q(".06") + Q(".24"), 1)

print(f"{len(checks)} exact rational arithmetic checks passed.")
print("Scope: explicit manuscript states and formulas only; no model imports or state advancement.")
for name, value in checks:
    print(f"{name}: {value}")
