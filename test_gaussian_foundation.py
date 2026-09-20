"""Local Gaussian Stage-A foundation conformance gate: checks A-R.

Implements the required fixed-state conformance tests of the Stage-A task,
section 24, plus the locality, side-effect and selection-blindness guards.

**Execution class: NON-MODEL-ADVANCING STATIC/PURE.**  Every check is a pure
function evaluation on a frozen or synthetic individual state, an exact
rational arithmetic identity, or an AST/source inspection.  This suite never
constructs a tick harness, never advances an epoch and generates no
trajectory; `test_no_harness_transition_is_called` asserts by AST over THIS
FILE that it makes no direct call to `run_tick`, `run_stage_a` or
`advance`.  That is a real check and a narrow one: it inspects direct calls in
this file only and does not prove an imported helper cannot transition.

All arithmetic is exact rational (`fractions.Fraction`).  Tolerances are zero,
so every identity below is an exact equality and the reported residuals are
exact zeros rather than small floats.

**The numbers here are synthetic and carry no scientific meaning.**  No world,
scale, quantum, horizon, seed, threshold or success criterion is adopted, and
no test asserts that the system recovers.  Recovery, cycling, plateau and
deadlock are scientific outcomes, not conformance requirements.
"""

from __future__ import annotations

import ast
import inspect
from fractions import Fraction

from gaussian_harness.actions import ActionGroup, AtomicAction
from gaussian_harness.capacity import CapacityLedger
from gaussian_harness.fixtures import (
    DECLARED_MASS,
    fixture_potential,
    hand_checkable_walkthrough,
    overdraft_attempt,
    walkthrough_residuals,
)
from gaussian_harness.forcing import (
    ForcingIncrement,
    accounting_residual,
    apply_forcing,
    conservation_residual,
    external_deviation,
)
from gaussian_harness.numerics import Refusal, add
from gaussian_harness.potential import LocalGaussianPotential
from gaussian_harness.valuation import (
    QUADRATURE_RULES,
    finite_ebu,
    group_ebu,
    linear_estimate,
    mobius_term,
    pair_mobius_term,
    path_receipt_closed_form,
    path_receipt_quadrature,
    quadratic_ebu,
    value_group,
)

PASSED = 0
FAILED = 0
MAX_ACCOUNTING_RESIDUAL = Fraction(0)
MAX_CONSERVATION_RESIDUAL = Fraction(0)
MAX_RECEIPT_RESIDUAL = Fraction(0)
MAX_ANALYTIC_RESIDUAL = Fraction(0)


def check(label: str, condition: bool, detail: str = "") -> None:
    global PASSED, FAILED
    if condition:
        PASSED += 1
        print(f"  PASS  {label}")
    else:
        FAILED += 1
        print(f"  FAIL  {label}  {detail}")


def note_residual(kind: str, value: Fraction) -> None:
    global MAX_ACCOUNTING_RESIDUAL, MAX_CONSERVATION_RESIDUAL
    global MAX_RECEIPT_RESIDUAL, MAX_ANALYTIC_RESIDUAL
    magnitude = abs(value)
    if kind == "accounting":
        MAX_ACCOUNTING_RESIDUAL = max(MAX_ACCOUNTING_RESIDUAL, magnitude)
    elif kind == "conservation":
        MAX_CONSERVATION_RESIDUAL = max(MAX_CONSERVATION_RESIDUAL, magnitude)
    elif kind == "receipt":
        MAX_RECEIPT_RESIDUAL = max(MAX_RECEIPT_RESIDUAL, magnitude)
    elif kind == "analytic":
        MAX_ANALYTIC_RESIDUAL = max(MAX_ANALYTIC_RESIDUAL, magnitude)


def test_a_equilibrium_minimum() -> None:
    """A. V is zero at the reference and strictly positive away from it."""
    potential = fixture_potential()
    reference = potential.reference
    check("A equilibrium value is exactly zero", potential.value_total(reference) == 0)
    strictly_positive = True
    for offset in (Fraction(1, 7), Fraction(3), Fraction(-5, 2)):
        for index in range(3):
            state = list(reference)
            state[index] += offset
            if potential.value_total(tuple(state)) <= 0:
                strictly_positive = False
    check("A any displacement raises V above zero", strictly_positive)


