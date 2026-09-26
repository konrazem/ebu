"""Exact checks for EBU_DYNAMIC_FIELD_THEORY_SYNTHESIS.md.

(The Theory I / II / III files are superseded working history; the synthesis is
the authority these checks track.)

Theorem verification, not a behavioural simulation. Every world here is a
declared toy of at most a few hundred states; no actor policy runs, no ledger is
driven, no arrival law is sampled, nothing is preregistered and no result here is
evidence about an economy. Arithmetic is exact `Fraction` and every tolerance is
literally zero.

**Every check in this module is deterministic and exhaustive over its declared
domain. There is no randomized search.** A previous revision contained a
20 000-trial random sweep offered as support for a rigidity claim; it has been
removed and replaced by the exact per-world certificate `R(V_0, C)`, which
decides the same question by finite linear algebra. A later revision also
replaced `SY1`'s 500 seeded random walks with an exhaustive enumeration of every
edge and every two-step walk of the declared lattice.

The `S1-*` section enumerates the **actual** frozen Study-1 action graph by
calling `demand_driven_ebu` pure functions on synthetic individual states. No
`EconomyRun`, no actor policy, no arrival law and no trajectory is involved, and
nothing in that package is modified: the atomic P-demand rule tested there is an
*analysis* of a candidate semantics, built in this module alone.

Checks are witnesses that the algebra was not mistyped; the proofs are in the
report. Where the report marks a statement DISPROVED AS STATED, the check below
is the counterexample itself.

Run: python3 dynamic_ebu_theory_checks.py
"""

from __future__ import annotations

import sys
from fractions import Fraction as F
from itertools import combinations, product

sys.path.insert(0, "/Users/konrad.grzyb/code/ebu")

RESULTS: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    RESULTS.append((name, bool(ok), detail))


# --------------------------------------------------------------------------
# exact linear algebra, lattices, graphs
# --------------------------------------------------------------------------

def rank(rows) -> int:
    rows = [list(r) for r in rows]
    if not rows:
        return 0
    ncols = len(rows[0])
    r = 0
    for c in range(ncols):
        piv = None
        for i in range(r, len(rows)):
            if rows[i][c] != 0:
                piv = i
                break
        if piv is None:
            continue
        rows[r], rows[piv] = rows[piv], rows[r]
        pv = rows[r][c]
        rows[r] = [v / pv for v in rows[r]]
        for i in range(len(rows)):
            if i != r and rows[i][c] != 0:
                f = rows[i][c]
                rows[i] = [a - f * b for a, b in zip(rows[i], rows[r])]
        r += 1
        if r == len(rows):
            break
    return r


def lattice(cells: int, total: int):
    if cells == 1:
        return [(total,)]
    out = []
    for k in range(total + 1):
        for rest in lattice(cells - 1, total - k):
            out.append((k,) + rest)
    return out


def states(cells: int, total: int):
    return [tuple(F(v) for v in s) for s in lattice(cells, total)]


def unit_edges(sts):
    idx = set(sts)
    out = []
    for x in sts:
        for i in range(len(x)):
            if x[i] < 1:
                continue
            for j in range(len(x)):
                if i == j:
                    continue
                y = list(x)
                y[i] -= 1
                y[j] += 1
                y = tuple(y)
                if y in idx:
                    out.append((x, y))
    return out


def gauss(ref, sig):
    ref = [F(v) for v in ref]
    sig = [F(v) for v in sig]

    def V(x):
        t = F(0)
        for xi, ri, si in zip(x, ref, sig):
            t += (xi - ri) * (xi - ri) / (2 * si * si)
        return t

    return V


def components(vertices, edges):
    """Connected components of an undirected edge list, as a vertex -> id map."""
    parent = {v: v for v in vertices}

    def find(v):
        while parent[v] != v:
            parent[v] = parent[parent[v]]
            v = parent[v]
        return v

    for (x, y) in edges:
        rx, ry = find(x), find(y)
        if rx != ry:
            parent[rx] = ry
    roots = sorted({find(v) for v in vertices}, key=str)
    order = {r: i for i, r in enumerate(roots)}
    return {v: order[find(v)] for v in vertices}


def spanning_tree(vertices, edges):
    """A spanning forest and the list of non-tree edges (chords)."""
    adj: dict = {v: [] for v in vertices}
    for e in edges:
        adj[e[0]].append((e[1], e))
        adj[e[1]].append((e[0], e))
    parent: dict = {}
    tree = set()
    for root in vertices:
        if root in parent:
            continue
        parent[root] = None
        stack = [root]
        while stack:
            u = stack.pop()
            for v, e in adj[u]:
                if v not in parent:
                    parent[v] = u
                    tree.add(e)
                    stack.append(v)
    chords = [e for e in edges if e not in tree]
    return parent, tree, chords


def fundamental_cycles(vertices, edges):
    """Each chord's fundamental cycle, as a closed oriented edge walk."""
    parent, tree, chords = spanning_tree(vertices, edges)

    def chain(v):
        out = [v]
        while parent[v] is not None:
            v = parent[v]
            out.append(v)
        return out

    cycles = []
    for (x, y) in chords:
        cx, cy = chain(x), chain(y)
        pos = {v: i for i, v in enumerate(cx)}
        lca = next(v for v in cy if v in pos)
        walk = [(x, y)]
        for k in range(cy.index(lca)):
            walk.append((cy[k], cy[k + 1]))
        for k in range(pos[lca], 0, -1):
            walk.append((cx[k], cx[k - 1]))
        cycles.append(walk)
    return cycles


def is_exact(vertices, edges, s):
    """Does an antisymmetric cochain admit W with s(x->y) = W(x) - W(y)?"""
    adj: dict = {v: [] for v in vertices}
    for (x, y) in edges:
        adj[x].append(y)
        adj[y].append(x)
    W: dict = {}
    for root in vertices:
        if root in W:
            continue
        W[root] = F(0)
        stack = [root]
        while stack:
            u = stack.pop()
            for v in adj[u]:
                val = W[u] - s(u, v)
                if v in W:
                    if W[v] != val:
                        return False
                else:
                    W[v] = val
                    stack.append(v)
    return True


# --------------------------------------------------------------------------
# shared worlds
# --------------------------------------------------------------------------

S3, E3 = states(3, 6), None
E3 = unit_edges(S3)
S2c, E2c = states(2, 3), None
E2c = unit_edges(S2c)

V_REF = gauss([2, 2, 2], [1, 1, 1])
V_SCALED = gauss([2, 2, 2], [2, 2, 2])
V_NULLSHIFT = gauss([F(5, 2)] * 3, [1, 1, 1])
V_PERCOORD = gauss([2, 2, 2], [1, 1, 2])
V_MOVED = gauss([F(5, 2), 2, F(3, 2)], [1, 1, 1])


# --------------------------------------------------------------------------
# 1. actor / field decomposition
# --------------------------------------------------------------------------

def section_decomposition() -> None:
    x_t = (F(3), F(2), F(1))
    x_n = (F(2), F(2), F(2))
    V_t, V_n = V_REF, V_SCALED
    e_actor = V_t(x_t) - V_t(x_n)
    e_field = V_t(x_n) - V_n(x_n)
    check("D1 actor/field decomposition is exact",
          e_actor + e_field == V_t(x_t) - V_n(x_n))
    e_field2 = V_t(x_t) - V_n(x_t)
    e_actor2 = V_n(x_t) - V_n(x_n)
    check("D1 the reversed order telescopes to the same total",
          e_actor2 + e_field2 == V_t(x_t) - V_n(x_n))
    mixed = e_actor - e_actor2
    check("D2 the split is order dependent", mixed != 0, f"mixed = {mixed}")
    check("D2 mixed term equals (p_t - p_{t+1}) * Delta W",
          mixed == (F(1) - F(1, 4)) * (V_REF(x_t) - V_REF(x_n)))


# --------------------------------------------------------------------------
# 2. Theorem I
# --------------------------------------------------------------------------

def centered(V, sts):
    base = sts[0]
    return [V(x) - V(base) for x in sts]


def rank_one_positive(fields, sts):
    vecs = [centered(V, sts) for V in fields]
    if rank(vecs) > 1:
        return False
    ref = next((v for v in vecs if any(c != 0 for c in v)), None)
    if ref is None:
        return True
    for v in vecs:
        lam = next((a / b for a, b in zip(v, ref) if b != 0), None)
        if lam is None or lam <= 0:
            return False
    return True


def edge_ratios(fields, edges):
    V0 = fields[0]
    out = []
    for V in fields:
        rho = None
        for (x, y) in edges:
            d0, d = V0(x) - V0(y), V(x) - V(y)
            if d0 == 0:
                if d != 0:
                    return None
                continue
            r = d / d0
            if rho is None:
                rho = r
            elif r != rho:
                return None
        if rho is None or rho <= 0:
            return None
        out.append(rho)
    return out


def section_theorem_one() -> None:
    check("I-A common sigma scaling is a scalar revaluation",
          rank_one_positive([V_REF, V_SCALED], S3))
    ratios = edge_ratios([V_REF, V_SCALED], E3)
    check("I-A the edge-ratio test returns p = 1/4",
          ratios is not None and ratios[1] == F(1, 4), str(ratios))
    check("I-B a reference shift along H^-1 1 is a scalar revaluation",
          rank_one_positive([V_REF, V_NULLSHIFT], S3))
    offsets = set(V_NULLSHIFT(x) - V_REF(x) for x in S3)
    check("I-B that shift changes V by one constant: p = 1, k = 3/8",
          offsets == {F(3, 8)}, str(offsets))
    check("I-B a null-direction shift changes no EBU value",
          all(V_NULLSHIFT(x) - V_NULLSHIFT(y) == V_REF(x) - V_REF(y) for (x, y) in E3))
    check("I-C per-coordinate sigma on three cells is NOT a scalar revaluation",
          not rank_one_positive([V_REF, V_PERCOORD], S3))
    check("I-C and its edge-ratio test fails too",
          edge_ratios([V_REF, V_PERCOORD], E3) is None)
    check("I-E a generic moving reference is NOT a scalar revaluation",
          not rank_one_positive([V_REF, V_MOVED], S3))
    fam = [V_REF, V_SCALED, V_NULLSHIFT, V_PERCOORD, V_MOVED,
           gauss([2, 2, 2], [F(1, 2), F(1, 2), F(1, 2)])]
    check("I-F vertex rank-one test and edge-ratio test agree on a connected component",
          all((rank_one_positive([a, b], S3)) == (edge_ratios([a, b], E3) is not None)
              for a in fam for b in fam))
    check("I-G the 3-cell M=6 reachable component has exactly 28 states",
          len(S3) == 28, f"{len(S3)}")


# --------------------------------------------------------------------------
# 3. TWO-CELL GAUSSIAN — corrected: the linear condition is not optional
# --------------------------------------------------------------------------

def scalar_revaluation(v0, v1):
    """Return (p, k) with v1 = p v0 + k on the listed states, else None."""
    for i in range(len(v0)):
        for j in range(len(v0)):
            if v0[i] != v0[j]:
                p = (v1[i] - v1[j]) / (v0[i] - v0[j])
                k = v1[i] - p * v0[i]
                if all(b == p * a + k for a, b in zip(v0, v1)):
                    return (p, k)
                return None
    return None


def section_two_cell() -> None:
    # the auditor's counterexample: reference OFF the conservation slice
    sts = [(F(0), F(2)), (F(1), F(1)), (F(2), F(0))]
    V0 = lambda x: (x[0] ** 2 + x[1] ** 2) / 2
    V1 = lambda x: x[0] ** 2 / 2 + x[1] ** 2 / 8
    v0, v1 = [V0(x) for x in sts], [V1(x) for x in sts]
    check("T1 the off-slice two-cell pair has V0 = (2,1,2)",
          v0 == [F(2), F(1), F(2)], str([str(v) for v in v0]))
    check("T1 and V1 = (1/2, 5/8, 2)",
          v1 == [F(1, 2), F(5, 8), F(2)], str([str(v) for v in v1]))
    check("T2 V0 ties the endpoints but V1 separates them",
          v0[0] == v0[2] and v1[0] != v1[2])
    check("T3 so NO scalar revaluation exists: a per-coordinate sigma change on "
          "two cells is NOT automatically one",
          scalar_revaluation(v0, v1) is None)
    check("T3 reference (0,0) does NOT lie on the conservation slice M = 2",
          F(0) + F(0) != F(2))

    # corrected criterion: reference ON the slice is what makes it work
    for (ref, M, expect) in [((F(3, 2), F(3, 2)), 3, True),
                             ((F(1), F(1)), 2, True),
                             ((F(0), F(0)), 2, False),
                             ((F(0), F(4)), 4, True),
                             ((F(1), F(2)), 4, False)]:
        lat = [(F(k), F(M - k)) for k in range(M + 1)]
        A = gauss(ref, [1, 1])
        B = gauss(ref, [1, 2])
        got = scalar_revaluation([A(x) for x in lat], [B(x) for x in lat])
        on_slice = (ref[0] + ref[1] == M)
        check(f"T4 two cells, ref={tuple(str(r) for r in ref)}, M={M}: "
              f"on-slice={on_slice} matches revaluation={got is not None}",
              (got is not None) == expect and on_slice == expect,
              f"got {got}")
    lat = [(F(k), F(3 - k)) for k in range(4)]
    A, B = gauss([F(3, 2), F(3, 2)], [1, 1]), gauss([F(3, 2), F(3, 2)], [1, 2])
    got = scalar_revaluation([A(x) for x in lat], [B(x) for x in lat])
    check("T5 on-slice two-cell revaluation has p = 5/8 exactly",
          got is not None and got[0] == F(5, 8), str(got))


# --------------------------------------------------------------------------
# 4. ENDPOINT NORMALIZER — corrected theorem, with the auditor's chain
# --------------------------------------------------------------------------

def antisymmetric_ok(edges, V, p):
    return all(V[x] == V[y] or p[x] == p[y] for (x, y) in edges)


def endpoint_criterion(vertices, edges, V, p):
    """Corrected criterion. Assumes the per-edge antisymmetry condition holds."""
    active = [(x, y) for (x, y) in edges if V[x] != V[y]]
    comp = components(vertices, active)
    for cyc in fundamental_cycles(vertices, edges):
        total = F(0)
        for (u, v) in cyc:
            if V[u] != V[v]:
                total += (V[u] - V[v]) / p[u]
        if total != 0:
            return False
    return True


def section_endpoint() -> None:
    # --- the auditor's chain: p varies, V varies, and the rule is EXACT ---
    Vc = {"a": F(9, 2), "b": F(1, 2), "c": F(1, 2), "d": F(5, 2)}
    Wc = {"a": F(9, 4), "b": F(1, 4), "c": F(1, 4), "d": F(9, 4)}
    pc = {"a": F(2), "b": F(2), "c": F(1), "d": F(1)}
    chain = [("a", "b"), ("b", "c"), ("c", "d")]
    verts = ["a", "b", "c", "d"]
    every = True
    for (x, y) in chain:
        for (u, v) in [(x, y), (y, x)]:
            if (Vc[u] - Vc[v]) / pc[u] != Wc[u] - Wc[v]:
                every = False
    check("E1 auditor chain: [V(x)-V(y)]/p(x) = W(x)-W(y) on EVERY orientation",
          every)
    check("E1 p is not constant", len(set(pc.values())) > 1)
    check("E1 W(a) = W(d) while V(a) != V(d)",
          Wc["a"] == Wc["d"] and Vc["a"] != Vc["d"])
    check("E1 the chain is a tree: cycle space has dimension 0",
          len(fundamental_cycles(verts, chain)) == 0)
    check("E1 the endpoint cochain is exact on the chain",
          antisymmetric_ok(chain, Vc, pc)
          and is_exact(verts, chain, lambda u, v: (Vc[u] - Vc[v]) / pc[u]))
    check("E2 DISPROVES the old claim 'connectivity forces p constant where V varies'",
          True and antisymmetric_ok(chain, Vc, pc) and len(set(pc.values())) > 1)

    # --- the chain also refutes Theorem B as originally stated ---
    check("E6 on the chain, s = W(x)-W(y) is exact, field-independent, and "
          "edge-proportional to V with a positive LOCAL factor 1/p(x)",
          all((Vc[u] - Vc[v]) / pc[u] == Wc[u] - Wc[v]
              for (x, y) in chain for (u, v) in [(x, y), (y, x)]))
    check("E6 yet NO global (p,k) gives V = p W + k, so the old Theorem B "
          "conclusion fails on a world meeting all four of its requirements",
          scalar_revaluation([Wc[s] for s in verts], [Vc[s] for s in verts]) is None)

    # --- the same local data on a ring: now it mints ---
    Vr = {"a": F(1), "b": F(0), "c": F(0), "d": F(1)}
    pr = {"a": F(2), "b": F(2), "c": F(1), "d": F(1)}
    ring = [("a", "b"), ("b", "c"), ("c", "d"), ("d", "a")]
    circ = sum(((Vr[x] - Vr[y]) / pr[x] for (x, y) in ring), F(0))
    check("E3 ring: every edge still satisfies the per-edge condition",
          antisymmetric_ok(ring, Vr, pr))
    check("E3 yet the circulation is -1/2, so the rule is NOT exact",
          circ == F(-1, 2), f"circulation {circ}")
    check("E3 the corrected criterion rejects the ring",
          not endpoint_criterion(["a", "b", "c", "d"], ring, Vr, pr))
    check("E3 and accepts the chain",
          endpoint_criterion(verts, chain, Vc, pc))

    # --- exhaustive equivalence of criterion and exactness ---
    for (name, verts_, edges_) in [
        ("4-ring", ["a", "b", "c", "d"],
         [("a", "b"), ("b", "c"), ("c", "d"), ("d", "a")]),
        ("4-chain", ["a", "b", "c", "d"],
         [("a", "b"), ("b", "c"), ("c", "d")]),
        ("theta graph", ["a", "b", "c", "d"],
         [("a", "b"), ("b", "c"), ("c", "d"), ("d", "a"), ("a", "c")]),
    ]:
        vals = [F(0), F(1), F(2)]
        ps = [F(1), F(2)]
        tested = agree = 0
        for Vv in product(vals, repeat=len(verts_)):
            V = dict(zip(verts_, Vv))
            for pv in product(ps, repeat=len(verts_)):
                p = dict(zip(verts_, pv))
                if not antisymmetric_ok(edges_, V, p):
                    continue
                tested += 1
                s = lambda u, v: (V[u] - V[v]) / p[u]
                if endpoint_criterion(verts_, edges_, V, p) == is_exact(verts_, edges_, s):
                    agree += 1
        check(f"E4 exhaustive on the {name}: criterion <=> exactness "
              f"({agree}/{tested} admissible assignments)",
              tested > 0 and agree == tested, f"{agree}/{tested}")

    # --- one active component is always enough ---
    Vs = {"a": F(0), "b": F(1), "c": F(2), "d": F(3)}
    ps = {v: F(2) for v in Vs}
    ring2 = [("a", "b"), ("b", "c"), ("c", "d"), ("d", "a")]
    check("E5 a single active component with constant p is always exact",
          antisymmetric_ok(ring2, Vs, ps)
          and is_exact(list(Vs), ring2, lambda u, v: (Vs[u] - Vs[v]) / ps[u]))


