"""Unexecuted SD-01 equation implementation. No runner or control defaults.

The preparation path never imports this module. A future audited runner must
bind complete controls, the frozen numerical environment, and authorization
before calling any function here. This module alone is not execution-ready.
"""
from fractions import Fraction
import math


def parameter(numerator, denominator=1):
    return float(Fraction(numerator, denominator))


def regeneration(x, source, rho):
    # Preserve written left-associative binary64 operation order.
    base = (rho * x) * (1.0 - x / 20.0)
    if source == 'logistic':
        return base
    if source == 'allee':
        return base * (x / 5.0 - 1.0)
    raise ValueError('unknown frozen source')


def shock(after_regeneration, tick, schedule):
    if schedule not in ('none', 'adversarial'):
        raise ValueError('unknown frozen shock schedule')
    return min(4.0, max(0.0, after_regeneration)) if schedule == 'adversarial' and tick in (2500, 5000, 10000, 15000) else 0.0


def action_menu(demand):
    # M is a set; zero-demand duplicates must collapse.
    return tuple(sorted({0.0, demand / 4.0, demand / 2.0, (3.0 * demand) / 4.0, demand}))


def h1_branch(y, q, demand, source, rho):
    pre = (y + regeneration(y, source, rho)) - q
    actions = tuple(v for v in action_menu(demand) if pre >= 5.0 and 0.0 <= v <= demand and 5.0 <= pre - v <= 20.0)
    return {'pre': pre, 'actions': actions, 'pre_reserve': pre >= 5.0}


def select_action(pre, demand, policy, eta, source, rho):
    if policy == 'H0' and eta is None:
        return min(demand, max(0.0, pre)), None
    if policy == 'H1' and eta is None:
        return min(demand, max(0.0, pre - 5.0)), None
    if policy == 'H2' and eta in (parameter(1, 2), parameter(9, 10), 1.0):
        return eta * min(demand, max(0.0, pre - 5.0)), None
    if policy != 'H3' or eta is not None:
        raise ValueError('unknown frozen policy or eta')
    branches = []
    for u in action_menu(demand):
        y = pre - u
        q1 = min(4.0, max(0.0, y + regeneration(y, source, rho)))
        no_shock = h1_branch(y, 0.0, demand, source, rho)
        adversarial = h1_branch(y, q1, demand, source, rho)
        branches.append({'action': u, 'post': y, 'current_post_reserve': y >= 5.0,
                         'no_shock': no_shock, 'adversarial': adversarial,
                         'admissible': 5.0 <= y <= 20.0 and bool(no_shock['actions']) and bool(adversarial['actions'])})
    current = tuple(row['action'] for row in branches if row['admissible'])
    # Undefined action is retained; a zero-service fallback is forbidden.
    return (max(current) if current else None), {'current': current, 'branches': branches}


def transition(x, tick, *, source, rho, demand, schedule, policy, eta=None):
    """Future single transition only; never called during preparation validation."""
    growth = regeneration(x, source, rho)
    regenerated = x + growth
    if not all(math.isfinite(v) for v in (x, growth, regenerated)):
        return {'terminal': 'NONFINITE_STATE', 'x': x, 'growth': growth}
    outflow = shock(regenerated, tick, schedule)
    pre = regenerated - outflow
    u, sets = select_action(pre, demand, policy, eta, source, rho)
    if u is None:
        return {'terminal': 'RECURSIVE_FEASIBILITY_FAILURE_UNDEFINED_EVOLUTION',
                'x': x, 'growth': growth, 'shock': outflow, 'pre': pre, 'sets': sets}
    following = pre - u
    residual = (((x + growth) - outflow) - u) - following
    tolerance = parameter(1, 10**12) * max(1.0, abs(x) + abs(growth) + abs(outflow) + abs(u) + abs(following))
    return {'terminal': None if math.isfinite(following) and abs(residual) <= tolerance else 'NUMERICAL_OR_CONSERVATION_FAILURE',
            'x': x, 'growth': growth, 'shock': outflow, 'pre': pre, 'served': u,
            'unmet': demand - u, 'next_x': following, 'reserve_margin': max(0.0, following - 5.0),
            'post_state_in_viability_set': (0.0 if policy == 'H0' else 5.0) <= following <= 20.0,
            'pre_and_post_reserve': x >= 5.0 and following >= 5.0,
            'residual': residual, 'sets': sets}