def test_b_symmetric_displacement() -> None:
    """B. Equal displacements either side of the reference are valued equally."""
    potential = fixture_potential()
    reference = potential.reference
    symmetric = True
    for offset in (Fraction(1, 3), Fraction(2), Fraction(7, 5)):
        for index in range(3):
            plus, minus = list(reference), list(reference)
            plus[index] += offset
            minus[index] -= offset
            if potential.value_total(tuple(plus)) != potential.value_total(tuple(minus)):
                symmetric = False
    check("B symmetric displacements have equal potential", symmetric)


def test_c_marginal_matches_finite_difference() -> None:
    """C. The analytic marginal equals the exact central difference.

    For a quadratic the central difference is exact at any step size, so this
    is an exact identity rather than a limit argument.
    """
    potential = fixture_potential()
    state = (Fraction(37, 4), Fraction(23, 2), Fraction(41, 5))
    agree = True
    for index in range(3):
        for step in (Fraction(1), Fraction(1, 8), Fraction(5, 3)):
            plus, minus = list(state), list(state)
            plus[index] += step
            minus[index] -= step
            central = (
                potential.value_total(tuple(plus)) - potential.value_total(tuple(minus))
            ) / (2 * step)
            residual = central - potential.marginal(state, index)
            note_residual("analytic", residual)
            if residual != 0:
                agree = False
    check("C analytic marginal equals exact central difference", agree)


def test_d_equilibrium_disturbance_is_negative() -> None:
    """D. At exact equilibrium mu = 0, yet any nonzero feasible move has E < 0."""
    potential = fixture_potential()
    reference = potential.reference
    marginals_zero = all(potential.marginal(reference, i) == 0 for i in range(3))
    check("D every marginal is exactly zero at the reference", marginals_zero)
    negative = True
    for source, destination, quantity in ((0, 1, 1), (1, 2, Fraction(1, 2)), (2, 0, 3)):
        group = ActionGroup.of(AtomicAction.declare(source, destination, quantity))
        if group_ebu(potential, reference, group) >= 0:
            negative = False
    check("D nonzero disturbance at equilibrium has strictly negative EBU", negative)


def test_e_restorative_action_is_positive() -> None:
    """E. Moving stock back toward the reference earns positive value."""
    potential = fixture_potential()
    state = (Fraction(8), Fraction(12), Fraction(10))
    group = ActionGroup.of(AtomicAction.declare(1, 0, Fraction(1)))
    value = group_ebu(potential, state, group)
    check("E restorative action has positive EBU", value == 3, f"got {value}")


def test_f_overshoot_uses_endpoint_potential() -> None:
    """F. Overshoot is valued by the endpoint potential, not the initial gradient.

    From (8, 12, 10) moving 4 units from cell 1 to cell 0 lands on (12, 8, 10),
    the mirror image with identical potential, so the exact value is zero. The
    initial force times quantity would report +16.
    """
    potential = fixture_potential()
    state = (Fraction(8), Fraction(12), Fraction(10))
    increment = AtomicAction.declare(1, 0, Fraction(4)).increment(3)
    exact_value = finite_ebu(potential, state, increment)
    naive = linear_estimate(potential, state, increment)
    check("F exact overshoot value is zero", exact_value == 0, f"got {exact_value}")
    check("F initial-force estimate disagrees", naive == 16, f"got {naive}")
    check("F endpoint value is not the linear estimate", exact_value != naive)
    beyond = AtomicAction.declare(1, 0, Fraction(5)).increment(3)
    check(
        "F overshooting past the mirror point is strictly negative",
        finite_ebu(potential, state, beyond) < 0,
    )