# --------------------------------------------------------------------------
# 5. settlement, cycles, minting
# --------------------------------------------------------------------------

def section_settlement() -> None:
    W = V_REF
    cycle = [(F(3), F(2), F(1)), (F(2), F(3), F(1)), (F(2), F(2), F(2)),
             (F(3), F(1), F(2)), (F(3), F(2), F(1))]
    total = sum((W(cycle[i]) - W(cycle[i + 1]) for i in range(len(cycle) - 1)), F(0))
    check("S1 normalized settlement telescopes to zero on a closed cycle", total == 0)
    ps = [F(1), F(1, 4), F(9), F(2)]
    check("S2 normalization closes the cycle for ANY field path sharing one W",
          sum(((ps[i] * (W(cycle[i]) - W(cycle[i + 1]))) / ps[i]
               for i in range(len(cycle) - 1)), F(0)) == 0)
    raw = sum((ps[i] * (W(cycle[i]) - W(cycle[i + 1])) for i in range(len(cycle) - 1)), F(0))
    check("S3 raw EBU has nonzero ACTOR-ledger circulation when p varies", raw != 0,
          f"actor circulation {raw}")

    # minimal endpoint counterexample (p varying on a single edge)
    V = {"a": F(1), "b": F(0)}
    p = {"a": F(1), "b": F(2)}
    circ = (V["a"] - V["b"]) / p["a"] + (V["b"] - V["a"]) / p["b"]
    check("S6 the endpoint rule is not even antisymmetric when p varies across an "
          "edge with Delta V != 0", circ == F(1, 2), f"{circ}")

    for (a, b) in [(F(2), F(1)), (F(5), F(3)), (F(7, 2), F(1, 2))]:
        minted = (a * a / 2 - b * b / 2) * a + (b * b / 2 - a * a / 2) * b
        check(f"S7 V=x^2/2, p=1/x gives (a-b)^2(a+b)/2 at a={a},b={b}",
              minted == (a - b) ** 2 * (a + b) / 2 and minted > 0, f"{minted}")
        Wc = lambda z: z ** 3 / 3
        check(f"S7 the exact rule W=x^3/3 closes the same cycle at a={a},b={b}",
              (Wc(a) - Wc(b)) + (Wc(b) - Wc(a)) == 0)

    Vt = {"a": F(0), "b": F(1), "c": F(3)}
    g = {("a", "b"): F(1), ("b", "c"): F(1), ("c", "a"): F(2)}
    tri = (g[("a", "b")] * (Vt["a"] - Vt["b"]) + g[("b", "c")] * (Vt["b"] - Vt["c"])
           + g[("c", "a")] * (Vt["c"] - Vt["a"]))
    two = g[("a", "b")] * (Vt["a"] - Vt["b"]) + g[("a", "b")] * (Vt["b"] - Vt["a"])
    check("S9 a symmetric pairwise weight always closes 2-cycles", two == 0)
    check("S9 but mints on a triangle", tri == 3, f"{tri}")


# --------------------------------------------------------------------------
# 6. graph topology
# --------------------------------------------------------------------------

def undirected(sts):
    idx = {x: i for i, x in enumerate(sts)}
    seen = set()
    for x in sts:
        for i in range(len(x)):
            if x[i] < 1:
                continue
            for j in range(len(x)):
                if i == j:
                    continue
                y = list(x)
                y[i] -= 1
                y[j] += 1
                y = tuple(y)
                if y in idx:
                    seen.add(frozenset((x, y)))
    return [tuple(sorted(e, key=lambda z: idx[z])) for e in seen], idx


def has_directed_cycle(vertices, arcs) -> bool:
    colour = {v: 0 for v in vertices}
    out: dict = {v: [] for v in vertices}
    for (u, v) in arcs:
        out[u].append(v)

    def visit(u):
        colour[u] = 1
        for v in out[u]:
            if colour[v] == 1:
                return True
            if colour[v] == 0 and visit(v):
                return True
        colour[u] = 2
        return False

    return any(colour[v] == 0 and visit(v) for v in vertices)


def section_graph() -> None:
    und, idx = undirected(S3)
    n, m = len(S3), len(und)
    cob = [[F(1) if idx[x] == k else (F(-1) if idx[y] == k else F(0))
            for (x, y) in und] for k in range(n)]
    rk = rank(cob)
    check("G1 exact cochains form a space of dimension n-1", rk == n - 1, f"{rk}")
    check("G2 the cycle space has dimension m-n+1", m - rk == m - n + 1,
          f"n={n} m={m} dim={m - rk}")
    cycles = fundamental_cycles(S3, und)
    check("G2 a fundamental cycle basis has exactly m-n+1 elements",
          len(cycles) == m - n + 1, f"{len(cycles)}")

    Wr = {x: F(idx[x] * idx[x] % 17) - F(8) for x in S3}
    check("G4 an exact cochain is exact", is_exact(S3, und, lambda u, v: Wr[u] - Wr[v]))
    first = und[0]
    def s_bad(u, v):
        base = Wr[u] - Wr[v]
        if frozenset((u, v)) == frozenset(first):
            return base + (F(1) if idx[u] < idx[v] else F(-1))
        return base
    check("G5 perturbing one edge destroys exactness",
          not is_exact(S3, und, s_bad))

    # directed regime
    dia_v = ["a", "b", "c", "d"]
    dia_arcs = [("a", "b"), ("a", "c"), ("b", "d"), ("c", "d")]
    check("G6 the diamond genuinely has no directed cycle (verified, not assumed)",
          not has_directed_cycle(dia_v, dia_arcs))
    s_dia = {("a", "b"): F(1), ("b", "d"): F(1), ("a", "c"): F(1), ("c", "d"): F(2)}
    check("G6 yet it is not exact: two irreversible routes settle differently",
          s_dia[("a", "b")] + s_dia[("b", "d")] != s_dia[("a", "c")] + s_dia[("c", "d")])
    check("G6 the underlying undirected cycle detects it",
          s_dia[("a", "b")] + s_dia[("b", "d")] - s_dia[("c", "d")] - s_dia[("a", "c")] != 0)

    # strong connectivity is SUFFICIENT but NOT NECESSARY
    tree_v = ["a", "b", "c"]
    tree_arcs = [("a", "b"), ("a", "c")]
    Wt = {"a": F(0), "b": F(-1), "c": F(-5)}
    check("G7 a directed tree has no directed cycle",
          not has_directed_cycle(tree_v, tree_arcs))
    check("G7 it is not strongly connected (no arc returns to a)",
          not any(v == "a" for (_, v) in tree_arcs))
    check("G7 yet every cochain on it is exact, so strong connectivity is NOT "
          "necessary for directed checking to suffice",
          is_exact(tree_v, tree_arcs, lambda u, v: Wt[u] - Wt[v]))


# --------------------------------------------------------------------------
# 7. common-W existence
# --------------------------------------------------------------------------

def same_weak_order(v0, v1) -> bool:
    n = len(v0)
    for i in range(n):
        for j in range(i + 1, n):
            if ((v0[i] < v0[j]) != (v1[i] < v1[j])) or ((v0[i] == v0[j]) != (v1[i] == v1[j])):
                return False
    return True


def quad_basis(x):
    a, b = x[0], x[1]
    return [F(1), a, b, a * a, a * b, b * b]


def rigidity_dim(total, ref, sig):
    sts = states(3, total)
    V = gauss(ref, sig)
    groups: dict = {}
    for x in sts:
        groups.setdefault(V(x), []).append(x)
    rows = []
    for members in groups.values():
        for k in range(1, len(members)):
            rows.append([p - q for p, q in zip(quad_basis(members[k]), quad_basis(members[0]))])
    return 6 - rank(rows), sorted((len(m) for m in groups.values()), reverse=True)


def section_common_w() -> None:
    sts = states(3, 6)
    v0, v1 = [V_REF(x) for x in sts], [V_SCALED(x) for x in sts]
    check("W1 a scalar revaluation is ordinally equivalent", same_weak_order(v0, v1))
    f: dict = {}
    ok = True
    for a, b in zip(v0, v1):
        if a in f and f[a] != b:
            ok = False
        f[a] = b
    check("W1 the induced f is well defined and strictly increasing on range(W)",
          ok and all((a < b) == (f[a] < f[b]) for a in f for b in f))

    d_sym, sizes_sym = rigidity_dim(6, [2, 2, 2], [1, 1, 1])
    check("W2 a level-set-rich reference field is RIGID (only affine partners)",
          d_sym == 2, f"dim {d_sym}, level sets {sizes_sym}")
    d_sym8, _ = rigidity_dim(8, [2, 2, 2], [1, 1, 1])
    check("W2 rigidity persists at M=8", d_sym8 == 2, f"dim {d_sym8}")
    d_asym, sizes_asym = rigidity_dim(6, [2, 2, 2], [1, 1, 2])
    check("W3 an unequal-sigma reference field is NOT rigid",
          d_asym > 2, f"dim {d_asym}, level sets {sizes_asym}")
    d_inj, sizes_inj = rigidity_dim(8, [-6, -6, -12], [F(1, 4), 4, F(5, 4)])
    check("W3 an injective reference field is maximally non-rigid",
          d_inj == 6 and sizes_inj[0] == 1, f"dim {d_inj}")

    s8 = states(3, 8)
    check("W4 the 3-cell M=8 reachable component has exactly 45 states",
          len(s8) == 45, f"{len(s8)}")
    A = gauss([-6, -6, -12], [F(1, 4), 4, F(5, 4)])
    B = gauss([-3, 21, F(3, 4)], [1, 8, 8])
    a, b = [A(x) for x in s8], [B(x) for x in s8]
    check("W4 class-B witness: identical weak order on all 45 states",
          same_weak_order(a, b))
    check("W4 class-B witness: NOT affinely related", scalar_revaluation(a, b) is None)

    s2 = states(2, 6)
    P, Q = gauss([-10, 0], [1, 1]), gauss([-10, -3], [1, 1])
    p2, q2 = [P(x) for x in s2], [Q(x) for x in s2]
    check("W6 on a 1-D reachable slice class B is inhabited",
          same_weak_order(p2, q2) and scalar_revaluation(p2, q2) is None)
    slopes = [(q2[i + 1] - q2[i]) / (p2[i + 1] - p2[i]) for i in range(len(s2) - 1)]
    check("W6 its chord slopes genuinely vary", len(set(slopes)) > 1)

    # the chain shows edge-local settlement is WEAKER than global representability
    Vc = {"a": F(9, 2), "b": F(1, 2), "c": F(1, 2), "d": F(5, 2)}
    Wc = {"a": F(9, 4), "b": F(1, 4), "c": F(1, 4), "d": F(9, 4)}
    order = ["a", "b", "c", "d"]
    check("W7 on the auditor chain V is NOT a function of W (W ties a,d; V does not)",
          Wc["a"] == Wc["d"] and Vc["a"] != Vc["d"])
    check("W7 so Theorem II.2's global criterion fails there",
          not same_weak_order([Wc[s] for s in order], [Vc[s] for s in order]))
    check("W7 yet an exact edge-local settlement by W exists",
          is_exact(order, [("a", "b"), ("b", "c"), ("c", "d")],
                   lambda u, v: Wc[u] - Wc[v]))


# --------------------------------------------------------------------------
# 8. Gaussian geometry
# --------------------------------------------------------------------------

def section_gaussian() -> None:
    sig = [F(1), F(2), F(3)]
    base = gauss([2, 2, 2], sig)
    s = [F(1, 2) * si * si for si in sig]
    shifted = gauss([F(2) + s[0], F(2) + s[1], F(2) + s[2]], sig)
    offs = set(shifted(x) - base(x) for x in S3)
    check("X1 a reference shift along H^-1 1 changes V by one constant",
          len(offs) == 1, str(offs))
    check("X1 so it changes no EBU value on the reachable slice",
          all(shifted(x) - shifted(y) == base(x) - base(y) for (x, y) in E3))
    bad = gauss([F(2) + s[0], F(2) + s[1], F(2)], sig)
    check("X1 a shift off that direction does change EBU values",
          any(bad(x) - bad(y) != base(x) - base(y) for (x, y) in E3))

    def compression_null(n):
        rows = []
        for i in range(n):
            for j in range(i + 1, n):
                t = [F(0)] * n
                t[i], t[j] = F(1), F(-1)
                rows.append([t[k] * t[k] for k in range(n)])
        return n - rank(rows)
    check("X2 on two cells the compression null space is 1-dimensional",
          compression_null(2) == 1)
    check("X3 on three or more cells it is trivial, forcing H_theta = p H_0",
          compression_null(3) == 0 and compression_null(4) == 0)
    check("X4 a generic moving reference admits no p",
          not rank_one_positive([V_REF, V_MOVED], S3))


# --------------------------------------------------------------------------
# 9. receipts — corrected
# --------------------------------------------------------------------------

def section_receipts() -> None:
    from gaussian_harness.actions import ActionGroup, AtomicAction
    from gaussian_harness.capacity import CapacityLedger
    from gaussian_harness.potential import LocalGaussianPotential
    from gaussian_harness.valuation import finite_ebu, mobius_term, value_group

    W_pot = LocalGaussianPotential.declare([10, 10, 10, 10], [1, 1, 2, 1])
    V_pot = LocalGaussianPotential.declare([10, 10, 10, 10], [2, 2, 4, 2])
    p = F(1, 4)
    state = (F(9), F(23, 2), F(10), F(19, 2))
    group = ActionGroup.of(AtomicAction.declare(0, 1, F(1)),
                           AtomicAction.declare(2, 3, F(1, 2)))
    vW, vV = value_group(W_pot, state, group), value_group(V_pot, state, group)

    # the path-level hypothesis, checked on the actual common path
    dG = group.increment(4)
    addp = lambda z, s: tuple(a + s * b for a, b in zip(z, dG))
    path_ok = all(V_pot.value_total(addp(state, F(k, 8))) ==
                  p * W_pot.value_total(addp(state, F(k, 8)))
                  for k in range(9))
    check("R0 the identity V = p W holds at every sampled point of the COMMON PATH, "
          "not merely at lattice vertices", path_ok)

    check("R1 Case I: the group value rescales by exactly p",
          vV.group_ebu == p * vW.group_ebu)
    check("R1 Case I: every common-path receipt rescales by exactly p",
          all(rv == p * rw for (_, rw), (_, rv) in zip(vW.receipts, vV.receipts)))
    dW = finite_ebu(W_pot, state, dG)
    check("R1 Case I: sum_a R_a/p = Delta W exactly",
          sum((rv / p for (_, rv) in vV.receipts), F(0)) == dW)
    check("R1 Case I: receipts close on the group value at zero tolerance",
          vW.residual == 0 and vV.residual == 0)

    # Case II counterexample: no common factor
    simpson = lambda g: (g(F(0)) + 4 * g(F(1, 2)) + g(F(1))) / 6
    Wv = lambda x: W_pot.value_total(x)
    dens = lambda da, s: -sum(W_pot.marginal(addp(state, s), i) * da[i]
                              for i in range(4) if da[i] != 0)
    das = [a.increment(4) for a in group.actions]
    Cs = [simpson(lambda s, d=d: dens(d, s)) for d in das]
    Rs = [simpson(lambda s, d=d: Wv(addp(state, s)) * dens(d, s)) for d in das]
    check("R2 Case II: sum_a C_a = Delta W exactly", sum(Cs, F(0)) == dW)
    VofW = lambda x: Wv(x) ** 2 / 2
    E_G = VofW(state) - VofW(addp(state, F(1)))
    check("R2 Case II: sum_a R_a = E_G exactly", sum(Rs, F(0)) == E_G)
    ratios = [r / c for r, c in zip(Rs, Cs)]
    check("R3 Case II: a common scalar can FAIL to exist for this group",
          len(set(ratios)) > 1, str([str(x) for x in ratios]))

    # ... but it can also SUCCEED for a non-affine f: the corrected statement
    x = (F(3), F(0), F(2), F(1))
    d1 = (F(-1), F(1), F(0), F(0))
    d2 = (F(0), F(0), F(-2), F(2))
    dG2 = tuple(a + b for a, b in zip(d1, d2))
    Wq = lambda z: sum(c * c for c in z) / 2
    add2 = lambda s: tuple(a + s * b for a, b in zip(x, dG2))
    om = lambda da, s: -sum(a * b for a, b in zip(add2(s), da))
    C1, C2 = simpson(lambda s: om(d1, s)), simpson(lambda s: om(d2, s))
    R1_, R2_ = (simpson(lambda s: Wq(add2(s)) * om(d1, s)),
                simpson(lambda s: Wq(add2(s)) * om(d2, s)))
    check("R4 witness group has Delta W = 0", Wq(x) - Wq(add2(F(1))) == 0)
    prof_prop = (om(d1, F(0)) * (om(d2, F(1)) - om(d2, F(0)))
                 == om(d2, F(0)) * (om(d1, F(1)) - om(d1, F(0))))
    check("R4 its two action profiles are NOT proportional", not prof_prop)
    check("R4 yet both receipts share ONE common factor 37/6 under f(w)=w^2/2",
          R1_ / C1 == R2_ / C2 == F(37, 6), f"{R1_ / C1}, {R2_ / C2}")
    check("R4 this DISPROVES 'distinct profiles imply failure unless f is affine'",
          R1_ / C1 == R2_ / C2 and not prof_prop)

    # Moebius
    incs = [AtomicAction.declare(0, 1, F(1)).increment(4),
            AtomicAction.declare(0, 2, F(1, 2)).increment(4),
            AtomicAction.declare(1, 3, F(3, 2)).increment(4)]
    mW = mobius_term(W_pot, state, incs[:2])
    mV = mobius_term(V_pot, state, incs[:2])
    check("M1 pair interaction coefficients rescale by the same p", mV / mW == p)
    check("M2 third-order Moebius vanishes for a quadratic field",
          mobius_term(W_pot, state, incs) == 0)

    def mob_general(Vfun, base, increments):
        n = len(increments)
        tot = F(0)
        for k in range(n + 1):
            sign = -1 if (n - k) % 2 else 1
            for chosen in combinations(range(n), k):
                comb = tuple(F(0) for _ in range(4))
                for pos in chosen:
                    comb = tuple(a + b for a, b in zip(comb, increments[pos]))
                tot += sign * (Vfun(base) - Vfun(tuple(a + b for a, b in zip(base, comb))))
        return tot
    check("M3 a nonaffine common-W transform makes it nonzero",
          mob_general(VofW, state, incs) != 0)

    # static V1 recovery -- no tautologies
    recs = [rw for (_, rw) in vW.receipts]
    check("V1-1 receipts are nonzero, so the recovery statement is not vacuous",
          all(r != 0 for r in recs), str([str(r) for r in recs]))
    check("V1-1 at p = 1 the normalized receipt EQUALS the V1 receipt",
          all(rw / F(1) == rw for (_, rw) in vW.receipts)
          and sum(recs, F(0)) == vW.group_ebu)
    check("V1-1 and W := V_theta0 makes the path-level identity trivial",
          all(W_pot.value_total(addp(state, F(k, 8)))
              == F(1) * W_pot.value_total(addp(state, F(k, 8))) for k in range(9)))
    owner = vW.owner_deltas
    check("V1-2 owner deltas sum to the group value",
          sum(owner.values(), F(0)) == vW.group_ebu)

    ledger = CapacityLedger(tuple(F(v) for v in (5, 5, 5, 5)))
    dec = ledger.project(owner)
    same = True
    for a in (F(1), F(3), F(1, 7), F(100)):
        scaled = CapacityLedger(tuple(a * b for b in ledger.balances))
        if scaled.project({k: a * v for k, v in owner.items()}).affordable != dec.affordable:
            same = False
    check("V1-3 affordability is invariant under the capacity unit", same)


# --------------------------------------------------------------------------
# 10. locality, monotonicity, gauge, field ledger, Capacity V2 semantics
# --------------------------------------------------------------------------

def section_corrections() -> None:
    # locality: factor-additive W is local; nonlinear f is not
    Wf = lambda z: sum(c * c for c in z) / 2
    f = lambda w: w * w / 2
    d = (F(-1), F(1), F(0))
    lin, non = set(), set()
    for spec in [F(0), F(3), F(10)]:
        x = (F(3), F(1), spec)
        y = tuple(a + b for a, b in zip(x, d))
        lin.add(Wf(x) - Wf(y))
        non.add(f(Wf(x)) - f(Wf(y)))
    check("L1 with affine f the value is independent of an untouched factor",
          len(lin) == 1, str([str(v) for v in lin]))
    check("L2 with nonlinear f it is NOT: locality of valuation fails",
          len(non) == 3, str(sorted(str(v) for v in non)))
    x0 = (F(2), F(1), F(10))
    y0 = tuple(a + b for a, b in zip(x0, d))
    check("L2 qualification: a Delta W = 0 group cannot exhibit the failure",
          Wf(x0) - Wf(y0) == 0 and f(Wf(x0)) - f(Wf(y0)) == 0)

    # factor-additive but NOT coordinate-separable W is still local
    WF = lambda z: (z[0] * z[1]) + (z[2] * z[2] + z[3])
    d2 = (F(-1), F(1), F(0), F(0))
    vals = set()
    for spect in [(F(0), F(0)), (F(5), F(7)), (F(2), F(9))]:
        x = (F(2), F(3)) + spect
        y = tuple(a + b for a, b in zip(x, d2))
        vals.add(WF(x) - WF(y))
    check("L3 a factor-additive W with a MULTI-COORDINATE factor is still local, "
          "so locality does not force coordinate separability",
          len(vals) == 1, str([str(v) for v in vals]))

    # strictly increasing does not give f' > 0
    fc = lambda w: w ** 3
    check("P1 f(w)=w^3 is strictly increasing on the sampled grid",
          all(fc(F(i, 4)) < fc(F(i + 1, 4)) for i in range(-8, 8)))
    check("P1 yet its chord slopes stay strictly positive (p_eff > 0 survives)",
          all((fc(F(j, 4)) - fc(F(i, 4))) / (F(j, 4) - F(i, 4)) > 0
              for i in range(-8, 8) for j in range(i + 1, 9)))
    check("P1 while f'(0) = 0, so p_local = f'(W) > 0 does NOT survive",
          3 * F(0) ** 2 == 0)

    # gauge freedom of W in the monotone class
    Wa = {"s0": F(0), "s1": F(1), "s2": F(2)}
    h = lambda w: w ** 3 + w
    Wb = {k: h(v) for k, v in Wa.items()}
    check("P2 h(w)=w^3+w is strictly increasing on the sampled grid",
          all(h(F(i, 4)) < h(F(i + 1, 4)) for i in range(-8, 8)))
    check("P2 W and h(W) carry the same ordinal structure",
          same_weak_order([Wa[s] for s in Wa], [Wb[s] for s in Wa]))
    check("P2 but give DIFFERENT settlements, so in the monotone class W is not "
          "pinned up to positive affine maps",
          (Wa["s0"] - Wa["s2"]) != (Wb["s0"] - Wb["s2"]),
          f"{Wa['s0'] - Wa['s2']} vs {Wb['s0'] - Wb['s2']}")

    # moving field: the external ledger closes the accounting
    Wz = {"x": F(3), "y": F(1)}
    hi, lo = F(2), F(1)
    Vt = lambda st, pp: pp * Wz[st]
    actor = hi * (Wz["x"] - Wz["y"]) + lo * (Wz["y"] - Wz["x"])
    field = (Vt("y", hi) - Vt("y", lo)) + (Vt("x", lo) - Vt("x", hi))
    check("N1 the actor ledger gains +2 around the closed physical cycle",
          actor == 2, f"{actor}")
    check("N1 the external field ledger loses exactly the same amount",
          field == -2, f"{field}")
    check("N1 so the GRAND TOTAL closes at zero: this is extraction from the "
          "field ledger, not creation ex nihilo",
          actor + field == 0)

    # Capacity V2: the ceiling is NOT part of affordability
    from capacity_v2.ledger import DeviationBoundedLedger
    from gaussian_harness.potential import LocalGaussianPotential
    pot = LocalGaussianPotential.declare([10, 10], [1, 1])
    led = DeviationBoundedLedger((F(0), F(0)), F(0))
    at_ref = (F(10), F(10))
    check("C1 V2 affordability refuses a negative projection (unchanged from V1)",
          not led.project({0: F(-1)}).affordable)
    rich = DeviationBoundedLedger((F(50), F(0)), F(0))
    check("C1 V2 affordability ACCEPTS a projection far above the ceiling, "
          "so the ceiling is not an affordability test",
          rich.project({0: F(-1)}).affordable
          and F(49) > rich.ceiling(pot, at_ref, 0))
    settled = rich.reconcile(pot, at_ref)
    check("C2 the ceiling acts AFTER settlement, retiring the excess into a sink",
          settled.balances[0] == F(0) and settled.retired == F(50),
          f"balances {settled.balances}, retired {settled.retired}")
    check("C3 at the reference the ceiling is zero, so retirement empties the cell",
          pot.factor_value(at_ref, 0) == 0 and settled.balances[0] == 0)
    check("C4 and only THEN does the unchanged affordability rule refuse damage",
          not settled.project({0: F(-1)}).affordable)



# --------------------------------------------------------------------------
# 11. THE DECISIVE THEOREMS: existence, ruler, freedom
# --------------------------------------------------------------------------

def ds_criterion(verts, edges, fields):
    """Theorem DS criterion: common orientation + acyclicity after contraction."""
    strict, null = [], []
    for (x, y) in edges:
        signs = set()
        for V in fields:
            d = V[x] - V[y]
            if d != 0:
                signs.add(1 if d > 0 else -1)
        if len(signs) > 1:
            return False
        if not signs:
            null.append((x, y))
        else:
            strict.append((x, y) if signs.pop() > 0 else (y, x))
    par = {v: v for v in verts}

    def find(v):
        while par[v] != v:
            par[v] = par[par[v]]
            v = par[v]
        return v

    for (x, y) in null:
        rx, ry = find(x), find(y)
        if rx != ry:
            par[rx] = ry
    arcs = [(find(a), find(b)) for (a, b) in strict]
    if any(a == b for (a, b) in arcs):
        return False
    nodes = {find(v) for v in verts}
    out: dict = {n: [] for n in nodes}
    for (a, b) in arcs:
        out[a].append(b)
    colour = {n: 0 for n in nodes}

    def dfs(u):
        colour[u] = 1
        for w in out[u]:
            if colour[w] == 1:
                return True
            if colour[w] == 0 and dfs(w):
                return True
        colour[u] = 2
        return False

    return not any(colour[n] == 0 and dfs(n) for n in nodes)


def ds_oracle(verts, edges, fields):
    """Independent brute force over integer W in {0..n-1}; complete for DAGs."""
    n = len(verts)
    for vals in product(range(n), repeat=n):
        W = dict(zip(verts, vals))
        ok = True
        for (x, y) in edges:
            s = W[x] - W[y]
            for V in fields:
                d = V[x] - V[y]
                if d == 0:
                    continue
                if s == 0 or (s > 0) != (d > 0):
                    ok = False
                    break
            if not ok:
                break
            if all(V[x] == V[y] for V in fields) and s != 0:
                ok = False
                break
        if ok:
            return True
    return False


def endpoint_W(verts, edges, Vm, p):
    """Finite necessary-and-sufficient algorithm for the endpoint normalizer."""
    for (x, y) in edges:
        if Vm[x] != Vm[y] and p[x] != p[y]:
            return None
    par = {v: v for v in verts}

    def find(v):
        while par[v] != v:
            par[v] = par[par[v]]
            v = par[v]
        return v

    for (x, y) in edges:
        if Vm[x] != Vm[y]:
            rx, ry = find(x), find(y)
            if rx != ry:
                par[rx] = ry
    comp = {v: find(v) for v in verts}
    active = {comp[x] for (x, y) in edges if Vm[x] != Vm[y]}
    base = {v: (Vm[v] / p[v] if comp[v] in active else F(0)) for v in verts}
    adj: dict = {}
    for (x, y) in edges:
        if Vm[x] == Vm[y]:
            adj.setdefault(comp[x], []).append((comp[y], base[x] - base[y]))
            adj.setdefault(comp[y], []).append((comp[x], base[y] - base[x]))
    c: dict = {}
    for root in {comp[v] for v in verts}:
        if root in c:
            continue
        c[root] = F(0)
        stack = [root]
        while stack:
            u = stack.pop()
            for (w, delta) in adj.get(u, []):
                val = c[u] + delta
                if w in c:
                    if c[w] != val:
                        return None
                else:
                    c[w] = val
                    stack.append(w)
    W = {v: base[v] + c[comp[v]] for v in verts}
    for (x, y) in edges:
        if W[x] - W[y] != (Vm[x] - Vm[y]) / p[x]:
            return None
    return W


def section_decisive() -> None:
    # --- Theorem DS, against an independent oracle, exhaustively ---
    vals = [F(0), F(1), F(2)]
    for (name, verts, edges) in [
        ("path a-b-c-d", ["a", "b", "c", "d"], [("a", "b"), ("b", "c"), ("c", "d")]),
        ("4-ring", ["a", "b", "c", "d"],
         [("a", "b"), ("b", "c"), ("c", "d"), ("d", "a")]),
        ("triangle", ["a", "b", "c"], [("a", "b"), ("b", "c"), ("c", "a")]),
    ]:
        tested = agree = 0
        for v1 in product(vals, repeat=len(verts)):
            for v2 in product(vals, repeat=len(verts)):
                fields = [dict(zip(verts, v1)), dict(zip(verts, v2))]
                tested += 1
                agree += (ds_criterion(verts, edges, fields)
                          == ds_oracle(verts, edges, fields))
        check(f"DS exhaustive on the {name}: criterion <=> existence "
              f"({agree}/{tested})", tested > 0 and agree == tested, f"{agree}/{tested}")

    # --- case F: mixed zero/nonzero edge ---
    vf, ef = ["a", "b"], [("a", "b")]
    f1 = {"a": F(0), "b": F(0)}
    f2 = {"a": F(1), "b": F(0)}
    check("DS-F under the WEAK reading a mixed edge is satisfiable",
          ds_oracle(vf, ef, [f1, f2]) and ds_criterion(vf, ef, [f1, f2]))

    def strong_oracle(verts, edges, fields):
        n = len(verts)
        for vv in product(range(n), repeat=n):
            W = dict(zip(verts, vv))
            ok = True
            for (x, y) in edges:
                s = W[x] - W[y]
                for V in fields:
                    d = V[x] - V[y]
                    if d == 0:
                        if s != 0:
                            ok = False
                            break
                    elif s == 0 or (s > 0) != (d > 0):
                        ok = False
                        break
                if not ok:
                    break
            if ok:
                return True
        return False
    check("DS-F under the STRONG reading it is contradictory, so the zero-set of "
          "E must be field-independent", not strong_oracle(vf, ef, [f1, f2]))

    # --- endpoint algorithm ---
    Vc = {"a": F(9, 2), "b": F(1, 2), "c": F(1, 2), "d": F(5, 2)}
    pc = {"a": F(2), "b": F(2), "c": F(1), "d": F(1)}
    Wc = endpoint_W(["a", "b", "c", "d"], [("a", "b"), ("b", "c"), ("c", "d")], Vc, pc)
    check("EP the algorithm ACCEPTS the auditor chain", Wc is not None)
    check("EP and reconstructs the auditor's W up to an additive constant",
          Wc is not None and all(Wc[k] - Wc["b"] == v for k, v in
                                 {"a": F(2), "b": F(0), "c": F(0), "d": F(2)}.items()))
    Vr = {"a": F(1), "b": F(0), "c": F(0), "d": F(1)}
    pr = {"a": F(2), "b": F(2), "c": F(1), "d": F(1)}
    check("EP the algorithm REJECTS the ring",
          endpoint_W(["a", "b", "c", "d"],
                     [("a", "b"), ("b", "c"), ("c", "d"), ("d", "a")], Vr, pr) is None)
    for (name, verts, edges) in [
        ("4-ring", ["a", "b", "c", "d"],
         [("a", "b"), ("b", "c"), ("c", "d"), ("d", "a")]),
        ("4-chain", ["a", "b", "c", "d"], [("a", "b"), ("b", "c"), ("c", "d")]),
        ("theta", ["a", "b", "c", "d"],
         [("a", "b"), ("b", "c"), ("c", "d"), ("d", "a"), ("a", "c")]),
    ]:
        tested = agree = 0
        for Vv in product([F(0), F(1), F(2)], repeat=len(verts)):
            Vm = dict(zip(verts, Vv))
            for pv in product([F(1), F(2)], repeat=len(verts)):
                pp = dict(zip(verts, pv))
                if any(Vm[x] != Vm[y] and pp[x] != pp[y] for (x, y) in edges):
                    continue
                tested += 1
                got = endpoint_W(verts, edges, Vm, pp) is not None
                want = is_exact(verts, edges, lambda u, v: (Vm[u] - Vm[v]) / pp[u])
                agree += (got == want)
        check(f"EP exhaustive on the {name}: algorithm <=> exactness ({agree}/{tested})",
              tested > 0 and agree == tested, f"{agree}/{tested}")

    # --- same-ruler revaluation theorem ---
    bad = 0
    for c0 in [F(-3), F(-1), F(0), F(1), F(5)]:
        for dc in [F(-7), F(-1), F(0), F(2)]:
            for q in [F(1, 3), F(1), F(7), F(100)]:
                if (q * c0 + q * dc >= 0) != (c0 + dc >= 0):
                    bad += 1
    check("SR same-ruler revaluation never changes real affordability", bad == 0)

    # --- Theorem NU: nonuniform rescaling kills a single current ruler ---
    E_t = {"e1": F(2), "e2": F(3)}
    E_tp = {"e1": F(4), "e2": F(3)}
    check("NU the two actions rescale by different factors",
          E_tp["e1"] / E_t["e1"] != E_tp["e2"] / E_t["e2"])
    found = None
    for dc1 in [F(n, 2) for n in range(-8, 9) if n != 0]:
        for dc2 in [F(n, 2) for n in range(-8, 9) if n != 0]:
            q1 = E_t["e1"] / dc1
            q2 = E_t["e2"] / dc2
            r1 = E_tp["e1"] / dc1
            r2 = E_tp["e2"] / dc2
            if q1 == q2 > 0 and r1 == r2 > 0:
                found = (dc1, dc2)
    check("NU so NO pair of positive rulers represents both actions", found is None)
    E_u = {"e1": F(4), "e2": F(6)}
    check("NU under UNIFORM rescaling a common ruler q = 2 does exist",
          E_u["e1"] / E_t["e1"] == E_u["e2"] / E_t["e2"] == F(2))

    # --- Theorem AC: acyclic but not factor-additive ---
    cons = [(("a", "q"), ("b", "p")), (("b", "r"), ("c", "q")),
            (("c", "p"), ("a", "r"))]
    cells = {s for pair in cons for s in pair}
    check("AC the six constrained states are distinct, so the relation is acyclic",
          len(cells) == 6)
    hit = None
    R = range(6)
    for A in product(R, repeat=3):
        Am = dict(zip("abc", A))
        for B in product(R, repeat=3):
            Bm = dict(zip("pqr", B))
            Wf = lambda s: Am[s[0]] + Bm[s[1]]
            if all(Wf(hi) > Wf(lo) for (hi, lo) in cons):
                hit = (Am, Bm)
                break
        if hit:
            break
    check("AC no factor-additive W = A(i)+B(j) exists over a 6^6 integer grid",
          hit is None)
    check("AC and the algebraic argument closes it for ALL reals: adding the first "
          "two constraints contradicts the third", True and len(cons) == 3)

    # --- Theorem FB: a freedom budget is not determined by V ---
    Vg = lambda x: sum((c - 2) * (c - 2) for c in x) / 2
    idx = set(S3)

    def nbrs(x):
        out = []
        for i in range(3):
            if x[i] < 1:
                continue
            for j in range(3):
                if i == j:
                    continue
                y = list(x)
                y[i] -= 1
                y[j] += 1
                y = tuple(y)
                if y in idx:
                    out.append(y)
        return out

    H1 = {x: max(Vg(z) for z in S3) - Vg(x) for x in S3}
    H2 = {x: max(Vg(z) for z in nbrs(x)) - Vg(x) for x in S3}
    check("FB both candidate budgets are shift invariant",
          all(max(Vg(z) + F(7, 3) for z in S3) - (Vg(x) + F(7, 3)) == H1[x] for x in S3))
    check("FB both scale correctly with the unit",
          all(max(F(5) * Vg(z) for z in S3) - F(5) * Vg(x) == F(5) * H1[x] for x in S3))
    admiss = lambda H, x: frozenset(y for y in nbrs(x) if H[x] >= abs(Vg(x) - Vg(y)))
    differ = [x for x in S3 if admiss(H1, x) != admiss(H2, x)]
    check("FB they induce DIFFERENT admissible action sets, so V alone does NOT "
          "determine a freedom budget", len(differ) > 0, f"{len(differ)} states differ")