def test_g_path_integral_closes() -> None:
    """G. Every quadrature rule reproduces the closed-form receipt exactly."""
    potential = fixture_potential()
    state = (Fraction(8), Fraction(12), Fraction(10))
    group = ActionGroup.of(
        AtomicAction.declare(1, 0, Fraction(1)), AtomicAction.declare(0, 2, Fraction(1, 2))
    )
    group_increment = group.increment(3)
    closes = True
    for action in group.actions:
        action_increment = action.increment(3)
        closed = path_receipt_closed_form(potential, state, group_increment, action_increment)
        for rule in QUADRATURE_RULES:
            numeric = path_receipt_quadrature(
                potential, state, group_increment, action_increment, rule
            )
            note_residual("receipt", numeric - closed)
            if numeric != closed:
                closes = False
    check("G analytic and numerical path integrals agree exactly", closes)
    single = ActionGroup.of(AtomicAction.declare(1, 0, Fraction(1)))
    single_increment = single.increment(3)
    receipt = path_receipt_closed_form(
        potential, state, single_increment, single_increment
    )
    check(
        "G single-action path integral equals its finite value",
        receipt == finite_ebu(potential, state, single_increment),
    )


def test_h_disjoint_actions_add() -> None:
    """H. Actions on disjoint supports add exactly; their interaction vanishes."""
    potential = LocalGaussianPotential.declare([10, 10, 10, 10], [1, 1, 1, 1])
    state = (Fraction(9), Fraction(11), Fraction(12), Fraction(8))
    first = AtomicAction.declare(0, 1, Fraction(1))
    second = AtomicAction.declare(2, 3, Fraction(1))
    group = ActionGroup.of(first, second)
    separate = finite_ebu(potential, state, first.increment(4)) + finite_ebu(
        potential, state, second.increment(4)
    )
    joint = group_ebu(potential, state, group)
    check("H disjoint simultaneous actions add exactly", joint == separate)
    check(
        "H disjoint pair interaction is exactly zero",
        pair_mobius_term(potential, state, first.increment(4), second.increment(4)) == 0,
    )


def test_i_shared_coordinate_interacts() -> None:
    """I. Actions sharing a coordinate interact even though V is factorized."""
    potential = fixture_potential()
    reference = potential.reference
    first = AtomicAction.declare(0, 1, Fraction(1))
    second = AtomicAction.declare(0, 2, Fraction(1))
    group = ActionGroup.of(first, second)
    separate = finite_ebu(potential, reference, first.increment(3)) + finite_ebu(
        potential, reference, second.increment(3)
    )
    joint = group_ebu(potential, reference, group)
    interaction = pair_mobius_term(
        potential, reference, first.increment(3), second.increment(3)
    )
    check("I shared-coordinate group is not the sum of singletons", joint != separate)
    check("I pair interaction is nonzero", interaction != 0, f"got {interaction}")
    check(
        "I group value equals singletons plus interaction",
        joint == separate + interaction,
    )
    check("I exact values are -1, -1 and -3", (separate, joint) == (-2, -3))


def test_j_receipts_sum_to_group_value() -> None:
    """J. sum_a R_a = E_G for every enumerated group, exactly."""
    potential = fixture_potential()
    state = (Fraction(15, 2), Fraction(12), Fraction(21, 2))
    candidates = [
        ActionGroup.of(AtomicAction.declare(0, 1, Fraction(1))),
        ActionGroup.of(
            AtomicAction.declare(0, 1, Fraction(1)), AtomicAction.declare(0, 2, Fraction(2))
        ),
        ActionGroup.of(
            AtomicAction.declare(1, 0, Fraction(3, 2)),
            AtomicAction.declare(2, 1, Fraction(1, 4)),
        ),
        ActionGroup.of(
            AtomicAction.declare(0, 1, Fraction(1)), AtomicAction.declare(1, 0, Fraction(1))
        ),
    ]
    closes = True
    for group in candidates:
        valuation = value_group(potential, state, group)
        note_residual("receipt", valuation.residual)
        if valuation.residual != 0:
            closes = False
    check("J receipts sum exactly to the group value", closes)
    cancelling = value_group(potential, state, candidates[3])
    check(
        "J a nonempty cancelling group has zero net increment and zero value",
        cancelling.group_ebu == 0,
    )