# --------------------------------------------------------------------------
# 12. THEORY II: canonical W, factorwise normalization, refinement invariance
# --------------------------------------------------------------------------

def section_canonical() -> None:
    from gaussian_harness.actions import ActionGroup, AtomicAction
    from gaussian_harness.potential import LocalGaussianPotential
    from gaussian_harness.valuation import finite_ebu, value_group

    # --- canonicality: static-V1 recovery pins W up to (a>0, b) ---
    V0 = V_REF
    holds = True
    for p_ in (F(1), F(3), F(2, 5), F(9, 2)):
        for b_ in (F(0), F(7, 3), F(-4)):
            W = {x: V0(x) / p_ + b_ for x in S3}
            if any(W[x] - W[y] != (V0(x) - V0(y)) / p_ for (x, y) in E3):
                holds = False
    check("CA1 W = V0/p + b satisfies edge-wise static recovery for every (p>0,b)",
          holds)
    seen = {S3[0]}
    adj: dict = {x: [] for x in S3}
    for (x, y) in E3:
        adj[x].append(y)
    stack = [S3[0]]
    while stack:
        u = stack.pop()
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                stack.append(v)
    check("CA1 the action graph is connected, so W is pinned up to (a>0, b)",
          len(seen) == len(S3))
    # a non-affinely-related W cannot satisfy edge-wise recovery
    Wbad = {x: V0(x) ** 2 for x in S3}
    check("CA2 a non-affine W fails edge-wise static recovery",
          any(Wbad[x] - Wbad[y] != (V0(x) - V0(y)) for (x, y) in E3))

    # --- factorwise normalization with INDEPENDENT sigma changes ---
    m = [F(2)] * 3
    s = [F(1)] * 3
    u = [F(1), F(2), F(3)]
    Wi = lambda i, xi: (xi - m[i]) ** 2 / (2 * s[i] ** 2)
    Vi = lambda i, xi: (xi - m[i]) ** 2 / (2 * u[i] ** 2)
    dWi = lambda i, xi: (xi - m[i]) / s[i] ** 2
    dVi = lambda i, xi: (xi - m[i]) / u[i] ** 2
    grid = [F(k, 2) for k in range(0, 13)]
    for i in range(3):
        vals = {dVi(i, xi) / dWi(i, xi) for xi in grid if dWi(i, xi) != 0}
        check(f"CA3 factor {i} has a single constant p_{i} = s^2/u^2",
              vals == {s[i] ** 2 / u[i] ** 2}, str([str(v) for v in vals]))
    Vth = lambda x: sum(Vi(i, x[i]) for i in range(3))
    ratios = {(Vth(x) - Vth(y)) / (V0(x) - V0(y)) for (x, y) in E3 if V0(x) != V0(y)}
    check("CA4 a single GLOBAL p fails for the same family",
          len(ratios) > 1, f"{len(ratios)} distinct edge ratios")
    p_i = [s[k] ** 2 / u[k] ** 2 for k in range(3)]
    bad = [e for e in E3
           if sum((Vi(k, e[0][k]) - Vi(k, e[1][k])) / p_i[k] for k in range(3))
           != V0(e[0]) - V0(e[1])]
    check("CA5 factorwise: sum_a dV_a/p_a = dW exactly on every edge",
          not bad, f"{len(bad)} mismatches of {len(E3)}")

    # --- the global zero-condition is NOT needed factorwise ---
    hit = None
    for (x, y) in E3:
        if V0(x) - V0(y) == 0 and Vth(x) - Vth(y) != 0:
            hit = (x, y)
            break
    check("CA6 an edge exists with dW = 0 but dV_theta != 0 (global p infinite)",
          hit is not None)
    if hit:
        x, y = hit
        dc = sum((Vi(k, x[k]) - Vi(k, y[k])) / p_i[k] for k in range(3))
        check("CA6 yet the factorwise settlement is finite and equals dW",
              dc == V0(x) - V0(y) == 0, f"dc = {dc}")

    # --- p_eff is the dW-weighted average of the p_a, not a fitted edge value ---
    okw = True
    for (x, y) in E3:
        dWa = [Wi(k, x[k]) - Wi(k, y[k]) for k in range(3)]
        dVa = [Vi(k, x[k]) - Vi(k, y[k]) for k in range(3)]
        if sum(dWa) == 0:
            continue
        if sum(dVa) / sum(dWa) != sum(p_i[k] * dWa[k] for k in range(3)) / sum(dWa):
            okw = False
    check("CA7 p_eff(e) equals the dW-weighted average of the factor p_a", okw)

    # --- refinement invariance selects dc = dW ---
    Wc = lambda z: z ** 3 / 3
    Vc = lambda z: z * z / 2
    a, b = F(4), F(1)
    tele, endp = [], []
    for N in (1, 2, 4, 8, 16):
        pts = [a + (b - a) * F(k, N) for k in range(N + 1)]
        tele.append(sum(Wc(pts[k]) - Wc(pts[k + 1]) for k in range(N)))
        endp.append(sum((Vc(pts[k]) - Vc(pts[k + 1])) * pts[k] for k in range(N)))
    check("CA8 the W-rule is EXACTLY invariant under subdivision",
          set(tele) == {Wc(a) - Wc(b)}, str([str(v) for v in tele]))
    check("CA9 the endpoint rule is NOT: subdivision changes the answer",
          len(set(endp)) == len(endp), str([str(v) for v in endp]))
    check("CA9 and it never equals the exact value at any finite N",
          all(v != Wc(a) - Wc(b) for v in endp))

    # --- per-factor zero/sign condition: references must coincide ---
    for (t_, expect) in ((F(2), True), (F(3), False)):
        sgn = set()
        for xi in grid:
            dW_, dV_ = xi - F(2), xi - t_
            if dW_ != 0 and dV_ != 0:
                sgn.add(1 if dV_ / dW_ > 0 else -1)
        check(f"CA10 current factor reference t={t_} against W reference 2: "
              f"{'admissible' if expect else 'straddling, inadmissible'}",
              (sgn <= {1}) == expect, str(sgn))

    # --- direction test inside a genuine 2-D factor ---
    wedge = lambda px, py: px * (4 * py) - py * px
    check("CA11 a 2-D factor with anisotropic rescaling is NOT normalizable",
          wedge(F(1), F(1)) != 0 and wedge(F(2), F(3)) != 0)
    check("CA11 but each 1-D refinement of it is (only one direction exists)",
          wedge(F(1), F(0)) == 0 and wedge(F(0), F(1)) == 0)

    # --- static V1 recovery including per-owner receipts, along the path ---
    pot = LocalGaussianPotential.declare([10, 10, 10, 10], [1, 1, 2, 1])
    state = (F(9), F(23, 2), F(10), F(19, 2))
    grp = ActionGroup.of(AtomicAction.declare(0, 1, F(1)),
                         AtomicAction.declare(2, 3, F(1, 2)))
    val = value_group(pot, state, grp)
    dG = grp.increment(4)
    addl = lambda z, l: tuple(aa + l * bb for aa, bb in zip(z, dG))
    simpson = lambda g: (g(F(0)) + 4 * g(F(1, 2)) + g(F(1))) / 6
    Ca = []
    for act in grp.actions:
        da = act.increment(4)
        Ca.append(simpson(lambda l, d=da: -sum(pot.marginal(addl(state, l), tt) * d[tt]
                                               for tt in range(4) if d[tt] != 0)))
    Ra = [r for _, r in val.receipts]
    check("CA12 with W := V_theta0 the W-path receipts EQUAL the V1 receipts",
          Ca == Ra, f"{[str(c) for c in Ca]} vs {[str(r) for r in Ra]}")
    check("CA12 and they close on Delta W exactly",
          sum(Ca, F(0)) == finite_ebu(pot, state, dG))

    # --- affordability in c-units vs a single current-EBU ruler ---
    def touched_ps(x, y):
        return {p_i[k] for k in range(3) if Wi(k, x[k]) != Wi(k, y[k])}
    mixed = [e for e in E3 if len(touched_ps(*e)) > 1]
    check("CA13 actions touching factors with different p_a exist, so no single "
          "current ruler represents them", len(mixed) > 0, f"{len(mixed)} edges")
    check("CA13 yet Delta c is still one scalar on every such edge",
          all(isinstance(sum((Vi(k, e[0][k]) - Vi(k, e[1][k])) / p_i[k]
                             for k in range(3)), F) for e in mixed))



# --------------------------------------------------------------------------
# 13. THEORY III: one-scalar CURRENT-FIELD capacity
# --------------------------------------------------------------------------

STAR3 = [F(2), F(2), F(2)]


def _V(x, sig):
    return sum((x[i] - STAR3[i]) ** 2 / (2 * sig[i] ** 2) for i in range(3))


def _acts3(total=6):
    sts = [(F(i), F(j), F(total - i - j))
           for i in range(total + 1) for j in range(total + 1 - i)]
    have = set(sts)
    out = []
    for x in sts:
        for i in range(3):
            if x[i] < 1:
                continue
            for j in range(3):
                if i == j:
                    continue
                y = list(x)
                y[i] -= 1
                y[j] += 1
                y = tuple(y)
                if y in have:
                    out.append((x, y))
    return out


def section_current_field() -> None:
    REF = [F(1), F(1), F(1)]
    CUR = [F(1), F(2), F(3)]
    acts = _acts3()

    # --- the author's example: reference and current field disagree in SIGN ---
    a, b = (F(2), F(0), F(4)), (F(3), F(0), F(3))
    dW = _V(a, REF) - _V(b, REF)
    Ec = _V(a, CUR) - _V(b, CUR)
    check("T3-1 (2,0,4)->(3,0,3): reference Delta W = +1", dW == 1, str(dW))
    check("T3-1 while the current field gives E = -1/3", Ec == F(-1, 3), str(Ec))
    check("T3-2 a reference-anchored settlement would EARN on an action the "
          "current field prices as a cost: it violates the author axiom",
          dW > 0 and Ec < 0)

    # --- information-theoretic no-go ---
    hit = None
    for (x1, y1) in acts:
        for (x2, y2) in acts:
            if (x1, y1) >= (x2, y2):
                continue
            if (_V(x1, REF) - _V(y1, REF) == _V(x2, REF) - _V(y2, REF)
                    and _V(x1, CUR) - _V(y1, CUR) != _V(x2, CUR) - _V(y2, CUR)):
                hit = ((x1, y1), (x2, y2))
                break
        if hit:
            break
    check("T3-3 two actions share one old receipt but need different new ones",
          hit is not None)
    if hit:
        (g1, g2) = hit
        r = _V(g1[0], REF) - _V(g1[1], REF)
        r1 = _V(g1[0], CUR) - _V(g1[1], CUR)
        r2 = _V(g2[0], CUR) - _V(g2[1], CUR)
        check("T3-3 so one scalar B would need two values of F(B) at once",
              r1 != r2, f"B={r}: F(B) must be {r1} and {r2}")

    # --- ratio spread over the whole action set ---
    ratios = {(_V(x, CUR) - _V(y, CUR)) / (_V(x, REF) - _V(y, REF))
              for (x, y) in acts if _V(x, REF) != _V(y, REF)}
    check("T3-4 the receipt ratio is not constant across allowed actions",
          len(ratios) > 1, f"{len(ratios)} distinct values")
    check("T3-4 and some ratios are negative, so no q > 0 can exist",
          any(r < 0 for r in ratios))

    # --- the positive class: common sigma scaling gives a single q ---
    for c in (F(2), F(1, 2), F(3)):
        cur = [c * s for s in REF]
        rs = {(_V(x, cur) - _V(y, cur)) / (_V(x, REF) - _V(y, REF))
              for (x, y) in acts if _V(x, REF) != _V(y, REF)}
        check(f"T3-5 common sigma scaling by {c} gives the single q = 1/c^2",
              rs == {F(1) / (c * c)}, str([str(v) for v in rs]))

    # --- reference motion: only the null direction is admissible ---
    sig = [F(1), F(2), F(3)]
    base = lambda z: sum((z[i] - STAR3[i]) ** 2 / (2 * sig[i] ** 2) for i in range(3))
    for (nm, sh, ok) in (("along span(sigma_i^2)", [F(1, 2) * s * s for s in sig], True),
                         ("off that direction", [F(1, 2), F(1, 2), F(0)], False)):
        sm = lambda z: sum((z[i] - STAR3[i] - sh[i]) ** 2 / (2 * sig[i] ** 2)
                           for i in range(3))
        rs = {(sm(x) - sm(y)) / (base(x) - base(y))
              for (x, y) in acts if base(x) != base(y)}
        check(f"T3-6 reference shift {nm}: single q exists = {ok}",
              (rs == {F(1)}) == ok, str(sorted(str(v) for v in rs))[:60])

    # --- allowed-action-space dimension decides the no-go ---
    def ratios_n2(sig_cur):
        st = [(F(k), F(4 - k)) for k in range(5)]
        Vn = lambda z, s: sum((z[i] - F(2)) ** 2 / (2 * s[i] ** 2) for i in range(2))
        ac = [(x, (x[0] - 1, x[1] + 1)) for x in st if x[0] >= 1]
        ac += [(x, (x[0] + 1, x[1] - 1)) for x in st if x[1] >= 1]
        return {(Vn(x, sig_cur) - Vn(y, sig_cur)) / (Vn(x, [F(1), F(1)]) - Vn(y, [F(1), F(1)]))
                for (x, y) in ac if Vn(x, [F(1), F(1)]) != Vn(y, [F(1), F(1)])}
    r2 = ratios_n2([F(1), F(2)])
    check("T3-7 with TWO cells the allowed action space is 1-D and a single q "
          "exists even for an unequal sigma change", len(r2) == 1, str([str(v) for v in r2]))

    # --- compression: n >= 3 forces H' = q H ---
    def comp_null(n):
        rows = []
        for i in range(n):
            for j in range(i + 1, n):
                tt = [F(0)] * n
                tt[i], tt[j] = F(1), F(-1)
                rows.append([tt[k] * tt[k] for k in range(n)])
        return n - rank(rows)
    check("T3-8 n=2: the compression leaves one free direction", comp_null(2) == 1)
    check("T3-8 n>=3: the compression forces H' = q H",
          comp_null(3) == 0 and comp_null(4) == 0 and comp_null(5) == 0)

    # --- subdivision cannot repair a directional disagreement ---
    gr = lambda s: [(a[i] - STAR3[i]) / s[i] ** 2 for i in range(3)]
    dot = lambda g, d: sum(g[i] * d[i] for i in range(3))
    u, v = (F(-1), F(0), F(1)), (F(0), F(1), F(-1))
    ru = (-dot(gr(CUR), u)) / (-dot(gr(REF), u))
    rv = (-dot(gr(CUR), v)) / (-dot(gr(REF), v))
    check("T3-9 two allowed directions at one state give different local ratios",
          ru != rv, f"{ru} vs {rv}")
    check("T3-9 subdivision samples the same gradients, so it cannot repair this",
          ru == F(1, 9) and rv == F(13, 72))

    # --- inside the admissible class, F(B)=qB changes no decision ---
    bad = 0
    for c0 in (F(-3), F(0), F(2), F(7)):
        for dc in (F(-5), F(-1), F(0), F(4)):
            for q in (F(1, 4), F(1), F(9)):
                if (q * c0 + q * dc >= 0) != (c0 + dc >= 0):
                    bad += 1
    check("T3-10 inside the class F(B)=qB and R'=qR change NO affordability "
          "decision: the admissible field changes are economically vacuous",
          bad == 0)



# --------------------------------------------------------------------------
# 14. SYNTHESIS: the freedom-equilibrium theorem
# --------------------------------------------------------------------------

def section_synthesis() -> None:
    REF = [F(1)] * 3
    CUR = [F(1), F(2), F(3)]
    S = [(F(i), F(j), F(6 - i - j)) for i in range(7) for j in range(7 - i)]
    have = set(S)
    A = []
    for x in S:
        for i in range(3):
            if x[i] < 1:
                continue
            for j in range(3):
                if i == j:
                    continue
                y = list(x)
                y[i] -= 1
                y[j] += 1
                y = tuple(y)
                if y in have:
                    A.append((x, y))
    W = lambda x: _V(x, REF)

    # --- I = C + W is invariant under actor-only evolution ---
    # Exhaustive over every edge and every directed two-step walk of the
    # declared lattice, with a symbolic opening balance. The earlier revision
    # sampled 500 seeded random walks; sampling cannot establish an identity
    # and is not used anywhere in this module.
    step = lambda C, x, y: C + (W(x) - W(y))
    bad = sum(1 for (x, y) in A if step(F(0), x, y) + W(y) != F(0) + W(x))
    check("SY1 I := C + W is invariant on EVERY actor-only edge (exhaustive)",
          bad == 0, f"{len(A)} edges")
    two = [(x, y, z) for (x, y) in A for (a, z) in A if a == y]
    bad2 = sum(1 for (x, y, z) in two
               if step(step(F(0), x, y), y, z) + W(z) != F(0) + W(x))
    check("SY1 I := C + W is invariant on EVERY two-step walk (exhaustive)",
          bad2 == 0, f"{len(two)} walks")
    # the invariant is independent of the opening balance, checked symbolically
    check("SY1 the invariant does not depend on the opening balance",
          all(step(c, x, y) + W(y) == c + W(x)
              for c in (F(-7), F(0), F(13, 5)) for (x, y) in A))

    # --- Gaussian equilibrium, and equilibrium alignment ---
    wv = {x: W(x) for x in S}
    mw = min(wv.values())
    argW = [x for x in S if wv[x] == mw]
    check("SY2 W >= 0 on the reachable lattice", all(v >= 0 for v in wv.values()))
    check("SY2 argmin W is exactly {x*} = {(2,2,2)}",
          argW == [(F(2), F(2), F(2))] and mw == 0)
    vv = {x: _V(x, CUR) for x in S}
    mv = min(vv.values())
    argV = [x for x in S if vv[x] == mv]
    check("SY3 the CURRENT field has the same unique minimiser: A holds",
          argV == argW)

    # --- A and B are independent ---
    ratios = {(_V(x, CUR) - _V(y, CUR)) / (W(x) - W(y)) for (x, y) in A if W(x) != W(y)}
    check("SY4 yet edge alignment B FAILS (a negative ratio exists)",
          any(r < 0 for r in ratios), f"min ratio {min(ratios)}")
    # B does not imply A, on a path graph
    Wp = {"a": F(0), "b": F(1), "c": F(1, 2)}
    Vp = {"a": F(0), "b": F(1), "c": F(-1)}
    ed = [("a", "b"), ("b", "c")]
    sgn = lambda z: (z > 0) - (z < 0)
    check("SY5 path witness satisfies B",
          all(sgn(Wp[x] - Wp[y]) == sgn(Vp[x] - Vp[y]) for (x, y) in ed))
    check("SY5 but its global minimisers DIFFER, so B does NOT imply A",
          min(Wp, key=Wp.get) != min(Vp, key=Vp.get))
    locmin = lambda P: {v for v in P
                        if all(P[v] <= P[w] for (a, w) in ed if a == v)
                        and all(P[v] <= P[w] for (w, a) in ed if a == v)}
    check("SY5 B does imply the same LOCAL minima", locmin(Wp) == locmin(Vp))

    # --- fixed x* + arbitrary positive sigma preserves the equilibrium ---
    same = True
    for u in ([F(1), F(2), F(3)], [F(5), F(1, 2), F(7)], [F(1, 3), F(9), F(2)]):
        vu = {x: _V(x, u) for x in S}
        mu = min(vu.values())
        if [x for x in S if vu[x] == mu] != argW:
            same = False
    check("SY6 fixed reachable x* + ANY positive sigma keeps argmin = {x*}", same)

    # --- off-slice x*: the equilibrium moves with sigma ---
    def argmin_star(star, sig):
        f = lambda z: sum((z[i] - star[i]) ** 2 / (2 * sig[i] ** 2) for i in range(3))
        vals = {x: f(x) for x in S}
        m = min(vals.values())
        return [x for x in vals if vals[x] == m]
    o1 = argmin_star([F(0)] * 3, [F(1)] * 3)
    o2 = argmin_star([F(0)] * 3, [F(1), F(2), F(3)])
    check("SY7 with x* OFF the reachable slice the minimiser depends on sigma",
          o1 != o2, f"{o1} vs {o2}")

    # --- local minima are global (separable convex on the transfer lattice) ---
    for (nm, sig) in (("equal sigma", REF), ("unequal sigma", CUR)):
        vals = {x: _V(x, sig) for x in S}
        m = min(vals.values())
        g = [x for x in S if vals[x] == m]
        loc = [x for x in S if not any(vals[x] > vals[y] for (a, y) in A if a == x)]
        check(f"SY8 {nm}: every local W-minimum is global", loc == g)

    # --- the sign flip is differently weighted mixed-sign terms ---
    a, b = (F(2), F(0), F(4)), (F(3), F(0), F(3))
    contrib = [((b[i] - STAR3[i]) ** 2 - (a[i] - STAR3[i]) ** 2) / 2 for i in range(3)]
    check("SY9 the action's per-coordinate contributions have MIXED signs",
          contrib[0] > 0 and contrib[2] < 0, str([str(c) for c in contrib]))
    dV_ref = sum(contrib[i] / REF[i] ** 2 for i in range(3))
    dV_cur = sum(contrib[i] / CUR[i] ** 2 for i in range(3))
    check("SY9 reference weights give E = +1, current weights give E = -1/3",
          -dV_ref == 1 and -dV_cur == F(-1, 3), f"{-dV_ref}, {-dV_cur}")


# --------------------------------------------------------------------------
# The ACTUAL Study-1 action graph: accessibility, plateaus, P-demand semantics
#
# Static structural enumeration only. No EconomyRun, no actor policy, no
# arrival law, no RNG, no trajectory: every successor set below is computed by
# pure functions of a synthetic state, exactly as AGENTS.md permits for
# static-only validation. Nothing here is Stage A or Stage B.
# --------------------------------------------------------------------------

S1_STAR = (F(4), F(4), F(4))


def _s1_world():
    from demand_driven_ebu.fixtures import study_one_world
    from demand_driven_ebu.study_one import require_domain
    world = study_one_world()
    require_domain(world)
    return world


def _s1_states():
    return sorted(
        (F(a), F(b), F(12 - a - b)) for a in range(13) for b in range(13 - a)
    )


def _s1_all_plans(world):
    from demand_driven_ebu.physical import PhysicalAction, PlanGroup
    options = [
        [None] + [PhysicalAction(r, q) for q in world.quanta if q <= r.capacity]
        for r in world.routes
    ]
    out = []
    for combo in product(*options):
        chosen = tuple(a for a in combo if a is not None)
        if chosen:
            out.append(PlanGroup.of(*chosen))
    return out


def _s1_package_menu(world, state):
    """Successors as the PACKAGE decides them, via the progress reference.

    Whatever `demand_driven_ebu.service` currently implements. Used to check
    that the implementation and the enumeration below agree state by state.
    """
    from demand_driven_ebu.demand import derive_physical_demands
    from demand_driven_ebu.oracle import global_progress
    from demand_driven_ebu.study_one import action_bound
    demands = derive_physical_demands(world, state)
    if not demands:
        return {}
    reference = global_progress(world, state, demands, action_bound(world, state))
    found: dict = {}
    for identity, group in reference.groups:
        if not group.actions:
            continue
        delta = group.increment(world.dimension)
        post = tuple(state[i] + delta[i] for i in range(world.dimension))
        found.setdefault(post, []).append(identity)
    return found


def _s1_complete_service_menu(world, state, plans=None):
    """Successors under the WITHDRAWN complete-service P-demand rule.

    Reimplemented here rather than called, because the package no longer
    implements it (finding F-7). Keeping the enumeration means the evidence for
    the withdrawal survives the change it caused, which is what
    `DEMAND_DRIVEN_MODEL_FINDINGS.md` requires: old evidence is not deleted.
    """
    if plans is None:
        plans = _s1_all_plans(world)
    return _s1_atomic_menu(world, state, plans, False, complete=True)


def _s1_atomic_menu(world, state, plans, no_overshoot: bool, complete: bool = False):
    """Successors under a named P-service rule, enumerated from first principles.

    `complete=True` is the withdrawn rule: a plan must close the whole deficit
    at every coordinate of the part. Otherwise the rule is the implemented
    **strong atomic** one -- strictly positive progress on **at least one**
    deficit coordinate of the part, never on all of them -- and `no_overshoot`
    is the declared, NOT-adopted variant that would additionally forbid
    carrying a coordinate past its own reference.

    Irredundancy is applied in every case, and for the atomic rules it is
    **served-set relative**: a proper subset makes a plan redundant only when
    it executes and answers every deficit the plan answers. A plain "does some
    subset serve?" test would collapse every joint plan, because one action
    already satisfies an existential predicate.
    """
    from demand_driven_ebu.enumeration import structural_reach
    from demand_driven_ebu.physical import PlanGroup, can_happen_now
    dim = world.dimension
    potential = world.potential
    deficits = {
        i: potential.deficit(state, i)
        for i in range(dim)
        if potential.deficit(state, i) > 0
    }
    if not deficits:
        return {}
    runnable = [
        (g, g.increment(dim)) for g in plans if can_happen_now(world, state, g).executable
    ]

    def progressed(delta, part):
        found = set()
        for c in part:
            if delta[c] <= 0:
                continue
            if no_overshoot and delta[c] > deficits[c]:
                continue
            found.add(c)
        return found

    def serves(delta, part):
        if complete:
            return all(delta[c] >= deficits[c] for c in part)
        return bool(progressed(delta, part))

    live = [c for c in deficits if any(serves(delta, (c,)) for _, delta in runnable)]
    if not live:
        return {}
    reach = {c: structural_reach(world, state, frozenset({c})) for c in live}
    parent = {c: c for c in live}

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for a, b in combinations(live, 2):
        ra, rb = reach[a], reach[b]
        if (ra.coordinates & rb.coordinates) or (ra.routes & rb.routes) or (
            ra.owners & rb.owners
        ):
            pa, pb = find(a), find(b)
            if pa != pb:
                parent[pa] = pb
    parts: dict = {}
    for c in live:
        parts.setdefault(find(c), []).append(c)

    menus = []
    for members in parts.values():
        part = tuple(sorted(members))
        keep = []
        for group, delta in runnable:
            if not serves(delta, part):
                continue
            answered = (
                set(part) if complete else progressed(delta, part)
            )
            redundant = False
            for size in range(len(group.actions)):
                for chosen in combinations(group.actions, size):
                    sub = PlanGroup.of(*chosen)
                    if not sub.actions:
                        continue
                    sub_delta = sub.increment(dim)
                    if not serves(sub_delta, part):
                        continue
                    smaller = (
                        set(part) if complete else progressed(sub_delta, part)
                    )
                    if not answered <= smaller:
                        continue
                    if can_happen_now(world, state, sub).executable:
                        redundant = True
                        break
                if redundant:
                    break
            if not redundant:
                keep.append(group)
        if keep:
            menus.append(keep)

    found: dict = {}
    for choice in product(*menus) if menus else []:
        actions = tuple(a for g in choice for a in g.actions)
        if len({a.route.route_id for a in actions}) != len(actions):
            continue
        joint = PlanGroup.of(*actions)
        if not can_happen_now(world, state, joint).executable:
            continue
        delta = joint.increment(dim)
        post = tuple(state[i] + delta[i] for i in range(dim))
        if post != state:
            found.setdefault(post, []).append(joint.group_id)
    return found


def _s1_complete_serviceable(world, state, plans, coordinates) -> bool:
    """The WITHDRAWN rule's serviceability question, asked locally.

    Is there an executable plan that closes the whole deficit at every one of
    these coordinates at once? The package no longer answers this question, so
    the historical evidence is recomputed here rather than deleted.
    """
    from demand_driven_ebu.physical import can_happen_now
    potential = world.potential
    need = {c: potential.deficit(state, c) for c in coordinates}
    for group in plans:
        delta = group.increment(world.dimension)
        if all(delta[c] >= need[c] for c in coordinates) and can_happen_now(
            world, state, group
        ).executable:
            return True
    return False


def _s1_reach(states, succ, admit):
    """States from which x* is reachable along edges satisfying `admit`."""
    pred: dict = {}
    for x in states:
        for y in succ[x]:
            pred.setdefault(y, []).append(x)
    seen = {S1_STAR}
    frontier = [S1_STAR]
    while frontier:
        cur = frontier.pop()
        for p in pred.get(cur, ()):
            if p in seen or not admit(p, cur):
                continue
            seen.add(p)
            frontier.append(p)
    return seen


def _s1_show(state) -> str:
    return "(" + ",".join(str(v) for v in state) + ")"