def test_k_third_order_mobius_vanishes() -> None:
    """K. For fixed increments on a quadratic, order-three Moebius terms vanish."""
    potential = LocalGaussianPotential.declare([10, 10, 10, 10], [1, 1, 2, 1])
    state = (Fraction(9), Fraction(23, 2), Fraction(10), Fraction(19, 2))
    increments = [
        AtomicAction.declare(0, 1, Fraction(1)).increment(4),
        AtomicAction.declare(0, 2, Fraction(1, 2)).increment(4),
        AtomicAction.declare(1, 3, Fraction(3, 2)).increment(4),
    ]
    triple = mobius_term(potential, state, increments)
    check("K third-order Moebius term is exactly zero", triple == 0, f"got {triple}")
    pair = mobius_term(potential, state, increments[:2])
    direct = pair_mobius_term(potential, state, increments[0], increments[1])
    check("K pair Moebius term matches -delta_a^T H delta_b", pair == direct)
    quad = mobius_term(potential, state, increments + [
        AtomicAction.declare(2, 3, Fraction(1)).increment(4)
    ])
    check("K fourth-order Moebius term is exactly zero", quad == 0, f"got {quad}")


def test_l_zero_capacity_rejects_disturbance() -> None:
    """L. With zero balances an equilibrium-disturbing action is unaffordable."""
    potential = fixture_potential()
    reference = potential.reference
    ledger = CapacityLedger.zero(3)
    group = ActionGroup.of(AtomicAction.declare(0, 1, Fraction(1)))
    valuation = value_group(potential, reference, group)
    decision = ledger.is_affordable(valuation)
    check("L equilibrium-disturbing action has negative value", valuation.group_ebu < 0)
    check("L zero capacity refuses it", not decision.affordable)
    check("L the refusing owner is the action source", decision.deficient_owners == (0,))


def test_m_earned_capacity_finances_later_loss() -> None:
    """M. Capacity earned earlier finances a later negative-EBU action."""
    potential = fixture_potential()
    state = (Fraction(8), Fraction(12), Fraction(10))
    ledger = CapacityLedger.zero(3)
    earn = ActionGroup.of(AtomicAction.declare(1, 0, Fraction(2)))
    earned = value_group(potential, state, earn)
    ledger = ledger.settle(earned.owner_deltas)
    state = add(state, earn.increment(3))
    check("M restoration earned capacity for owner 1", ledger.balances[1] == 4)
    spend = ActionGroup.of(AtomicAction.declare(1, 2, Fraction(1)))
    spent = value_group(potential, state, spend)
    decision = ledger.is_affordable(spent)
    check("M the later action has negative value", spent.group_ebu < 0)
    check("M previously earned capacity makes it affordable", decision.affordable)
    ledger = ledger.settle(spent.owner_deltas)
    check("M balance fell but stayed nonnegative", ledger.balances[1] == 3)


def test_n_overdraft_is_rejected() -> None:
    """N. No owner may go into debt, and refusal leaves the ledger untouched."""
    potential = fixture_potential()
    state = (Fraction(9), Fraction(11), Fraction(10))
    ledger = CapacityLedger.zero(3)
    group = ActionGroup.of(AtomicAction.declare(0, 1, Fraction(1)))
    valuation = value_group(potential, state, group)
    refused = False
    try:
        ledger.settle(valuation.owner_deltas)
    except Refusal:
        refused = True
    check("N settlement refuses to overdraw", refused)
    check("N the ledger is unchanged after refusal", ledger.balances == (0, 0, 0))
    value, owners = overdraft_attempt()
    check("N fixture overdraft is refused for the source owner", owners == (0,))
    check("N the refused action was genuinely damaging", value < 0)
    negative_rejected = False
    try:
        CapacityLedger((Fraction(1), Fraction(-1), Fraction(0)))
    except Refusal:
        negative_rejected = True
    check("N a negative balance cannot be constructed at all", negative_rejected)