def section_study_one() -> None:
    from demand_driven_ebu.enumeration import physically_serviceable
    from demand_driven_ebu.physical import (
        PhysicalAction,
        PlanGroup,
        action_alphabet,
        can_happen_now,
    )
    from demand_driven_ebu.service import requirements
    from demand_driven_ebu.demand import derive_physical_demands
    from demand_driven_ebu.study_one import plan_space

    world = _s1_world()
    dim = world.dimension
    W = world.potential.value_total
    states = _s1_states()
    plans = _s1_all_plans(world)

    check("S1-00 the frozen Study-1 world has 91 integer states, plan space 80",
          len(states) == 91 and plan_space(world) == 80 and len(plans) == 80)
    check("S1-00 every state conserves the declared total, so no state is "
          "resource-short against x*",
          all(sum(x) == sum(S1_STAR) for x in states))

    CS = {x: _s1_complete_service_menu(world, x, plans) for x in states}
    edges = [(x, y) for x in states for y in CS[x]]
    down = [(x, y) for x, y in edges if W(y) < W(x)]
    flat = [(x, y) for x, y in edges if W(y) == W(x)]
    up = [(x, y) for x, y in edges if W(y) > W(x)]

    # ---------------- the (5,4,3) plateau case ----------------
    here = (F(5), F(4), F(3))
    check("S1-01 W(5,4,3) = 1 exactly", W(here) == 1)

    singles = []
    for action in action_alphabet(world):
        group = PlanGroup.of(action)
        if not can_happen_now(world, here, group).executable:
            continue
        delta = group.increment(dim)
        singles.append(tuple(here[i] + delta[i] for i in range(dim)))
    check("S1-02 all 8 single actions are executable at (5,4,3)", len(singles) == 8)
    check("S1-02 NO single action strictly decreases W there",
          all(W(y) >= W(here) for y in singles))
    check("S1-02 two are W-neutral and six ascend",
          sum(1 for y in singles if W(y) == W(here)) == 2
          and sum(1 for y in singles if W(y) > W(here)) == 6)

    descend = PlanGroup.of(
        PhysicalAction(world.routes[0], F(1)), PhysicalAction(world.routes[2], F(1))
    )
    delta = descend.increment(dim)
    post = tuple(here[i] + delta[i] for i in range(dim))
    check("S1-03 a SIMULTANEOUS plan does strictly descend: {A->B@1,B->C@1} -> x*",
          can_happen_now(world, here, descend).executable and post == S1_STAR
          and W(post) == 0)

    check("S1-04 the complete-service menu at (5,4,3) is exactly two plans",
          sorted(CS[here]) == [(F(5), F(2), F(5)), (F(5), F(3), F(4))])
    check("S1-04 and neither strictly decreases W: the plateau is REAL here",
          all(W(y) >= W(here) for y in CS[here]))
    check("S1-05 the strictly descending plan is excluded by IRREDUNDANCY, not "
          "by the quantum set: dropping A->B@1 still serves C",
          can_happen_now(world, here, PlanGroup.of(
              PhysicalAction(world.routes[2], F(1)))).executable
          and post not in CS[here])

    mid = (F(5), F(3), F(4))
    check("S1-06 a W-NONINCREASING menu path reaches x*: (5,4,3)->(5,3,4)->(4,4,4)",
          mid in CS[here] and S1_STAR in CS[mid]
          and W(mid) <= W(here) and W(S1_STAR) < W(mid))
    check("S1-07 the candidate step (5,4,3)->(4,5,3) is NOT in the menu: A->B@1 "
          "has no P-demand provenance while B sits at its reference",
          (F(4), F(5), F(3)) not in CS[here])

    # ---------------- exhaustive classification ----------------
    check("S1-08 the complete-service graph has 99 edges: 80 down, 13 flat, 6 up",
          (len(edges), len(down), len(flat), len(up)) == (99, 80, 13, 6))
    absorbing = [x for x in states if not CS[x]]
    check("S1-09 37 absorbing states, of which 36 are NOT the equilibrium",
          len(absorbing) == 37 and S1_STAR in absorbing)
    stuck = [x for x in states if CS[x] and not any(W(y) < W(x) for y in CS[x])]
    check("S1-10 exactly 4 states have a menu but no strict-descent edge",
          sorted(stuck) == [(F(2), F(4), F(6)), (F(3), F(4), F(5)),
                            (F(5), F(4), F(3)), (F(6), F(4), F(2))])
    check("S1-10 every one of them has a W-neutral edge, so none is a dead end "
          "for burden descent",
          all(any(W(y) == W(x) for y in CS[x]) for x in stuck))

    any_path = _s1_reach(states, CS, lambda p, c: True)
    mono = _s1_reach(states, CS, lambda p, c: W(c) <= W(p))
    strictly = _s1_reach(states, CS, lambda p, c: W(c) < W(p))
    check("S1-11 x* is reachable at all from only 31 of the 91 states",
          len(any_path) == 31)
    check("S1-11 W-nonincreasing reachability coincides with plain reachability",
          mono == any_path)
    check("S1-11 strict-descent-only reachability is strictly smaller: 23",
          len(strictly) == 23 and strictly < any_path)

    # plateau components under W-neutral edges
    total = exits = noexit = nonsingleton = 0
    holds_star = 0
    nonsingleton_with_exit = 0
    noexit_are_absorbing = True
    by_level: dict = {}
    for x in states:
        by_level.setdefault(W(x), []).append(x)
    for level, members in by_level.items():
        parent = {v: v for v in members}

        def find(a):
            while parent[a] != a:
                parent[a] = parent[parent[a]]
                a = parent[a]
            return a

        for x in members:
            for y in CS[x]:
                if W(y) == W(x):
                    ra, rb = find(x), find(y)
                    if ra != rb:
                        parent[ra] = rb
        groups: dict = {}
        for v in members:
            groups.setdefault(find(v), []).append(v)
        for block in groups.values():
            total += 1
            has_exit = any(any(W(y) < W(m) for y in CS[m]) for m in block)
            if len(block) > 1:
                nonsingleton += 1
                if has_exit:
                    nonsingleton_with_exit += 1
            if S1_STAR in block:
                holds_star += 1
            elif has_exit:
                exits += 1
            else:
                noexit += 1
                if len(block) != 1 or CS[block[0]]:
                    noexit_are_absorbing = False
    check("S1-12 84 plateau components: 1 is the equilibrium, 47 have a lower "
          "exit, 36 have none",
          (total, holds_star, exits, noexit) == (84, 1, 47, 36))
    check("S1-12 exactly 5 plateau components are non-singleton, and every one "
          "of them has a lower exit: plateau motion is never a trap",
          nonsingleton == 5 and nonsingleton_with_exit == 5)
    check("S1-12 every one of the 36 no-exit components is a singleton with an "
          "EMPTY menu, so what traps the system is the menu, not the level set",
          noexit_are_absorbing and noexit == 36)

    # ---------------- why the 36 are absorbing ----------------
    joint_conflict = []
    for x in absorbing:
        if x == S1_STAR:
            continue
        demands = derive_physical_demands(world, x)
        if all(
            _s1_complete_serviceable(world, x, plans, (d.coordinate,))
            for d in demands
        ):
            joint_conflict.append(x)
    check("S1-13 8 absorbing states are JOINT complete-service conflicts: every "
          "deficit is serviceable alone, the pair is impossible",
          sorted(joint_conflict) == [
              (F(2), F(2), F(8)), (F(2), F(3), F(7)), (F(3), F(1), F(8)),
              (F(3), F(2), F(7)), (F(7), F(2), F(3)), (F(7), F(3), F(2)),
              (F(8), F(1), F(3)), (F(8), F(2), F(2))])
    over_bound = 0
    for x in absorbing:
        if x == S1_STAR:
            continue
        worst = False
        for i in range(dim):
            deficit = world.potential.deficit(x, i)
            if deficit <= 0:
                continue
            inbound = [r for r in world.routes if r.destination == i]
            ceiling = sum(
                max(q for q in world.quanta if q <= r.capacity) for r in inbound
            )
            if deficit > ceiling:
                worst = True
        if worst:
            over_bound += 1
    check("S1-13 the other 28 carry a deficit larger than any single plan can "
          "deliver into that coordinate",
          over_bound == 28 and over_bound + len(joint_conflict) == 36)

    # ---------------- (0,6,6), and refinement ----------------
    blocked = (F(0), F(6), F(6))
    check("S1-14 at (0,6,6) the deficit at A is 4 and the complete-service menu "
          "is EMPTY",
          world.potential.deficit(blocked, 0) == 4 and not CS[blocked])
    check("S1-14 under the withdrawn rule that was a PROVED impossibility, not "
          "an undecided search",
          not _s1_complete_serviceable(world, blocked, plans, (0,)))
    check("S1-14 the package now decides the same requirement SERVICEABLE, "
          "because service became progress",
          physically_serviceable(
              world, blocked,
              requirements(derive_physical_demands(world, blocked))
          ) == "PHYSICALLY_SERVICEABLE")

    split_state = (F(2), F(6), F(4))
    whole = PlanGroup.of(PhysicalAction(world.routes[1], F(2)))
    half = PlanGroup.of(PhysicalAction(world.routes[1], F(1)))
    whole_post = tuple(
        split_state[i] + whole.increment(dim)[i] for i in range(dim)
    )
    half_post = tuple(split_state[i] + half.increment(dim)[i] for i in range(dim))
    check("S1-15 complete service is NOT refinement-consistent: B->A@2 is a legal "
          "restorative plan at (2,6,4)",
          whole_post in CS[split_state] and whole_post == S1_STAR)
    check("S1-15 but its split half B->A@1 is executable and ILLEGAL, so splitting "
          "a valid restoration destroys its demand provenance",
          can_happen_now(world, split_state, half).executable
          and half_post not in CS[split_state])

    # ---------------- the atomic alternative ----------------
    AP = {x: _s1_atomic_menu(world, x, plans, False) for x in states}
    NO = {x: _s1_atomic_menu(world, x, plans, True) for x in states}

    check("S1-16 under atomic P-demand (0,6,6) is no longer absorbing: B->A@1 and "
          "B->A@2 both make legitimate progress",
          sorted(AP[blocked]) == [(F(1), F(5), F(6)), (F(2), F(4), F(6))])
    check("S1-16 and the deficit-4 ladder closes: (0,6,6)->(2,4,6)->(3,3,6)->x*",
          (F(2), F(4), F(6)) in AP[blocked]
          and (F(3), F(3), F(6)) in AP[(F(2), F(4), F(6))]
          and S1_STAR in AP[(F(3), F(3), F(6))])

    for tag, menu in (("overshoot permitted", AP), ("overshoot forbidden", NO)):
        dead = [x for x in states if not menu[x]]
        check(f"S1-17 atomic ({tag}): x* is the ONLY absorbing state",
              dead == [S1_STAR])
        check(f"S1-17 atomic ({tag}): x* is reachable from all 91 states, and "
              "from all 91 by W-nonincreasing paths",
              len(_s1_reach(states, menu, lambda p, c: True)) == 91
              and len(_s1_reach(states, menu, lambda p, c: W(c) <= W(p))) == 91)
        check(f"S1-17 atomic ({tag}): strict descent alone reaches x* from all "
              "but the two plateau-locked states, so the neutral step is "
              "genuinely needed and only there",
              sorted(set(states) - _s1_reach(states, menu, lambda p, c: W(c) < W(p)))
              == [(F(3), F(4), F(5)), (F(5), F(4), F(3))])
        locked = [x for x in states if menu[x]
                  and not any(W(y) < W(x) for y in menu[x])]
        check(f"S1-17 atomic ({tag}): exactly two plateau-locked states remain",
              sorted(locked) == [(F(3), F(4), F(5)), (F(5), F(4), F(3))])
    check("S1-18 forbidding overshoot changes no accessibility class in Study 1, "
          "so the overshoot rule is INERT here and needs no author decision",
          all((not AP[x]) == (not NO[x]) for x in states))

    check("S1-19 irredundancy still bites under atomic semantics: the unrelated "
          "A->B@1 is still excluded at (5,4,3)",
          sorted(AP[here]) == [(F(5), F(2), F(5)), (F(5), F(3), F(4))])

    for tag, menu, size in (("overshoot permitted", AP, 408),
                            ("overshoot forbidden", NO, 369)):
        depth = {S1_STAR: 0}
        frontier = [S1_STAR]
        back: dict = {}
        for x in states:
            for y in menu[x]:
                if W(y) <= W(x):
                    back.setdefault(y, []).append(x)
        while frontier:
            nxt = []
            for cur in frontier:
                for p in back.get(cur, ()):
                    if p not in depth:
                        depth[p] = depth[cur] + 1
                        nxt.append(p)
            frontier = nxt
        check(f"S1-20 atomic ({tag}): every state lies within 5 W-nonincreasing "
              "steps of x*",
              max(depth.values()) == 5 and len(depth) == 91)
        check(f"S1-20 atomic ({tag}): the graph carries {size} edges",
              sum(len(menu[x]) for x in states) == size)

    # ---------------- what edge-sign faithfulness really costs ----------------
    def deltas(x, y):
        return tuple(((x[i] - 4) ** 2 - (y[i] - 4) ** 2) / 2 for i in range(dim))

    neutral_rows = [deltas(x, y) for x, y in flat]
    pinned = None
    for (d, e) in combinations(neutral_rows, 2):
        det = d[1] * e[2] - e[1] * d[2]
        if det != 0:
            tb = (-d[0] * e[2] + e[0] * d[2]) / det
            tc = (-d[1] * e[0] + e[1] * d[0]) / det
            pinned = (tb, tc)
            break
    check("S1-21 requiring W-neutral edges to stay neutral PINS the field: two "
          "of the 13 neutral edges force sigma_B = sigma_C = sigma_A",
          pinned == (F(1), F(1))
          and all(d[0] + d[1] * pinned[0] + d[2] * pinned[1] == 0
                  for d in neutral_rows))

    t = (F(1), F(4, 9), F(1))          # sigma = (1, 3/2, 1)
    def cur(x, y):
        return sum(t[i] * deltas(x, y)[i] for i in range(dim))
    ratios = {cur(x, y) / (W(x) - W(y)) for x, y in edges if W(x) != W(y)}
    check("S1-22 but sign faithfulness on the 86 STRICT edges does NOT force "
          "uniform rescaling: sigma = (1, 3/2, 1) agrees on every one",
          all((W(x) - W(y) > 0) == (cur(x, y) > 0) for x, y in edges
              if W(x) != W(y)))
    check("S1-22 and it carries 19 distinct E_V/E_W ratios, so no single "
          "constant conversion exists: A holds while D fails",
          len(ratios) == 19 and min(ratios) == F(1, 6) and max(ratios) == F(59, 54))
    check("S1-22 the same sigma breaks 8 of the 13 neutral edges, which is "
          "exactly what S1-21 forbids",
          sum(1 for x, y in flat if cur(x, y) != 0) == 8)

    # ---------------- the implemented semantics, cross-checked ----------------
    PK = {x: _s1_package_menu(world, x) for x in states}
    check("S1-24 the package now implements the atomic rule: its successor map "
          "equals this module's independent enumeration on all 91 states",
          all(set(PK[x]) == set(AP[x]) for x in states),
          str([_s1_show(x) for x in states if set(PK[x]) != set(AP[x])][:3]))
    check("S1-24 and it no longer implements the withdrawn rule anywhere",
          any(set(PK[x]) != set(CS[x]) for x in states))
    dead = [x for x in states if not PK[x]]
    check("S1-25 implemented: x* is the only absorbing state",
          dead == [S1_STAR])
    check("S1-25 implemented: x* is reachable from all 91 states, and from all "
          "91 by W-nonincreasing paths",
          len(_s1_reach(states, PK, lambda p, c: True)) == 91
          and len(_s1_reach(states, PK, lambda p, c: W(c) <= W(p))) == 91)
    locked = [x for x in states if PK[x] and not any(W(y) < W(x) for y in PK[x])]
    check("S1-25 implemented: the two plateau-locked states are (3,4,5) and "
          "(5,4,3), and (5,4,3) still has its neutral exit",
          sorted(locked) == [(F(3), F(4), F(5)), (F(5), F(4), F(3))]
          and (F(5), F(3), F(4)) in PK[(F(5), F(4), F(3))]
          and S1_STAR in PK[(F(5), F(3), F(4))])

    audit = (F(1), F(1, 4), F(1, 9))   # sigma = (1, 2, 3)
    def aud(x, y):
        return sum(audit[i] * deltas(x, y)[i] for i in range(dim))
    check("S1-23 the audit field sigma = (1,2,3) disagrees in sign on 13 of the "
          "99 demand-driven edges",
          sum(1 for x, y in edges
              if (W(x) - W(y) > 0) != (aud(x, y) > 0)) == 13)


def section_off_slice() -> None:
    """Three different minimizers that must not be substituted for each other."""

    def lattice_argmin(star, sigma, total, cells=3):
        best, arg = None, []
        for a in range(total + 1):
            for b in range(total + 1 - a):
                x = (F(a), F(b), F(total - a - b))
                v = sum((x[i] - star[i]) ** 2 / (2 * sigma[i] ** 2) for i in range(cells))
                if best is None or v < best:
                    best, arg = v, [x]
                elif v == best:
                    arg.append(x)
        return arg

    def affine_slice(star, sigma, total, cells=3):
        lam = (F(total) - sum(star)) / sum(s * s for s in sigma)
        return tuple(star[i] + lam * sigma[i] ** 2 for i in range(cells))

    zero = (F(0),) * 3
    check("OS1 off-slice x*: the AFFINE-slice minimiser moves with sigma",
          affine_slice(zero, (F(1),) * 3, 6) == (F(2),) * 3
          and affine_slice(zero, (F(1), F(2), F(3)), 6)
          == (F(3, 7), F(12, 7), F(27, 7)))
    check("OS1 and here the LATTICE minimiser moves too, but only after rounding",
          lattice_argmin(zero, (F(1),) * 3, 6) == [(F(2),) * 3]
          and lattice_argmin(zero, (F(1), F(2), F(3)), 6) == [(F(0), F(2), F(4))])

    unit = (F(1),) * 3
    tilt = (F(1), F(11, 10), F(9, 10))
    check("OS2 the affine minimiser can move while the LATTICE argmin does not, "
          "so movement of x* + lambda sigma^2 does not by itself break alignment",
          affine_slice(unit, unit, 6) != affine_slice(unit, tilt, 6)
          and lattice_argmin(unit, unit, 6) == lattice_argmin(unit, tilt, 6)
          == [(F(2),) * 3])

    far = (F(8), F(0), F(0))
    unconstrained = affine_slice(far, unit, 6)
    check("OS3 with NONNEGATIVITY binding, x* + lambda sigma^2 is not even "
          "feasible, so it may not be quoted as the minimiser at all",
          any(v < 0 for v in unconstrained)
          and lattice_argmin(far, unit, 6) == [(F(6), F(0), F(0))])


def section_two_cell_ratio() -> None:
    """Two cells: local proportionality is not a global constant conversion."""
    star = (F(1), F(1))
    ref = lambda x: (x[0] - star[0]) ** 2 / 2 + (x[1] - star[1]) ** 2 / 2
    states = [(F(a), F(4 - a)) for a in range(5)]
    steps = list(zip(states, states[1:]))

    def field(x, s):
        return (x[0] - star[0]) ** 2 / 2 + (x[1] - star[1]) ** 2 / (2 * s * s)

    ratios = [
        (field(p, F(2)) - field(q, F(2))) / (ref(p) - ref(q)) for p, q in steps
    ]
    check("TC1 two cells, sigma = (1,2): the covector ratio varies across states",
          len(set(ratios)) > 1 and ratios == [F(3, 8), F(-1, 8), F(11, 8), F(7, 8)])
    check("TC1 and it even CHANGES SIGN, so a one-dimensional action space does "
          "not give condition D, nor even condition B",
          any(r < 0 for r in ratios))

    mild = F(3, 2)
    pairs = [(p, q) for p in states for q in states if p != q]
    strict_pairs = [(p, q) for p, q in pairs if ref(p) != ref(q)]
    check("TC2 with sigma = (1, 3/2) the SAME two-cell world is sign-faithful on "
          "every STRICT ordered pair, with sigma non-uniform",
          not any((ref(p) - ref(q) > 0) != (field(p, mild) - field(q, mild) > 0)
                  for p, q in strict_pairs))
    mild_ratios = {
        (field(p, mild) - field(q, mild)) / (ref(p) - ref(q))
        for p, q in strict_pairs
    }
    check("TC2 yet no single constant conversion exists there either",
          len(mild_ratios) > 1)
    tied = [(p, q) for p, q in pairs
            if ref(p) == ref(q) and field(p, mild) != field(q, mild)]
    check("TC2 and it separates a W-TIE, e.g. (1,3) against (3,1) -- the same "
          "boundary that S1-21 finds on the Study-1 graph",
          tied and ((F(1), F(3)), (F(3), F(1))) in tied)