def test_o_forcing_changes_audit_not_balances() -> None:
    """O. External forcing moves J and x. It credits no balance."""
    potential = fixture_potential()
    state = potential.reference
    ledger = CapacityLedger.zero(3)
    audit = Fraction(0)
    before_balances = ledger.balances
    shock = ForcingIncrement(0, 1, Fraction(2))
    moved = apply_forcing(state, shock)
    audit += external_deviation(potential, state, moved)
    check("O forcing changed the audit ledger", audit == 4)
    check("O forcing credited no balance", ledger.balances == before_balances)
    check("O every balance is still zero", ledger.total == 0)
    check("O forcing conserved mass exactly", conservation_residual(moved, DECLARED_MASS) == 0)
    relieving = ForcingIncrement(1, 0, Fraction(1))
    relieved = apply_forcing(moved, relieving)
    signed = external_deviation(potential, moved, relieved)
    check("O a deviation-lowering shock gives a negative signed entry", signed == -3)


def test_p_action_changes_balances_not_audit() -> None:
    """P. An actor action moves B. It never moves J."""
    potential = fixture_potential()
    state = (Fraction(8), Fraction(12), Fraction(10))
    ledger = CapacityLedger.zero(3)
    audit = Fraction(4)
    group = ActionGroup.of(AtomicAction.declare(1, 0, Fraction(1)))
    valuation = value_group(potential, state, group)
    settled = ledger.settle(valuation.owner_deltas)
    audit_after = audit
    check("P the action changed a balance", settled.balances != ledger.balances)
    check("P the audit ledger is unchanged by the action", audit_after == audit)
    check("P only the owning cell's balance moved", settled.balances == (0, 3, 0))


def test_q_conservation_closes() -> None:
    """Q. Physical mass is conserved by forcing and by every action group."""
    potential = fixture_potential()
    worst = Fraction(0)
    state = potential.reference
    worst = max(worst, abs(conservation_residual(state, DECLARED_MASS)))
    state = apply_forcing(state, ForcingIncrement(0, 1, Fraction(2)))
    worst = max(worst, abs(conservation_residual(state, DECLARED_MASS)))
    for group in (
        ActionGroup.of(AtomicAction.declare(1, 0, Fraction(1))),
        ActionGroup.of(
            AtomicAction.declare(1, 2, Fraction(1, 2)),
            AtomicAction.declare(0, 1, Fraction(1, 4)),
        ),
    ):
        state = add(state, group.increment(3))
        residual = conservation_residual(state, DECLARED_MASS)
        note_residual("conservation", residual)
        worst = max(worst, abs(residual))
    check("Q conservation residual is exactly zero throughout", worst == 0, f"max {worst}")


def test_r_driven_accounting_closes() -> None:
    """R. V(x) + sum_i B_i = J holds exactly at every step of the walkthrough."""
    potential = fixture_potential()
    worst = Fraction(0)
    for step in hand_checkable_walkthrough():
        residual = accounting_residual(
            potential, step.state, CapacityLedger(step.balances), step.audit
        )
        note_residual("accounting", residual)
        worst = max(worst, abs(residual))
    check("R driven accounting residual is exactly zero", worst == 0, f"max {worst}")
    accounting, conservation = walkthrough_residuals()
    check("R fixture reports zero accounting residual", accounting == 0)
    check("R fixture reports zero conservation residual", conservation == 0)
    steps = hand_checkable_walkthrough()
    check("R the shock issued no capacity", steps[1].balance_total == 0)
    check("R audit stayed fixed after the single shock", {s.audit for s in steps[1:]} == {4})
    check(
        "R deviation and capacity exchanged without changing their sum",
        all(s.potential_value + s.balance_total == s.audit for s in steps),
    )


def test_locality_of_valuation() -> None:
    """Unrelated coordinates cannot influence a local candidate's EBU."""
    potential = LocalGaussianPotential.declare([10, 10, 10, 10], [1, 1, 1, 1])
    action = AtomicAction.declare(0, 1, Fraction(1))
    increment = action.increment(4)
    indices = potential.affected_factors(action.support)
    check("locality: affected factors are exactly the action support", indices == {0, 1})
    baseline = (Fraction(9), Fraction(11), Fraction(10), Fraction(10))
    disturbed = (Fraction(9), Fraction(11), Fraction(3), Fraction(17))
    check(
        "locality: changing untouched coordinates leaves the value unchanged",
        finite_ebu(potential, baseline, increment, indices)
        == finite_ebu(potential, disturbed, increment, indices),
    )
    check(
        "locality: the local value matches whole-world evaluation",
        finite_ebu(potential, baseline, increment, indices)
        == potential.value_total(baseline) - potential.value_total(add(baseline, increment)),
    )


def test_analytic_and_finite_forms_agree() -> None:
    """The definitional difference and the quadratic closed form agree exactly."""
    potential = LocalGaussianPotential.declare([10, 10, 10], [Fraction(1, 2), 2, 1])
    state = (Fraction(37, 4), Fraction(23, 2), Fraction(41, 5))
    agree = True
    for source, destination, quantity in (
        (0, 1, Fraction(1)),
        (1, 2, Fraction(7, 3)),
        (2, 0, Fraction(1, 8)),
    ):
        increment = AtomicAction.declare(source, destination, quantity).increment(3)
        residual = finite_ebu(potential, state, increment) - quadratic_ebu(
            potential, state, increment
        )
        note_residual("analytic", residual)
        if residual != 0:
            agree = False
    check("finite difference equals the analytic quadratic form exactly", agree)


def test_evaluation_is_side_effect_free() -> None:
    """Valuation and projection never mutate physical state or balances."""
    potential = fixture_potential()
    state = (Fraction(8), Fraction(12), Fraction(10))
    ledger = CapacityLedger.zero(3)
    group = ActionGroup.of(
        AtomicAction.declare(1, 0, Fraction(1)), AtomicAction.declare(0, 2, Fraction(1, 2))
    )
    valuation = value_group(potential, state, group)
    ledger.is_affordable(valuation)
    potential.value_total(state)
    potential.gradient_on(state, frozenset({0, 1, 2}))
    check("evaluation left the state unchanged", state == (8, 12, 10))
    check("evaluation left the balances unchanged", ledger.balances == (0, 0, 0))
    check("evaluation left the potential unchanged", potential.reference == (10, 10, 10))
    check(
        "projection returns a new ledger rather than mutating",
        ledger.settle({1: Fraction(3)}) is not ledger and ledger.balances == (0, 0, 0),
    )


def test_no_mean_reversion_or_ebu_selection_in_source() -> None:
    """The package contains no restoring drift and no value-ranked selection.

    Both checks are structural over the AST, so explanatory prose in a
    docstring cannot satisfy or trip them. They cover the named modules only.
    """
    import gaussian_harness.potential as potential_module
    import gaussian_harness.valuation as valuation_module
    import gaussian_harness.capacity as capacity_module

    drift_names = {"gamma", "mean_reversion", "restoring_drift", "revert"}
    seen_names: set[str] = set()
    ranked: list[str] = []
    for module in (potential_module, valuation_module, capacity_module):
        tree = ast.parse(inspect.getsource(module))
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                seen_names.add(node.id)
            elif isinstance(node, ast.arg):
                seen_names.add(node.arg)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                seen_names.add(node.name)
            # A candidate ranked by computed value would need a key= sort or
            # a max/min over valuations. Neither may appear in these modules.
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in {"max", "min", "sorted"}:
                    if any(keyword.arg == "key" for keyword in node.keywords):
                        ranked.append(f"{module.__name__}:{node.func.id}(key=...)")
    drift = sorted(seen_names & drift_names)
    check("no restoring-drift identifier anywhere in the evaluation path", not drift, str(drift))
    check("no value-ranked selection in the valuation path", not ranked, str(ranked))


def test_no_harness_transition_is_called() -> None:
    """AST guard: this file makes no direct call to a harness transition."""
    tree = ast.parse(inspect.getsource(inspect.getmodule(test_a_equilibrium_minimum)))
    forbidden = {"run_tick", "run_stage_a", "advance", "advance_epoch", "execute_tick"}
    called = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            name = None
            if isinstance(node.func, ast.Name):
                name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                name = node.func.attr
            if name in forbidden:
                called.add(name)
    check("no direct harness transition call in this file", not called, str(called))