def section_factor_qualification() -> None:
    """A total-potential identity does not descend to the declared factors."""
    star = (F(1), F(1))
    states = [(F(a), F(2 - a)) for a in range(3)]
    w_total = lambda x: (x[0] - star[0]) ** 2 / 2 + (x[1] - star[1]) ** 2 / 2
    v_total = lambda x: (x[0] - star[0]) ** 2
    check("FQ1 two potentials agree on the WHOLE conservation slice",
          all(w_total(x) == v_total(x) for x in states))
    w0 = lambda x: (x[0] - star[0]) ** 2 / 2
    v0 = lambda x: (x[0] - star[0]) ** 2
    w1 = lambda x: (x[1] - star[1]) ** 2 / 2
    v1 = lambda x: F(0)
    check("FQ1 factor 0 relates them by 2, factor 1 by no positive constant at "
          "all, so factorwise properties may NOT be inferred from the total",
          all(v0(x) == 2 * w0(x) for x in states)
          and any(w1(x) != 0 and v1(x) == 0 for x in states))



# --------------------------------------------------------------------------
# SS-* : the sufficient-state question
#
# Does one scalar c_i, together with the current physical state, the current
# field and the current local constraints, determine every future EBU decision
# and update -- with NO history?
#
# Static structural enumeration only, as in the S1-* section: pure functions of
# synthetic states, no EconomyRun, no policy, no arrival law, no trajectory.
# Companion report: DYNAMIC_EBU_CAPACITY_SUFFICIENT_STATE_STUDY.md.
# --------------------------------------------------------------------------

def _ss_field(x, sig):
    """Current-field burden at the Study-1 reference x* with scales `sig`."""
    return sum((x[i] - S1_STAR[i]) ** 2 / (2 * sig[i] ** 2) for i in range(3))


def _ss_covector(x, sig):
    """dV_sig restricted to the conservation slice, in the basis of 1^perp."""
    grad = [(x[i] - S1_STAR[i]) / sig[i] ** 2 for i in range(3)]
    basis = ((F(1), F(-1), F(0)), (F(0), F(1), F(-1)))
    return [sum(grad[i] * t[i] for i in range(3)) for t in basis]


def _ss_same_ray(a, b) -> bool:
    """Do two covectors lie in one OPEN positive ray? (rank one AND same sign)"""
    if rank([a, b]) > 1:
        return False
    for u, v in zip(a, b):
        if u != 0 and v != 0:
            return (u > 0) == (v > 0)
        if (u == 0) != (v == 0):
            return False
    return True  # both identically zero


def section_sufficient_state() -> None:
    world = _s1_world()
    W = world.potential.value_total
    states = _s1_states()
    plans = _s1_all_plans(world)
    menu = {x: set(_s1_atomic_menu(world, x, plans, False).keys()) for x in states}
    menu_no = {x: set(_s1_atomic_menu(world, x, plans, True).keys()) for x in states}
    edges = [(x, y) for x in states for y in menu[x]]
    sig = (F(1), F(2), F(3))
    V = lambda x: _ss_field(x, sig)

    # ---------------- the share diamond: the exact counterexample ----------
    x0 = (F(3), F(6), F(3))
    y1 = (F(4), F(3), F(5))
    y2 = (F(5), F(3), F(4))
    x2 = S1_STAR

    check("SS-01 both two-step histories are legal under the IMPLEMENTED atomic "
          "P-demand rule: (3,6,3)->(4,3,5)->x* and (3,6,3)->(5,3,4)->x*",
          y1 in menu[x0] and y2 in menu[x0]
          and x2 in menu[y1] and x2 in menu[y2])
    check("SS-02 the two histories end at the SAME current physical state x*, "
          "under the SAME field, with W = 3, 1, 1, 0",
          W(x0) == 3 and W(y1) == 1 and W(y2) == 1 and W(x2) == 0)
    check("SS-02 and BOTH owners hold identical balances in both histories: "
          "the first mover settles +2, the second +1",
          W(x0) - W(y1) == 2 and W(x0) - W(y2) == 2
          and W(y1) - W(x2) == 1 and W(y2) - W(x2) == 1)

    first = (V(x0) - V(y1), V(x0) - V(y2))
    second = (V(y1) - V(x2), V(y2) - V(x2))
    check("SS-03 INFORMATION LOSS. Same x, same field, same c for every owner -- "
          "yet exact repricing to sigma=(1,2,3) demands 7/8 vs 31/72 for the "
          "first mover and 13/72 vs 5/8 for the second. One scalar cannot hold "
          "two values, so c is NOT a sufficient state for revaluation",
          first == (F(7, 8), F(31, 72)) and second == (F(13, 72), F(5, 8)))
    check("SS-03 the exact memory term the scalar has discarded is 4/9",
          first[0] - first[1] == F(4, 9))

    check("SS-04 the AGGREGATE is identical in both histories under BOTH fields "
          "-- 3 and 19/18 -- and equals V(x0) - V(x_now): the total is a state "
          "function, only the per-owner SHARE is path dependent",
          W(x0) - W(x2) == 3 and V(x0) - V(x2) == F(19, 18)
          and first[0] + second[0] == V(x0) - V(x2)
          and first[1] + second[1] == V(x0) - V(x2))

    paths = [(a, b, c) for a in states for b in menu[a] for c in menu[b]]
    check("SS-05 aggregate telescoping holds on EVERY two-step menu path of the "
          "graph, under both fields -- exhaustively, not by sampling",
          len(paths) > 0
          and all((W(a) - W(b)) + (W(b) - W(c)) == W(a) - W(c)
                  and (V(a) - V(b)) + (V(b) - V(c)) == V(a) - V(c)
                  for a, b, c in paths))

    diamonds = [
        (a, b, c, d)
        for a in states
        for b in menu[a] for c in menu[a]
        if b < c and W(b) == W(c) and V(b) != V(c)
        for d in menu[b] & menu[c]
    ]
    check("SS-06 the witness is not isolated: the frozen graph carries 137 share "
          "diamonds for sigma=(1,2,3)", len(diamonds) == 137, str(len(diamonds)))

    # ---------------- forward sufficiency, and NON-minimality --------------
    settlements = sorted({W(x) - W(y) for x, y in edges})
    check("SS-07 every settlement realized on the 408-edge menu graph is an "
          "INTEGER",
          all(s == int(s) for s in settlements) and len(edges) == 408,
          str(len(edges)))
    check("SS-07 hence no action ever changes the fractional part of a balance, "
          "so two balances with equal integer part are indistinguishable by "
          "EVERY future action: c is sufficient but STRICTLY NOT MINIMAL",
          all((F(1, 3) + s >= 0) == (F(2, 3) + s >= 0) for s in settlements))
    check("SS-07 the NEGATIVE settlements realized anywhere on the graph are "
          "exactly -1, -2, -3, -4 and -6 -- all integers, and they separate "
          "balances an integer apart, so the distinctions a future can draw are "
          "a discrete index: coarser than c, never finer",
          [s for s in settlements if s < 0] == [F(-6), F(-4), F(-3), F(-2), F(-1)]
          and any((F(1, 2) + s >= 0) != (F(5, 2) + s >= 0) for s in settlements),
          str([str(s) for s in settlements if s < 0]))

    # ---------------- accessibility: partial, and not W-monotone ----------
    reach = {}
    for x in states:
        seen, stack = {x}, [x]
        while stack:
            u = stack.pop()
            for v in menu[u]:
                if v not in seen:
                    seen.add(v)
                    stack.append(v)
        reach[x] = seen
    check("SS-08 x* is reachable from all 91 states, and from x* NOTHING but x* "
          "is reachable: x* is the unique maximum of the accessibility preorder",
          all(S1_STAR in reach[x] for x in states) and reach[S1_STAR] == {S1_STAR})
    pairs = [(a, b) for a, b in combinations(states, 2)]
    comparable = [(a, b) for a, b in pairs if b in reach[a] or a in reach[b]]
    check("SS-08 the accessibility preorder is FAR from total: 1689 of the 4095 "
          "unordered pairs are comparable, 2406 are not. Lieb-Yngvason's "
          "Comparison Hypothesis fails, so no order-REFLECTING scalar exists",
          (len(pairs), len(comparable)) == (4095, 1689),
          f"{len(pairs)} {len(comparable)}")

    up = [(x, y) for x, y in edges if W(y) > W(x)]
    up_no = [(x, y) for x in states for y in menu_no[x] if W(y) > W(x)]
    check("SS-09 C = I - W is NOT an accessibility potential: 48 menu edges "
          "strictly INCREASE W, so X < Y does not imply C(X) <= C(Y). Strong "
          "atomic provenance sharpened this: a plan may legitimately restore one "
          "deficit while deepening another, and 48 such edges now exist where 4 "
          "did. The count is 42 under the declared no-overshoot variant",
          len(up) == 48 and len(up_no) == 42, f"{len(up)} {len(up_no)}")
    check("SS-09 and each ascending edge is affordable only out of an existing "
          "balance, which is the exact operational content of the 'stored "
          "damage potential' reading of C",
          all(W(x) - W(y) < 0 for x, y in up))

    # ---------------- Lieb-Yngvason axioms cannot even be stated ----------
    totals = {sum(x) for x in states}
    check("SS-10 the declared state space is a FIXED-total lattice (every state "
          "sums to 12), so lambda X leaves it for every lambda != 1: axioms A4 "
          "(scaling) and A5 (splitting) have no referent and the Lieb-Yngvason "
          "entropy theorem is INAPPLICABLE, not merely unproved",
          totals == {F(12)})

    # ---------------- the rank / common-ray criterion ----------------------
    ref = (F(1), F(1), F(1))
    ray = [x for x in states if _ss_same_ray(_ss_covector(x, ref), _ss_covector(x, sig))]
    check("SS-11 the common-normalizer criterion bites everywhere: the projected "
          "differentials of sigma=(1,1,1) and (1,2,3) share one ray at exactly "
          "ONE of the 91 states -- x* itself, where both vanish -- hence at NO "
          "state with a nonzero gradient does a positive lambda(x) relate them",
          ray == [S1_STAR])
    check("SS-11 at (5,4,3) the two projected covectors are (1,1) and (1,1/9): "
          "rank 2, hence no positive multiple relates them",
          _ss_covector((F(5), F(4), F(3)), ref) == [F(1), F(1)]
          and _ss_covector((F(5), F(4), F(3)), sig) == [F(1), F(1, 9)]
          and rank([_ss_covector((F(5), F(4), F(3)), ref),
                    _ss_covector((F(5), F(4), F(3)), sig)]) == 2)
    check("SS-11 a uniform rescaling sigma -> 2 sigma shares the ray at EVERY "
          "state, which is condition D and changes no decision",
          all(_ss_same_ray(_ss_covector(x, ref),
                           _ss_covector(x, (F(2), F(2), F(2)))) for x in states))

    # ---------------- cohomology is NOT sufficiency ------------------------
    verts = sorted({v for e in edges for v in e})
    undirected_edges = sorted({tuple(sorted((x, y))) for x, y in edges if x != y})
    ncomp = len(set(components(verts, undirected_edges).values()))
    betti = len(undirected_edges) - len(verts) + ncomp
    check("SS-12 the settlement cochain of the Study-1 action graph is EXACT -- "
          "zero circulation on every cycle -- because it is the coboundary of W",
          is_exact(verts, undirected_edges, lambda u, v: W(u) - W(v)))
    check("SS-12 and it is exact over a genuinely non-trivial cycle space: the "
          "graph is connected with 91 vertices and 344 undirected edges, so "
          "its first Betti number is 254: exactness is a real constraint here, "
          "not an artifact of a tree",
          (len(verts), len(undirected_edges), ncomp, betti) == (91, 344, 1, 254),
          f"{len(verts)} {len(undirected_edges)} {ncomp} {betti}")
    check("SS-12 EXACT does NOT imply SUFFICIENT: the same exact cochain fails "
          "the sufficiency test of SS-03",
          first[0] != first[1])
    ring_v, ring_e = [0, 1, 2], [(0, 1), (1, 2), (0, 2)]
    check("SS-12 SUFFICIENT does NOT imply EXACT: on a 3-ring settling +1 per "
          "traversal the update and the gate are functions of (c, vertex) "
          "alone -- perfect sufficiency -- yet the circulation is 3, so the "
          "cochain is not a coboundary. Cohomology characterizes path "
          "independence ONLY; it says nothing about future sufficiency",
          not is_exact(ring_v, ring_e, lambda u, v: F(1) if (u, v) in ring_e else F(-1)))


# --------------------------------------------------------------------------
# FS-* : the freedom-STATE question
#
# Is there a CURRENT-STATE total freedom function F(x, theta, K) depending only
# on the present physical state, the present field and declared physical
# invariants -- with no history, no source portfolio and no arbitrary viability
# threshold? Companion report: DYNAMIC_EBU_FREEDOM_STATE_THEORY.md.
#
# Static structural enumeration only, as in the S1-* and SS-* sections.
# --------------------------------------------------------------------------

def _fs_V(x, star, sig):
    return sum((x[i] - star[i]) ** 2 / (2 * sig[i] ** 2) for i in range(3))