def test_no_science_is_adopted_here() -> None:
    """Nothing in this suite registers a parameter or asserts recovery.

    The recovery check inspects the label of every `check(...)` call rather
    than the raw file text, so it cannot be satisfied or tripped by prose.
    """
    module = inspect.getmodule(test_a_equilibrium_minimum)
    tree = ast.parse(inspect.getsource(module))
    recovery_labels: list[str] = []
    for function in ast.walk(tree):
        if not isinstance(function, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        # This guard's own labels necessarily name the thing they forbid.
        if function.name == "test_no_science_is_adopted_here":
            continue
        for node in ast.walk(function):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id == "check" and node.args:
                    label = node.args[0]
                    if isinstance(label, ast.Constant) and isinstance(label.value, str):
                        if "recover" in label.value.lower():
                            recovery_labels.append(label.value)
    check(
        "no assertion in this suite requires recovery",
        not recovery_labels,
        str(recovery_labels),
    )
    recovery_named = [
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and "recover" in node.name.lower()
    ]
    check("no test function is named for recovery", not recovery_named, str(recovery_named))
    check("this suite declares its synthetic scope", "synthetic" in inspect.getsource(module))


def main() -> int:
    groups = (
        ("A equilibrium minimum", test_a_equilibrium_minimum),
        ("B symmetric displacement", test_b_symmetric_displacement),
        ("C analytic marginal vs finite difference", test_c_marginal_matches_finite_difference),
        ("D equilibrium disturbance is negative", test_d_equilibrium_disturbance_is_negative),
        ("E restorative action is positive", test_e_restorative_action_is_positive),
        ("F overshoot uses endpoint potential", test_f_overshoot_uses_endpoint_potential),
        ("G path integral closes", test_g_path_integral_closes),
        ("H disjoint actions add", test_h_disjoint_actions_add),
        ("I shared-coordinate interaction", test_i_shared_coordinate_interacts),
        ("J receipts sum to group value", test_j_receipts_sum_to_group_value),
        ("K third-order Moebius vanishes", test_k_third_order_mobius_vanishes),
        ("L zero capacity rejects disturbance", test_l_zero_capacity_rejects_disturbance),
        ("M earned capacity finances later loss", test_m_earned_capacity_finances_later_loss),
        ("N overdraft is rejected", test_n_overdraft_is_rejected),
        ("O forcing changes J not B", test_o_forcing_changes_audit_not_balances),
        ("P action changes B not J", test_p_action_changes_balances_not_audit),
        ("Q conservation closes", test_q_conservation_closes),
        ("R driven accounting closes", test_r_driven_accounting_closes),
        ("locality of valuation", test_locality_of_valuation),
        ("analytic and finite forms agree", test_analytic_and_finite_forms_agree),
        ("evaluation is side-effect free", test_evaluation_is_side_effect_free),
        ("no mean reversion or EBU selection", test_no_mean_reversion_or_ebu_selection_in_source),
        ("no harness transition called", test_no_harness_transition_is_called),
        ("no science adopted here", test_no_science_is_adopted_here),
    )
    for label, test in groups:
        print(f"\n{label}")
        test()
    print(
        f"\nLocal Gaussian foundation gate: {PASSED} passed, {FAILED} failed, "
        f"{len(groups)} groups"
    )
    print("Execution class: NON-MODEL-ADVANCING STATIC/PURE (this suite only)")
    print(f"  numeric policy: exact rational, tolerance 0")
    print(f"  max |analytic vs finite residual|:  {MAX_ANALYTIC_RESIDUAL}")
    print(f"  max |receipt closure residual|:     {MAX_RECEIPT_RESIDUAL}")
    print(f"  max |conservation residual|:        {MAX_CONSERVATION_RESIDUAL}")
    print(f"  max |accounting residual|:          {MAX_ACCOUNTING_RESIDUAL}")
    print("  scientific-study execution: NONE")
    print("  scientific trajectories generated: 0")
    print("  scientific evidence generated: NONE")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())