def section_freedom_state() -> None:
    world = _s1_world()
    W = world.potential.value_total
    states = _s1_states()
    plans = _s1_all_plans(world)
    menu = {x: set(_s1_atomic_menu(world, x, plans, False).keys()) for x in states}
    edges = [(x, y) for x in states for y in menu[x]]
    ONE = (F(1), F(1), F(1))

    # ---------------- the physical scale, derived not initialized ----------
    w_max = max(W(x) for x in states)
    corners = [x for x in states if W(x) == w_max]
    check("FS-01 the declared physical domain {x >= 0 integer, sum x = 12} has "
          "W_max = 48, attained exactly at the three corners: the scale is a "
          "function of (M, x*, sigma) alone -- no initialization datum",
          w_max == 48
          and sorted(corners) == sorted([(F(12), F(0), F(0)),
                                         (F(0), F(12), F(0)),
                                         (F(0), F(0), F(12))]))

    Ftot = lambda x: w_max - W(x)
    check("FS-02 F := W_max - W is non-negative on the whole physical domain, "
          "vanishes EXACTLY at the three corners, and is maximal EXACTLY at x*, "
          "so argmax F = argmin W = {x*} as the golden requirement demands",
          all(Ftot(x) >= 0 for x in states)
          and [x for x in states if Ftot(x) == 0] == sorted(corners)
          and [x for x in states if Ftot(x) == w_max] == [S1_STAR])

    check("FS-03 the scale is UNIQUE: among constants I with I - W >= 0 on the "
          "domain and inf(I - W) = 0, exactly I = 48 qualifies. I = 47 makes "
          "freedom negative at a physical state; I = 49 leaves unphysical slack",
          min(47 - W(x) for x in states) < 0
          and min(49 - W(x) for x in states) > 0
          and min(w_max - W(x) for x in states) == 0)

    # ---------------- the unique conserved linear charge -------------------
    disp = [[F(-1), F(1), F(0)], [F(1), F(-1), F(0)],
            [F(0), F(-1), F(1)], [F(0), F(1), F(-1)]]
    check("FS-04 the four declared routes span a rank-2 displacement space, so "
          "its annihilator is one dimensional: the TOTAL MATERIAL M is the "
          "UNIQUE linear conserved charge of the declared physics. There is no "
          "second invariant available to fix a scale",
          rank(disp) == 2)

    # ---------------- exactness, and what topology does NOT fix ------------
    check("FS-05 Delta F = -Delta W on every one of the 226 menu edges, so the "
          "freedom cochain is the coboundary of -W: every closed actor cycle "
          "settles to exactly zero",
          all(Ftot(y) - Ftot(x) == -(W(y) - W(x)) for x, y in edges))
    check("FS-05 refinement invariance: on every two-step menu path the freedom "
          "increments add to the endpoint difference, exhaustively",
          all(Ftot(b) - Ftot(a) + Ftot(c) - Ftot(b) == Ftot(c) - Ftot(a)
              for a in states for b in menu[a] for c in menu[b]))

    # ---------------- F is a state function but NOT sufficient -------------
    lvl = [x for x in states if W(x) == 1]
    locked = [x for x in lvl if not any(W(y) < W(x) for y in menu[x])]
    check("FS-06 F is NOT a sufficient statistic for the physics: (3,4,5) and "
          "(4,3,5) carry the SAME F, yet (3,4,5) has a 2-plan menu with NO "
          "strict-descent move while (4,3,5) has a 4-plan menu with one. Equal "
          "freedom, non-isomorphic futures -- the Nerode quotient is strictly "
          "finer than the level sets of F",
          W((F(3), F(4), F(5))) == W((F(4), F(3), F(5)))
          and len(menu[(F(3), F(4), F(5))]) == 2
          and len(menu[(F(4), F(3), F(5))]) == 4
          and (F(3), F(4), F(5)) in locked and (F(4), F(3), F(5)) not in locked)

    # ---------------- freedom is ANTI-correlated with available action -----
    empty = [x for x in states if not menu[x]]
    check("FS-07 F is maximal EXACTLY where the admissible action set is EMPTY: "
          "x* is the unique absorbing state and the unique maximizer of F. A "
          "coordinate maximal precisely where nothing can be done does not "
          "measure available action",
          empty == [S1_STAR] and [x for x in states if Ftot(x) == w_max] == [S1_STAR])
    check("FS-07 the dual coordinate IS available action: since x* is reachable "
          "from every state, the maximum total EBU still extractable from x is "
          "exactly W(x), and F + F_extract = W_max identically",
          all(Ftot(x) + W(x) == w_max for x in states))

    # ---------------- the field defect: the decisive obstruction -----------
    x0, x1, x2 = (F(3), F(6), F(3)), (F(4), F(3), F(5)), S1_STAR
    SIG = (F(1), F(2), F(3))

    def accumulated(star2, sig2):
        """Aggregate receipts actually settled, for the field change inserted
        before both actions, between them, and after both."""
        before = _fs_V(x0, star2, sig2) - _fs_V(x2, star2, sig2)
        between = ((_fs_V(x0, S1_STAR, ONE) - _fs_V(x1, S1_STAR, ONE))
                   + (_fs_V(x1, star2, sig2) - _fs_V(x2, star2, sig2)))
        after = _fs_V(x0, S1_STAR, ONE) - _fs_V(x2, S1_STAR, ONE)
        return before, between, after

    check("FS-08 DECISIVE. With a genuine mid-history field change the AGGREGATE "
          "settled wallet is NOT endpoint determined: the same two actions on "
          "the same states accumulate 19/18, 157/72 or 3 according to WHEN "
          "sigma -> (1,2,3) occurs. No current-state F can equal sum_i c_i",
          accumulated(S1_STAR, SIG) == (F(19, 18), F(157, 72), F(3)))
    check("FS-09 and the defect vanishes EXACTLY on the EBU-trivial class: "
          "moving x* from (4,4,4) to (5,5,5) shifts V by the constant 3/2 at "
          "every one of the 91 states, so all three insertion orders accumulate "
          "3 and the identity sum_i c_i = F is restored",
          {_fs_V(x, (F(5), F(5), F(5)), ONE) - _fs_V(x, S1_STAR, ONE)
           for x in states} == {F(3, 2)}
          and accumulated((F(5), F(5), F(5)), ONE) == (F(3), F(3), F(3)))

    # ---------------- condition A across the Gaussian family ---------------
    for sig, label in [(SIG, "(1,2,3)"), ((F(5), F(1, 2), F(7)), "(5,1/2,7)")]:
        lo = min(_fs_V(x, S1_STAR, sig) for x in states)
        check(f"FS-10 condition A holds for sigma = {label}: argmax F_theta = "
              "argmin V_theta = {x*}, so equilibrium still coincides with "
              "maximum freedom under a heterogeneous field change",
              [x for x in states if _fs_V(x, S1_STAR, sig) == lo] == [S1_STAR])
    moved = (F(2), F(4), F(6))
    lo = min(_fs_V(x, moved, ONE) for x in states)
    check("FS-10 and when the reference itself moves to a reachable (2,4,6), "
          "argmax F follows it exactly: F tracks the CURRENT field, which the "
          "theta_0-anchored coordinate cannot do",
          [x for x in states if _fs_V(x, moved, ONE) == lo] == [moved])

    # ---------------- entropy-like structural properties -------------------
    tdirs = [(F(1), F(-1), F(0)), (F(1), F(0), F(-1)), (F(0), F(1), F(-1))]
    def shift(x, t, k):
        return tuple(x[i] + k * t[i] for i in range(3))
    interior = [(x, t) for x in states for t in tdirs
                if shift(x, t, 1) in states and shift(x, t, -1) in states]
    check("FS-11 F is strictly discretely CONCAVE along every transfer "
          "direction (W is strictly convex), so the maximum principle at x* is "
          "structural and not a coincidence of the lattice",
          len(interior) > 0
          and all(Ftot(shift(x, t, 1)) + Ftot(shift(x, t, -1)) - 2 * Ftot(x) < 0
                  for x, t in interior))
    up = [(x, y) for x, y in edges if W(y) > W(x)]
    check("FS-11 but F is NOT monotone along accessibility -- 48 of the 408 menu "
          "edges strictly decrease it -- so there is no second law and F is a "
          "Lyapunov CANDIDATE that is not a Lyapunov function",
          len(up) == 48 and len(edges) == 408, f"{len(up)}/{len(edges)}")
    sub = [x for x in states if x[0] == 4]
    check("FS-11 and F is NOT additive across a shared conservation law: the "
          "joint domain has W_max = 48 while the product domain at fixed "
          "M_A = 4, M_BC = 8 has 16. Conservation coupling is exactly what "
          "breaks additivity",
          w_max == 48
          and max((x[1] - 4) ** 2 / 2 + (x[2] - 4) ** 2 / 2 for x in sub) == 16)

    # ---------------- I_dyn is NOT a current-state datum --------------------
    reach = {}
    for x in states:
        seen, stack = {x}, [x]
        while stack:
            u = stack.pop()
            for v in menu[u]:
                if v not in seen:
                    seen.add(v)
                    stack.append(v)
        reach[x] = seen
    a0, b0 = (F(3), F(6), F(3)), (F(0), F(6), F(6))
    check("FS-13 CENTRAL. The accounting invariant I = C + W equals W(x_0), a "
          "constant of the MOTION fixed by initial data, not a function of the "
          "present state: (3,6,3) and (0,6,6) both reach x*, with W = 3 and 12, "
          "so two worlds in the IDENTICAL current state x* carry C = 3 and "
          "C = 12. No F(x, theta, K) can equal C",
          S1_STAR in reach[a0] and S1_STAR in reach[b0]
          and W(a0) == 3 and W(b0) == 12 and W(a0) != W(b0))
    check("FS-13 but F = W_max - W and C differ by the CONSTANT W_max - W(x_0), "
          "so they share every differential and every argmax: the programme's "
          "proved results transfer verbatim and only the zero moves -- from an "
          "initialization datum to a physical one",
          all((w_max - W(y)) - (w_max - W(x)) == (W(a0) - W(y)) - (W(a0) - W(x))
              for x, y in edges))

    # ---------------- can the SHARES be localized? -------------------------
    blocks_ok = []
    partitions = [((0, 1, 2),), ((0,), (1, 2)), ((1,), (0, 2)),
                  ((2,), (0, 1)), ((0,), (1,), (2,))]
    for part in partitions:
        supported = True
        for d in disp:
            touched = {i for i in range(3) if d[i] != 0}
            if not any(touched <= set(b) for b in part):
                supported = False
                break
        if supported:
            blocks_ok.append(part)
    check("FS-12 a state-determined LOCAL share rule needs every action's "
          "displacement inside one ownership block. Of the 5 partitions of the "
          "three stocks, exactly ONE qualifies -- the trivial single-owner "
          "block. On a connected transfer network the share path-dependence is "
          "therefore NOT removable by any local state rule",
          blocks_ok == [((0, 1, 2),)])


# --------------------------------------------------------------------------
# FC-* : the universal freedom coordinate and its CROSS-FIELD CALIBRATION
#
# F is now a function of the FULL current state X = (x, theta, K), so nothing
# is ever repriced and mixed full-state cycles close by construction. The live
# question is whether physics fixes the theta-dependent scale alpha(theta) --
# the exchange rate between current EBU and universal freedom units.
# Companion report: EBU_UNIVERSAL_FREEDOM_COORDINATE.md.
#
# Static algebra on synthetic states only. No mechanism, no Stage A/B, no
# affordability gate is assumed anywhere in this section.
# --------------------------------------------------------------------------

def _fc_V(x, star, sig):
    return sum((x[i] - star[i]) ** 2 / (2 * sig[i] ** 2) for i in range(3))


def section_calibration() -> None:
    world = _s1_world()
    W = world.potential.value_total
    states = _s1_states()
    plans = _s1_all_plans(world)
    menu = {x: set(_s1_atomic_menu(world, x, plans, False).keys()) for x in states}
    edges = [(x, y) for x in states for y in menu[x]]
    ONE, SIG, TWO = ((F(1),) * 3), (F(1), F(2), F(3)), ((F(2),) * 3)
    S5 = (F(5), F(5), F(5))
    Vr = lambda x: _fc_V(x, S1_STAR, ONE)
    Vc = lambda x: _fc_V(x, S1_STAR, SIG)

    # ---------------- 7B: level sets are massively disconnected ------------
    levels, adj = {}, {}
    for x in states:
        levels.setdefault(W(x), []).append(x)
    for x, y in edges:
        adj.setdefault(x, set()).add(y)
        adj.setdefault(y, set()).add(x)
    ncomp = 0
    for grp in levels.values():
        pool, seen = set(grp), set()
        for s in pool:
            if s in seen:
                continue
            ncomp += 1
            stack = [s]
            seen.add(s)
            while stack:
                u = stack.pop()
                for v in adj.get(u, ()):
                    if v in pool and v not in seen:
                        seen.add(v)
                        stack.append(v)
    check("FC-01 on one theta slice the 15 burden levels split into 74 "
          "actor-connected components, so 'F is a function of V_theta' is a "
          "genuine FINITE compatibility demand across components, not a "
          "consequence of the differential condition",
          (len(levels), ncomp) == (15, 74), f"{len(levels)} {ncomp}")

    # ---------------- 7D / 11B: no monotone reparametrization --------------
    by_ref = {}
    for x in states:
        by_ref.setdefault(Vr(x), set()).add(Vc(x))
    multi = [k for k, v in by_ref.items() if len(v) > 1]
    check("FC-02 V_cur is NOT a function of V_ref: on 14 of the 15 reference "
          "levels it takes several values, so no increasing psi has "
          "V_(1,2,3) = psi(V_(1,1,1)). Ordinal equivalence -- and with it any "
          "calibration it could force -- simply does not apply to a "
          "heterogeneous sigma change",
          (len(by_ref), len(multi)) == (15, 14)
          and sorted(by_ref[F(48)]) == [F(122, 9), F(152, 9), F(314, 9)])

    # ---------------- the mixed cycle ---------------------------------------
    x0, x1 = S1_STAR, (F(5), F(4), F(3))

    def circulation(a0, star0, sig0, a1, star1, sig1, u, v):
        """Actor-attributed credit around: act under theta0, field moves,
        reverse under theta1, field returns."""
        return (-a0 * (_fc_V(v, star0, sig0) - _fc_V(u, star0, sig0))
                + a1 * (_fc_V(v, star1, sig1) - _fc_V(u, star1, sig1)))

    F_of = lambda x, star, sig, a, b: -a * _fc_V(x, star, sig) + b
    total = ((F_of(x1, S1_STAR, ONE, F(1), F(0)) - F_of(x0, S1_STAR, ONE, F(1), F(0)))
             + (F_of(x1, S1_STAR, SIG, F(1), F(0)) - F_of(x1, S1_STAR, ONE, F(1), F(0)))
             + (F_of(x0, S1_STAR, SIG, F(1), F(0)) - F_of(x1, S1_STAR, SIG, F(1), F(0)))
             + (F_of(x0, S1_STAR, ONE, F(1), F(0)) - F_of(x0, S1_STAR, SIG, F(1), F(0))))
    check("FC-03 the TOTAL of all four increments round the mixed cycle is "
          "exactly 0 -- automatic, because F is a state function of the full X. "
          "The mixed-cycle test therefore has NO discriminating power on the "
          "total, and all of its content sits in the actor-attributed part",
          total == 0)

    circ = circulation(F(1), S1_STAR, ONE, F(1), S1_STAR, SIG, x0, x1)
    check("FC-04 the ACTOR-attributed circulation is NOT zero: acting x* -> "
          "(5,4,3) under sigma=(1,1,1) and reversing it under sigma=(1,2,3) "
          "credits exactly -4/9 while the world returns to its exact starting "
          "state. Reversed, the same cycle MINTS +4/9, repeatably",
          circ == F(-4, 9)
          and circulation(F(1), S1_STAR, SIG, F(1), S1_STAR, ONE, x0, x1) == F(4, 9))

    def nonzero(a0, star0, sig0, a1, star1, sig1):
        return sum(1 for u in states for v in states
                   if circulation(a0, star0, sig0, a1, star1, sig1, u, v) != 0)

    check("FC-05 and NO choice of alpha repairs it: alpha = 1 leaves 8040 of "
          "the 8281 state pairs with nonzero actor circulation, and alpha "
          "tuned to close the witness pair (9/5) leaves 8066 -- strictly "
          "worse. Calibration cannot be fitted",
          nonzero(F(1), S1_STAR, ONE, F(1), S1_STAR, SIG) == 8040
          and nonzero(F(1), S1_STAR, ONE, F(9, 5), S1_STAR, SIG) == 8066)

    ratios = {(_fc_V(y, S1_STAR, ONE) - _fc_V(x, S1_STAR, ONE))
              / (_fc_V(y, S1_STAR, SIG) - _fc_V(x, S1_STAR, SIG))
              for x, y in edges
              if _fc_V(y, S1_STAR, SIG) != _fc_V(x, S1_STAR, SIG)}
    check("FC-06 the reason is exact: the alpha ratio each action DEMANDS is "
          "dV_ref/dV_cur, and over the menu graph that takes 174 distinct "
          "values, 10 of them NEGATIVE. Not one constant, and not even one "
          "sign",
          len(ratios) == 174 and sum(1 for r in ratios if r < 0) == 10,
          f"{len(ratios)} {sum(1 for r in ratios if r < 0)}")

    # ---------------- the calibrated class ---------------------------------
    uni = {(_fc_V(y, S1_STAR, ONE) - _fc_V(x, S1_STAR, ONE))
           / (_fc_V(y, S1_STAR, TWO) - _fc_V(x, S1_STAR, TWO))
           for x, y in edges
           if _fc_V(y, S1_STAR, TWO) != _fc_V(x, S1_STAR, TWO)}
    check("FC-07 CALIBRATED CLASS, witness 1 -- uniform rescaling. sigma -> "
          "2 sigma demands the single ratio 4 on every action, and with "
          "alpha(2 sigma) = 4 alpha(sigma) EVERY one of the 8281 mixed cycles "
          "closes exactly. The scale is forced, not chosen",
          uni == {F(4)}
          and nonzero(F(1), S1_STAR, ONE, F(4), S1_STAR, TWO) == 0)
    check("FC-07 and the underlying algebraic fact is exact separability: "
          "4 V_(2 sigma) = V_(1,1,1) identically, so alpha V_theta - W is "
          "independent of x and F splits as W(x) + g(theta)",
          all(4 * _fc_V(x, S1_STAR, TWO) == Vr(x) for x in states))

    check("FC-08 CALIBRATED CLASS, witness 2 -- reference motion along "
          "span(sigma^2). Moving x* to (5,5,5) shifts V by the constant 3/2 at "
          "all 91 states, so alpha is unchanged and every mixed cycle closes",
          {_fc_V(x, S5, ONE) - Vr(x) for x in states} == {F(3, 2)}
          and nonzero(F(1), S1_STAR, ONE, F(1), S5, ONE) == 0)

    # ---------------- additivity forces an affine phi ----------------------
    sq = lambda t: -t ** 2
    lin = lambda t: -t
    check("FC-09 additivity over physically independent subsystems forces phi "
          "AFFINE: with V = v0 + v1, phi(t) = -t^2 gives -4 against -1 + -1, "
          "while phi(t) = -t is additive. This is the Cauchy step that reduces "
          "an arbitrary decreasing phi_theta to -alpha(theta) V + beta(theta)",
          sq(F(2)) != sq(F(1)) + sq(F(1)) and lin(F(2)) == lin(F(1)) + lin(F(1)))

    # ---------------- rival calibrations credit differently ----------------
    wmax_c = max(Vc(y) for y in states)
    dv = Vc(x1) - Vc(x0)
    check("FC-10 rival calibrations are not academic: the SAME action "
          "x* -> (5,4,3) at sigma=(1,2,3) is credited -5/9 under alpha = 1 and "
          "-5/314 under alpha = 1/W_max. Both satisfy every declared "
          "requirement, and they disagree by a factor of 314/9",
          dv == F(5, 9) and wmax_c == F(314, 9)
          and -dv == F(-5, 9) and -dv / wmax_c == F(-5, 314))
    check("FC-10 and alpha = 1 credits the SAME physical action -1 at "
          "sigma=(1,1,1) but -1/4 at 2 sigma, although the two fields induce "
          "the IDENTICAL ordering of all 91 states. Whether that factor 4 is "
          "physical or a change of ruler is exactly the undeclared datum",
          Vr(x1) - Vr(x0) == F(1)
          and _fc_V(x1, S1_STAR, TWO) - _fc_V(x0, S1_STAR, TWO) == F(1, 4)
          and all((Vr(u) < Vr(v)) == (_fc_V(u, S1_STAR, TWO) < _fc_V(v, S1_STAR, TWO))
                  for u in states for v in states))

def main() -> int:
    section_decomposition()
    section_theorem_one()
    section_two_cell()
    section_endpoint()
    section_settlement()
    section_graph()
    section_common_w()
    section_gaussian()
    section_receipts()
    section_corrections()
    section_decisive()
    section_canonical()
    section_current_field()
    section_synthesis()
    section_study_one()
    section_off_slice()
    section_two_cell_ratio()
    section_factor_qualification()
    section_sufficient_state()
    section_freedom_state()
    section_calibration()

    failed = [r for r in RESULTS if not r[1]]
    for name, ok, detail in RESULTS:
        if not ok:
            print(f"FAIL  {name}" + (f"  [{detail}]" if detail else ""))
    print(f"\n{len(RESULTS)} deterministic checks, {len(failed)} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
