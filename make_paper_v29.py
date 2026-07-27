"""
Generate the V2.9 local-preservation foundation PDF:
  Energy_Balance_Project_Foundation_v2.9.pdf

Content mirrors Foundation_v2.9_local_preservation.md (the authoritative
source). Every numerical table and figure is built AT COMPILE TIME directly
from the committed machine-readable result artifacts:

  results/v2.9/d9_d10/v29_d9_d10_summary.json        (144 runs, plan-hash checked)
  results/v2.9/d9_d10/v29_d9_d10_trace.jsonl.gz      (D9 trajectory figure)
  results/v2.9/deterministic/v29_deterministic_summary.json (24 runs)

Nothing is hand-transcribed; the build ABORTS if a plan hash or headline count
does not match the committed values. Equations are typeset with the matplotlib
mathtext engine (no external LaTeX toolchain).

Run with the project venv:  venv/bin/python make_paper_v29.py

This is a documentation build only. It does NOT touch the physics, P1C, or any
result artifact, and it upgrades no claim: numerical validation is never proof,
and the note awaits independent expert review.
"""
from __future__ import annotations
import gzip
import hashlib
import json
import os
import tempfile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Image, Table,
                                TableStyle, PageBreak, HRFlowable, KeepTogether)

OUT = "Energy_Balance_Project_Foundation_v2.9.pdf"
EQ_DPI = 220
EQ_DIR = tempfile.mkdtemp(prefix="v29eq_")
_eqn = [0]
_fig = [0]
_tab = [0]

# ---------------------------------------------------------------------------
# committed artifacts (loaded once; the whole document derives from these)
# ---------------------------------------------------------------------------
D9D10_PLAN_HASH = "87ad0ae2eb3cca6d86a56378c4a76508b29d7a63cb39ac74f5a362be1004c34a"
DET_PLAN_HASH = "af8f119b4af433290e6fc2546913868421e2f4adcaa467eb6d4d31e5e4856aa2"

_strict = lambda cst: (_ for _ in ()).throw(ValueError(f"non-strict JSON constant {cst}"))

with open("results/v2.9/d9_d10/v29_d9_d10_summary.json", encoding="utf-8") as fh:
    SUM = json.load(fh, parse_constant=_strict)
with open("results/v2.9/deterministic/v29_deterministic_summary.json", encoding="utf-8") as fh:
    DET = json.load(fh, parse_constant=_strict)
with open("v29_d9_d10_plan.json", encoding="utf-8") as fh:
    _plan = json.load(fh)
_h = hashlib.sha256(json.dumps(_plan, sort_keys=True,
                               separators=(",", ":")).encode()).hexdigest()
if not (SUM["plan_hash"] == _h == D9D10_PLAN_HASH):
    raise SystemExit("FATAL: D9/D10 plan hash mismatch; refusing to typeset")
if DET["plan_hash"] != DET_PLAN_HASH:
    raise SystemExit("FATAL: deterministic plan hash mismatch; refusing to typeset")

RUNS = {r["run_id"]: r for r in SUM["runs"]}
if len(SUM["runs"]) != 144 or len(RUNS) != 144:
    raise SystemExit("FATAL: expected 144 unique committed runs")
D10 = [r for r in SUM["runs"] if r["experiment"] == "D10"]
D10_CORE = [r for r in D10 if r["run_id"].startswith("D10-core/")]
POLICIES = ("P0", "P1", "soft", "P1C")


def _counts(pol):
    sub = [r for r in D10 if r["policy"] == pol]
    from collections import Counter
    c = Counter(r["primary_classification"] for r in sub)
    over = sum(1 for r in sub if r["O_physical"] > 1e-9)
    return len(sub), c, over


# hard build-time consistency checks against the headline numbers cited in prose
_n, _c, _o = _counts("P1C")
assert (_n, _c.get("collapse", 0), _c["safe_service"], _c["safe_rationing"], _o) \
    == (35, 0, 25, 10, 0), "P1C headline mismatch"
for _pol in ("P1", "soft"):
    _n, _c, _o = _counts(_pol)
    assert (_n, _c["collapse"], _c["safe_service"], _o) == (35, 25, 10, 25), \
        f"{_pol} headline mismatch"
assert _counts("P0")[1]["safe_rationing"] == 35, "P0 headline mismatch"
assert sum(1 for r in SUM["runs"] if r["terminal_status"] != "completed") == 18


# ---------------------------------------------------------------------------
# styles / flowable helpers (same family as make_paper_v28_discrete.py)
# ---------------------------------------------------------------------------
sty = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=sty["Heading1"], fontSize=14, spaceBefore=14,
                    spaceAfter=6, textColor=colors.HexColor("#1F3A5F"))
H2 = ParagraphStyle("H2", parent=sty["Heading2"], fontSize=11.5, spaceBefore=10,
                    spaceAfter=4, textColor=colors.HexColor("#2C5580"))
BODY = ParagraphStyle("BODY", parent=sty["BodyText"], fontSize=9.7, leading=13.6,
                      alignment=TA_JUSTIFY, spaceAfter=6)
TITLE = ParagraphStyle("TITLE", parent=sty["Title"], fontSize=21,
                       textColor=colors.HexColor("#1F3A5F"))
SUB = ParagraphStyle("SUB", parent=sty["Italic"], fontSize=11, alignment=TA_CENTER,
                     textColor=colors.HexColor("#2C5580"))
THM = ParagraphStyle("THM", parent=BODY, leftIndent=10, rightIndent=8, spaceBefore=4,
                     spaceAfter=6, borderColor=colors.HexColor("#C6D2DE"),
                     borderWidth=0.6, borderPadding=6,
                     backColor=colors.HexColor("#F5F8FB"))
CEX = ParagraphStyle("CEX", parent=THM, borderColor=colors.HexColor("#D9C6C6"),
                     backColor=colors.HexColor("#FBF5F5"))
CAP = ParagraphStyle("CAP", parent=sty["Italic"], fontSize=8.6, leading=11,
                     alignment=TA_CENTER, textColor=colors.HexColor("#44566B"),
                     spaceAfter=10)
CELL = ParagraphStyle("CELL", parent=BODY, fontSize=8.3, leading=10.4, spaceAfter=0,
                      alignment=TA_LEFT)
CELLH = ParagraphStyle("CELLH", parent=CELL, textColor=colors.white,
                       fontName="Helvetica-Bold")

S = []
def P(t): S.append(Paragraph(t, BODY))
def h1(t): S.append(Paragraph(t, H1))
def h2(t): S.append(Paragraph(t, H2))
def thm(t): S.append(Paragraph(t, THM))
def cex(t): S.append(Paragraph(t, CEX))
def gap(h=6): S.append(Spacer(1, h))
def cap(t):
    S.append(Paragraph(t, CAP))

C = "<font face='Courier'>%s</font>"
def c(t): return C % t


def eq(latex, fontsize=13):
    """Typeset a mathtext equation to a PNG and center it in the flow."""
    _eqn[0] += 1
    path = os.path.join(EQ_DIR, f"eq{_eqn[0]}.png")
    fig = plt.figure()
    fig.text(0.5, 0.5, f"${latex}$", fontsize=fontsize, ha="center", va="center",
             color="#12243A")
    fig.savefig(path, dpi=EQ_DPI, transparent=True, bbox_inches="tight",
                pad_inches=0.04)
    plt.close(fig)
    from PIL import Image as PILImage
    with PILImage.open(path) as im:
        pw, ph = im.size
    dw, dh = pw * 72.0 / EQ_DPI, ph * 72.0 / EQ_DPI
    maxw = 15.5 * cm
    if dw > maxw:
        s = maxw / dw
        dw, dh = dw * s, dh * s
    img = Image(path, width=dw, height=dh)
    img.hAlign = "CENTER"
    S.append(img)
    gap(6)


def table(data, colw, keep=False):
    _tab[0] += 1
    wr = [[Paragraph(str(v), CELLH if r == 0 else CELL) for v in row]
          for r, row in enumerate(data)]
    t = Table(wr, colWidths=colw)
    t.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#C8D2DC")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F3A5F"))]))
    S.append(KeepTogether(t) if keep else t)
    gap(4)


def add_figure(path, width=15.5 * cm):
    _fig[0] += 1
    from PIL import Image as PILImage
    with PILImage.open(path) as im:
        pw, ph = im.size
    img = Image(path, width=width, height=width * ph / pw)
    img.hAlign = "CENTER"
    S.append(img)
    gap(2)


# ---------------------------------------------------------------------------
# figures, generated from committed artifacts only
# ---------------------------------------------------------------------------
# CVD-validated palettes (dataviz validator: all checks pass; the borderline
# D9-C/D9-D pair additionally differs by dash pattern + direct labels, and
# phase-map cells carry letter labels so identity is never color-alone).
CLS_COLOR = {"collapse": "#D55E00", "safe_rationing": "#E69F00",
             "safe_service": "#0072B2"}
CLS_LETTER = {"collapse": "C", "safe_rationing": "R", "safe_service": "S"}
ARM_STYLE = {  # D9 trajectory series: color, dash, label
    "D9-A": ("#0072B2", "-", "D9-A  P1 reserve-blind"),
    "D9-B": ("#D55E00", "-", "D9-B  soft penalty"),
    "D9-C": ("#009E73", "-", "D9-C  P1C (chi=1)"),
    "D9-D": ("#CC79A7", "--", "D9-D  P1C (chi=0)"),
}


def fig_d9_trajectories() -> str:
    """Source-stock trajectories of the four D9 arms, straight from the
    committed per-tick trace (x_after[0] per valid tick)."""
    series = {}
    with gzip.open("results/v2.9/d9_d10/v29_d9_d10_trace.jsonl.gz", "rt",
                   encoding="utf-8") as fh:
        for line in fh:
            rec = json.loads(line, parse_constant=_strict)
            if rec["run_id"] in ARM_STYLE:
                ix = rec["schema"].index("x_after")
                series[rec["run_id"]] = [row[ix][0] for row in rec["rows"]]
    if set(series) != set(ARM_STYLE):
        raise SystemExit("FATAL: D9 arms missing from committed trace")
    fig, ax = plt.subplots(figsize=(7.6, 3.4), dpi=200)
    for rid in ("D9-A", "D9-B", "D9-C", "D9-D"):
        col, ls, lab = ARM_STYLE[rid]
        ax.plot(range(1, len(series[rid]) + 1), series[rid], ls, color=col,
                lw=1.6 if rid != "D9-D" else 1.4, label=lab)
    ax.axhline(11.0, color="#666F7A", lw=0.9, ls=(0, (4, 3)))
    ax.axhline(5.0, color="#9AA3AD", lw=0.9, ls=(0, (1, 2)))
    ax.text(201, 11.0, " R_eff = 11", va="center", fontsize=7.5, color="#44566B")
    ax.text(201, 5.0, " Allee A = 5", va="center", fontsize=7.5, color="#6B7683")
    ax.text(100, 9.6, "D9-C / D9-D (identical, held at reserve)", fontsize=7.5,
            color="#00694D")
    ax.text(60, -2.6, "D9-A / D9-B collapse", fontsize=7.5, color="#8A3D00")
    ax.set_xlim(0, 232)
    ax.set_ylim(-5.8, 18.5)
    ax.set_xlabel("tick", fontsize=8.5)
    ax.set_ylabel("source stock  $x_0$", fontsize=8.5)
    ax.tick_params(labelsize=8)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.grid(axis="y", color="#E4E8EC", lw=0.6)
    ax.set_axisbelow(True)
    ax.legend(fontsize=7.5, frameon=False, loc="upper center", ncol=2,
              bbox_to_anchor=(0.5, 1.02))
    path = os.path.join(EQ_DIR, "fig_d9.png")
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return path


def fig_d10_phasemap() -> str:
    """Core D10 phase map (4 small multiples, one per policy), colored by
    committed primary classification with in-cell letters."""
    dgs = sorted({r["d_over_gmax"] for r in D10_CORE})
    etas = sorted({r["eta"] for r in D10_CORE})
    fig, axes = plt.subplots(1, 4, figsize=(9.6, 2.9), dpi=200, sharey=True)
    for ax, pol in zip(axes, POLICIES):
        for yi, dg in enumerate(dgs):
            for xi, eta in enumerate(etas):
                r = next(r for r in D10_CORE if r["policy"] == pol
                         and r["d_over_gmax"] == dg and r["eta"] == eta)
                cls = r["primary_classification"]
                ax.add_patch(plt.Rectangle((xi, yi), 0.94, 0.94,
                                           facecolor=CLS_COLOR[cls], lw=0))
                ax.text(xi + 0.47, yi + 0.47, CLS_LETTER[cls], ha="center",
                        va="center", fontsize=8.5, color="white",
                        fontweight="bold")
        ax.set_xlim(-0.06, len(etas)); ax.set_ylim(-0.06, len(dgs))
        ax.set_xticks([i + 0.47 for i in range(len(etas))],
                      [f"{e:g}" for e in etas], fontsize=7.5)
        ax.set_yticks([i + 0.47 for i in range(len(dgs))],
                      [f"{d:g}" for d in dgs], fontsize=7.5)
        ax.set_title(pol, fontsize=9)
        ax.set_xlabel(r"$\eta$", fontsize=8.5)
        ax.set_aspect("equal")
        for side in ("top", "right", "left", "bottom"):
            ax.spines[side].set_visible(False)
        ax.tick_params(length=0)
    axes[0].set_ylabel(r"$d\,/\,g_{max}$", fontsize=8.5)
    handles = [plt.Rectangle((0, 0), 1, 1, facecolor=CLS_COLOR[k])
               for k in ("safe_service", "safe_rationing", "collapse")]
    fig.legend(handles, ["S safe_service", "R safe_rationing", "C collapse"],
               ncol=3, fontsize=8, frameon=False, loc="lower center",
               bbox_to_anchor=(0.5, -0.04))
    path = os.path.join(EQ_DIR, "fig_d10.png")
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return path


# ---------------------------------------------------------------------------
# fmt helpers
# ---------------------------------------------------------------------------
def f2(v): return f"{v:.2f}"
def f3(v): return f"{v:.3f}"


# =========================== title page ===========================
S.append(Spacer(1, 2.4 * cm))
S.append(Paragraph("The Energy Balance Project", TITLE)); gap(6)
S.append(Paragraph("Local Preservation &mdash; Version 2.9", SUB))
S.append(Paragraph("A source-local safe-export budget, the P1C preservation "
                   "controller, and its deterministic validation", SUB))
gap(16)
S.append(HRFlowable(width="60%", color=colors.HexColor("#1F3A5F"), thickness=1))
gap(16)
P("<b>Status: research note with deterministic numerical validation. NOT PEER "
  "REVIEWED.</b> Passing tests are validation at declared fixture points, never "
  "mathematical proof. No claim of general stability, stochastic robustness, or "
  "monetary validity is made anywhere in this document.")
P("<b>Provenance.</b> Every number, table, and figure below is generated at "
  "compile time from the committed machine-readable artifacts in "
  + c("results/v2.9/") + " by " + c("make_paper_v29.py") + "; the build aborts on "
  "any plan-hash or headline mismatch. Authoritative text source: "
  + c("Foundation_v2.9_local_preservation.md") + ". Locked plan hashes: "
  "deterministic " + c(DET_PLAN_HASH[:16] + "&hellip;") + ", D9/D10 "
  + c(D9D10_PLAN_HASH[:16] + "&hellip;") + ".")
P("<b>The V2.9 question.</b> <i>Can a spatially local process determine how much "
  "a regenerative source may safely export, preserve its certified reserve, and "
  "reveal infeasible demand &mdash; without evaluating the whole world or "
  "simulating its future?</i>")
P("Author: Konrad Grzyb. Independent research project; not affiliated with any "
  "university or institution, and not affiliated with the EU-funded "
  "eBalance-Plus project.")
S.append(PageBreak())

# =========================== 1. motivation ===========================
h1("1. Motivation and the original project objective")
P("The Energy Balance Project asks whether <b>purely local physical rules</b> can "
  "keep a resource field alive &mdash; no central optimizer, no global objective, "
  "no simulated future. Since V2.0 the model is a scalar stock field on a graph: "
  "each cell has a viable band, cells exchange stock over lossy edges, and "
  "&ldquo;health&rdquo; is a quadratic burden functional that the engine never "
  "optimizes &mdash; survival must emerge or fail on its own.")
P("The project&rsquo;s stated long-term objective (V2.9 objective-alignment "
  "draft, &sect;1) is not maximal service. It is an <b>honest physical "
  "sustainability signal</b>, in priority order: (1) preserve the regenerative "
  "foundation; (2) calculate and report the true sustainable allowance; "
  "(3) record ecological debt whenever consumption exceeds it; and only then "
  "(4)&ndash;(6) build EBU accounting and economic layers. Two guardrails bind "
  "every future layer: <b>no laundering by price</b> (cost is never permission "
  "for irreversible harm) and <b>no laundering by transfer</b> (moving tokens "
  "redistributes responsibility, never reduces planetary debt).")
P("V2.9 is the stage where <b>preservation</b> first gets a concrete, testable, "
  "purely local mechanism, and the <b>sustainable allowance</b> gets its first "
  "formula: a safe-export budget a source computes from its own frozen state. "
  "The deterministic answer, in the fixtures tested: <b>yes for one-step reserve "
  "preservation and honest rationing</b> &mdash; with sharp, recorded limits: "
  "feasibility is separate (no export rule can create it), and nothing here "
  "proves long-horizon or stochastic viability (&sect;15&ndash;16).")

# =========================== 2. V2.8 baseline ===========================
h1("2. What was known at V2.8")
P("V2.7 proved a continuous-time energy&ndash;dissipation identity for the "
  "idealized Onsager transport law: along solutions,")
eq(r"\frac{dV}{dt} \;=\; \sum_i \mu_i u_i \;-\; \sum_e \left( \frac{J_e^2}{M_e} + \theta_e J_e \right),")
P("where <i>V</i> is the total burden (per-cell quadratic penalties), "
  "&mu;<sub>i</sub> = &part;V/&part;x<sub>i</sub> the local marginal, "
  "u<sub>i</sub> the local natural drive (supply + regeneration &minus; demand "
  "&minus; leakage), and each edge <i>e</i> (mobility M<sub>e</sub>, threshold "
  "&theta;<sub>e</sub>, efficiency &eta;<sub>e</sub>) carries the loss-aware flux "
  "J<sub>e</sub> = M<sub>e</sub>[&mu;<sub>i</sub> &minus; &eta;<sub>e</sub>"
  "&mu;<sub>j</sub> &minus; &theta;<sub>e</sub>]<sub>+</sub>. Transport can only "
  "dissipate; only drive can raise the burden.")
P("V2.8 crossed half the continuous&rarr;discrete gap. For <b>Model D0</b> "
  "&mdash; the synchronous, frozen-state, <b>unconstrained</b>, loss-aware "
  "explicit-Euler law")
eq(r"x^{n+1} \;=\; x^{n} + \Delta t\,\left( u(x^{n}) + S\,J(x^{n}) \right)")
P("&mdash; it proved the finite-step burden inequality (V2.8 Thm 4.4/6.1):")
eq(r"V(x^{n+1}) - V(x^{n}) \;\leq\; \Delta t\,\mu^{\top} u \;-\; "
   r"\Delta t \sum_e \left( \frac{J_e^2}{M_e} + \theta_e J_e \right) \;+\; "
   r"\frac{L_V \Delta t^2}{2}\, \| u + S J \|^2,")
P("drive minus dissipation plus an explicit step-size penalty, with a corrected "
  "curvature constant L<sub>V</sub> that <b>sums</b> simultaneously active "
  "penalty weights. Its &sect;11 scope list excludes clipping, projection, "
  "spill, saturation, hard-reserve constraints, and sequential updates: "
  "<b>any constrained flow is outside the V2.8 theorem</b>. That exclusion is "
  "exactly where V2.9 begins &mdash; a preservation controller must constrain "
  "flows, so it must bring its own mathematics.")

# =========================== 3. soft not hard ===========================
h1("3. Why soft penalties are not hard preservation")
P("The burden can include a reserve term &chi;<sub>i</sub>[R<sub>i</sub> &minus; "
  "x<sub>i</sub>]<sub>+</sub>&sup2; that penalizes dipping below a reserve. It "
  "shapes the force: as the source falls toward R, the reserve marginal "
  "&minus;2&chi;(R &minus; x)<sub>+</sub> pushes against export. But it is "
  "<b>soft</b>, and the algebra says why it cannot guarantee anything:")
cex("<b>Observation (alignment draft 5.1).</b> The reserve penalty and its "
    "derivative both vanish at x = R itself. At the boundary there is no force "
    "left; one more finite tick of demand steps straight through. A soft penalty "
    "can <i>delay</i> damage &mdash; in D9 it measurably does (&sect;10) &mdash; "
    "but it cannot <i>forbid</i> it. Hard preservation needs a constraint, not a "
    "gradient.")

# =========================== 4. safe-export budget ===========================
h1("4. The safe-export budget")
P("Freeze one source cell at tick start: stock x, local drive u, timestep "
  "&Delta;t, certified effective reserve R<sup>eff</sup>. If the source exports "
  "an aggregate rate Q for one tick (ignoring incoming flow, which only helps), "
  "its successor is x&prime; = x + &Delta;t(u &minus; Q). Requiring x&prime; "
  "&ge; R<sup>eff</sup> and solving for Q gives the largest reserve-safe "
  "aggregate export rate; with explicit physical measurement margins "
  "&epsilon;<sub>x</sub> (stock) and &epsilon;<sub>u</sub> (drive) it becomes "
  "the <b>robust budget</b> (Amendment 4, A4.5):")
eq(r"Q_{max} = \frac{\left[\, x + \Delta t\,u - R^{\mathrm{eff}} \,\right]_+}{\Delta t}"
   r"\,,\qquad Q_{max}^{rob} = \frac{\left[\, (x-\epsilon_x) + \Delta t\,(u-\epsilon_u)"
   r" - R^{\mathrm{eff}} \,\right]_+}{\Delta t}.")
P("Every symbol is local: the source&rsquo;s own stock, drive, reserve "
  "certificate, and the tick length. No global state, no other cell, no future "
  "rollout. Two structural points (both from the independent Gate-2.1B review, "
  "which corrected the first design): the budget governs <b>the sum, not each "
  "edge</b> (else k edges could export k&middot;Q<sub>max</sub>); and "
  "<b>feasibility is a separate hypothesis</b> &mdash; Q<sub>max</sub> = 0 means "
  "&ldquo;no export allowed&rdquo;, not &ldquo;safe&rdquo;.")
cex("<b>Feasibility counterexample (review Obs 4.2).</b> With g &equiv; 0, "
    "u = &minus;&delta; &lt; 0 and x = R<sup>eff</sup>, even zero export gives "
    "x&prime; = R<sup>eff</sup> &minus; &Delta;t&delta; &lt; R<sup>eff</sup>. "
    "When natural decline alone crosses the reserve, no export rule can preserve "
    "it; the controller must <i>report</i> that state, never claim to have "
    "prevented it.")
P("This yields the action-time state classification, computed from frozen local "
  "data only (" + c("p1c_v29.classify_state") + "):")
table([["State", "Condition", "Export"],
       ["P (preservable)", "x &ge; R<sup>eff</sup> and x + &Delta;t&middot;u &ge; R<sup>eff</sup>",
        "up to Q<sub>max</sub><sup>rob</sup> (regenerative)"],
       ["R (recovery required)", "x &lt; R<sup>eff</sup>", "zero"],
       ["I (locally infeasible)", "x &ge; R<sup>eff</sup> but x + &Delta;t&middot;u &lt; R<sup>eff</sup>",
        "zero &mdash; and zero cannot save the boundary; reported explicitly"],
       ["F (flow source)", "external renewable flow", "declared flow cap; no stock reserve"]],
      [3.4 * cm, 7.2 * cm, 5.0 * cm])
P("Finite and irreversible stocks get a <b>zero</b> preservation-safe budget "
  "even in state P: positive extraction of a non-regenerating stock is "
  "depletion, not preservation.")

# =========================== 5. allocation ===========================
h1("5. Aggregate multi-edge allocation")
P("When a source&rsquo;s edges request more than its budget &mdash; aggregate "
  "raw request Q<sub>req</sub> = &Sigma;<sub>e</sub> q<sub>e</sub><sup>req</sup> "
  "exceeding Q<sub>max</sub><sup>rob</sup> &mdash; P1C scales <b>all</b> of that "
  "source&rsquo;s outgoing requests by one factor computed from frozen state:")
eq(r"\sigma = \min\!\left(1,\; \frac{Q_{max}^{rob}}{Q_{req}}\right),\qquad "
   r"q_e^{acc} = \sigma\, q_e^{req}.")
P("Proportional scaling keeps the decision local (one number per source), treats "
  "edges symmetrically, and composes with the synchronous update without "
  "ordering artifacts. Raw requests are the unmodified loss-aware D0 fluxes "
  "(reused, not forked). Uncommitted <b>incoming</b> flow is excluded from the "
  "budget: a source must stay safe even if every upstream neighbor withholds "
  "this tick; delivered incoming flow appears only as a diagnostic.")

# =========================== 6. tick sequence ===========================
h1("6. The P1C tick sequence")
P("One P1C tick (" + c("p1c_v29.p1c_step") + "), in frozen order:")
table([["Step", "Action"],
       ["1", "<b>Freeze</b> the state vector; compute each cell&rsquo;s local drive u<sub>i</sub> from its own frozen stock (D0 semantics, unchanged)."],
       ["2", "<b>Gather</b> raw loss-aware edge requests q<sub>e</sub><sup>req</sup> from frozen local views (the D0 local law, unchanged)."],
       ["3", "<b>Classify</b> each configured source (P/R/I/F) and compute its ONE aggregate safe-export budget (&sect;4)."],
       ["4", "<b>Scale</b> that source&rsquo;s requests proportionally when they exceed the budget (&sect;5)."],
       ["5", "<b>Apply</b> all accepted flows in one simultaneous update: the source loses the full withdrawal q<sub>e</sub><sup>acc</sup>; the destination receives only &eta;<sub>e</sub> q<sub>e</sub><sup>acc</sup>."],
       ["6", "<b>Count service after transport loss</b>: delivered service is &eta;<sub>e</sub> q<sub>e</sub><sup>acc</sup>, never the pre-loss withdrawal."],
       ["7", "<b>Report unmet demand explicitly</b>: the requested&ndash;delivered gap is a first-class output, never renamed, never hidden."]],
      [1.2 * cm, 14.4 * cm])
eq(r"x_i^{n+1} \;=\; x_i \;+\; \Delta t \left( u_i \;+\; \sum_{e\,\in\,\mathrm{in}(i)} "
   r"\eta_e\, q_e^{acc} \;-\; \sum_{e\,\in\,\mathrm{out}(i)} q_e^{acc} \right)")
P("Everything on the decision path reads frozen local data only. The global "
  "functional V is computed <i>after</i> the update by the researcher harness as "
  "a diagnostic &mdash; never by the controller (enforced by AST tests).")

# =========================== 7. theorem ===========================
h1("7. The one-step preservation result")
thm("<b>Theorem (one-step aggregate reserve preservation; Gate-2.1B review, "
    "Thm 4.1).</b> Fix a tick. Suppose a protected regenerative source i "
    "satisfies, on its frozen state: (1) x<sub>i</sub> &ge; R<sub>i</sub>"
    "<sup>eff</sup>; (2) x<sub>i</sub> + &Delta;t&middot;u<sub>i</sub> &ge; "
    "R<sub>i</sub><sup>eff</sup> (its no-export successor remains feasible "
    "&mdash; state P); and (3) its aggregate accepted export satisfies "
    "Q<sub>i</sub><sup>acc</sup> &le; Q<sub>i,max</sub>, where")
eq(r"Q_{i,\max} \;=\; \frac{\left[\, x_i + \Delta t\, u_i - R_i^{\mathrm{eff}} \,\right]_+}{\Delta t},")
thm("and the synchronous update of &sect;6 step 5 is applied. Then "
    "x<sub>i</sub><sup>n+1</sup> &ge; R<sub>i</sub><sup>eff</sup>.")
P("<b>Proof.</b> Incoming flow is non-negative, so x<sub>i</sub><sup>n+1</sup> "
  "&ge; x<sub>i</sub> + &Delta;t&middot;u<sub>i</sub> &minus; &Delta;t&middot;"
  "Q<sub>i</sub><sup>acc</sup>. By (3), &Delta;t&middot;Q<sub>i</sub><sup>acc"
  "</sup> &le; [x<sub>i</sub> + &Delta;t u<sub>i</sub> &minus; R<sub>i</sub>"
  "<sup>eff</sup>]<sub>+</sub>, which under (2) equals x<sub>i</sub> + "
  "&Delta;t u<sub>i</sub> &minus; R<sub>i</sub><sup>eff</sup>. Hence "
  "x<sub>i</sub><sup>n+1</sup> &ge; R<sub>i</sub><sup>eff</sup>. &#8718;")
P("With the robust budget the same algebra holds whenever the true stock and "
  "drive lie within the declared margins &epsilon;<sub>x</sub>, "
  "&epsilon;<sub>u</sub>. P1C satisfies hypothesis (3) by construction "
  "(&sigma; &le; Q<sub>max</sub><sup>rob</sup>/Q<sub>req</sub>), so every "
  "state-P tick is an instance of the theorem; the harness records per-tick "
  "conformance.")
cex("<b>What this theorem is not.</b> A one-step algebraic statement under "
    "explicit hypotheses. It is NOT: an infinite-horizon sustainability theorem; "
    "a proof of global homeostasis; a proof for arbitrary (asynchronous, "
    "sequential) actor scheduling; a proof under model uncertainty beyond the "
    "declared &epsilon; margins; a proof of complete service (P1C rations "
    "precisely when demand is unsafe); or an EBU accounting theorem (no EBU "
    "exists in V2.9). Feasibility (hypothesis 2) is an assumption, not a "
    "conclusion.")
h2("Relationship to V2.8")
P("The V2.8 finite-step inequality holds for the <b>unconstrained</b> D0 flux; "
  "capping the aggregate export changes the flux, so that theorem does "
  "<b>not</b> transfer to P1C (every P1C tick record carries "
  + c("covered_by_v28_theorem = False") + "). P1C carries its own one-step "
  "reserve algebra (above) plus numerical conformance checks "
  "(" + c("test_v29_p1c.py") + ", 83 checks). The <b>joint</b> theorem &mdash; "
  "constrained preservation <i>and</i> a dissipation/descent inequality for the "
  "capped flux &mdash; remains open (&sect;16).")

# =========================== 8. feasibility ===========================
h1("8. Feasibility: recovery-required and infeasible states")
P("The P/R/I/F classifier makes the negative cases first-class outputs. "
  "<b>State R</b> (x &lt; R<sup>eff</sup>): the reserve is already breached; "
  "export is zero; recovery is up to the source&rsquo;s own regeneration "
  "&mdash; P1C makes no recovery claim. <b>State I</b> (x &ge; R<sup>eff</sup> "
  "but x + &Delta;t&middot;u &lt; R<sup>eff</sup>): natural decline alone will "
  "cross the reserve this tick; export is zero AND the controller reports "
  + c("zero_export_insufficient = true") + ". This is the honest-signal case: "
  "the demand structure is infeasible for this source and no local export rule "
  "can fix it &mdash; the information must go up to whatever layer sets demand.")
P("D10&rsquo;s demand axis deliberately crosses both analytic boundaries: "
  "d/g<sub>max</sub> = 1 is the logistic fold (maximum sustainable "
  "regeneration), and delivering demand d through an edge of efficiency &eta; "
  "requires d &le; &eta;&middot;g<sub>max</sub>. Points with &eta; &lt; "
  "d/g<sub>max</sub> &lt; 1 are regeneration-feasible but transport-infeasible: "
  "the committed map (&sect;11) shows P1C rationing exactly there.")

# =========================== 9. D1-D8 ===========================
h1("9. D1&ndash;D8: deterministic validation of the substrate")
P("Before any preservation experiment, V2.9 Gate 2 ran a preregistered "
  "deterministic wind tunnel (plan hash " + c(DET_PLAN_HASH[:16] + "&hellip;")
  + ", 24 runs, fixtures D1&ndash;D8) on the frozen D0 engine "
  + c("d0_v29.py") + ", comparing P0 (no transport), P1 (exact D0), P1K "
  "(diagnostic projection wrapper), and ablations P2 (loss-blind force), P3 "
  "(sequential live-state), P4 (oversized step &mdash; deliberately unsafe). "
  "Headline committed outcomes:")
_fa = DET["fixture_analyses"]
table([["Fixture", "Question", "Committed outcome"],
       ["D1", "lossless relaxation", "P1 drives V 17.0 &rarr; 6.3&times;10<sup>&minus;30</sup>, zero descent violations; P0 exactly constant."],
       ["D2", "lossy transport vs loss-blind ablation",
        f"P1 rests where the loss-aware force &asymp; &theta; ({_fa['D2']['p1_final_loss_aware_force']:.4f} vs &theta; = 0.05) while the loss-blind force is still {_fa['D2']['p1_final_loss_blind_force']:.2f}; final V: P1 {_fa['D2']['V_final_P1']:.2f} &lt; P2 {_fa['D2']['V_final_P2']:.2f} (11 descent violations recorded for P2)."],
       ["D3", "one-tick causality",
        f"synchronous P1: probe difference 0.0 at tick 1, first difference at tick {_fa['D3']['paired_probe_differences']['P1']['first_probe_diff_tick']}; sequential P3 leaks {_fa['D3']['paired_probe_differences']['P3']['tick1_probe_diff']:.4f} at tick 1."],
       ["D4/D6/D7", "driven service + shocks",
        "P1 serves 100% of feasible demand from admissible stock and recovers after supply/demand shocks (recovery ticks 440 and 611); P0 exits the physical domain."],
       ["D5", "Allee reserve pressure",
        "<b>did NOT discriminate</b>: penalty ON and OFF arms identical on headline outcomes (both converged, both served 150/150, no Allee crossings). Retained; motivated D9."],
       ["D8", "oversized-step negative control",
        f"tick-1 overshoot ratio exactly {_fa['D8']['p4_tick1_ratio']:.2f} as registered; the monotone-growth sub-claim FAILED (recorded, not repaired). Certified contrast non-increasing."]],
      [1.7 * cm, 3.6 * cm, 10.3 * cm])
P("Interpretation limits are frozen in the plan: deterministic fixtures only; a "
  "success is evidence the law <i>can</i> work in that fixture, never that it "
  "always works. P1K is a diagnostic projection wrapper whose ledger closes by "
  "construction &mdash; closure never certifies that delivered stock was "
  "physically available, so P1K can never found a physical-service claim.")

# =========================== 10. D9 ===========================
S.append(PageBreak())
h1("10. D9: the Allee reserve-stress experiment")
P("D9 (four arms, 200 ticks, &Delta;t = 0.2) puts an Allee source (A = 5, "
  "K = 20, certified R<sup>eff</sup> = 11) under sustained demand 5.0 &mdash; "
  "deliberately hard enough that unconstrained transport breaches the reserve. "
  "All values below are read from the committed summary at build time.")
_d9rows = [["Arm", "Policy", "Class", "Reserve crossed", "Allee crossed",
            "O_physical", "Delivered", "Unmet"]]
for rid, pol in (("D9-A", "P1 reserve-blind"), ("D9-B", "soft (&chi;=1)"),
                 ("D9-C", "P1C (&chi;=1, cap)"), ("D9-D", "P1C (&chi;=0, cap)")):
    r = RUNS[rid]
    _d9rows.append([
        rid, pol, r["primary_classification"].replace("_", " "),
        f"tick {r['first_reserve_crossing_tick']}" if r["first_reserve_crossing_tick"] else "never",
        f"tick {r['first_allee_crossing_tick']}" if r["first_allee_crossing_tick"] else "never",
        f"{r['O_physical']:.3f}" if r["O_physical"] > 1e-9 else "&le; 10<sup>&minus;9</sup>",
        f2(r["cumulative_delivered"]), f2(r["cumulative_unmet_demand"])])
table(_d9rows, [1.3 * cm, 2.9 * cm, 2.3 * cm, 1.9 * cm, 1.9 * cm, 2.3 * cm,
                2.0 * cm, 1.6 * cm])
cap(f"Table: the four committed D9 arms (results/v2.9/d9_d10). P1C binding on "
    f"{RUNS['D9-C']['p1c_binding_ticks']}/200 ticks; "
    f"{RUNS['D9-C']['theorem_eligible_ticks']} theorem-eligible ticks with "
    f"{RUNS['D9-C']['theorem_violation_count']} observed violations.")
add_figure(fig_d9_trajectories())
cap("Figure: committed D9 source-stock trajectories (from the per-tick trace). "
    "Reserve-blind (D9-A) and soft (D9-B) cross R<sup>eff</sup> at tick 8 and "
    "the Allee threshold at ticks 17 and 24; both P1C arms hold the source at "
    "exactly R<sup>eff</sup> = 11 for all 200 ticks.")
P("Readings. The soft penalty <b>delayed</b> the Allee crossing (tick 24 vs 17) "
  "and reduced over-use (183.0 vs 201.8) but crossed the reserve at the "
  "<b>same tick 8</b>: it slows damage, it does not prevent it (&sect;3). Both "
  "P1C arms held the source at exactly R<sup>eff</sup> = 11 (final = minimum = "
  "11.0) with zero reserve and zero Allee crossings, the cap binding on 193/200 "
  "ticks, and <b>zero observed one-step-preservation violations over 200 "
  "eligible ticks</b>. P1C delivered less (130.8 vs 189.7) and reported the "
  "difference honestly as unmet demand (69.2): the demand was physically "
  "unsafe, and rationing &mdash; not silent depletion &mdash; is the designed "
  "behavior. <b>D9-C and D9-D are identical on every recorded metric: the hard "
  "cap, not &chi;, provides preservation in this fixture.</b>")

# =========================== 11. D10 ===========================
h1("11. D10: the service-versus-preservation phase map")
P("D10 sweeps a logistic source&ndash;sink world (140 runs: an 80-run core map "
  "over demand ratio d/g<sub>max</sub> &isin; {0.25, 0.5, 0.9, 1.0, 1.1} "
  "&times; transport efficiency &eta; &isin; {0.5, 0.7, 0.9, 1.0}, plus 60 "
  "secondary-slice runs over &theta;, &delta;/K, &chi;, &rho;, r<sub>dt</sub>), "
  "four policies at every point. Committed classification counts (35 runs per "
  "policy):")
_rows = [["Policy", "collapse", "safe_service", "safe_rationing",
          "runs with O_physical &gt; 10<sup>&minus;9</sup>"]]
for pol in POLICIES:
    n, cc, over = _counts(pol)
    _rows.append([pol, cc.get("collapse", 0), cc.get("safe_service", 0),
                  cc.get("safe_rationing", 0), over])
table(_rows, [2.6 * cm, 2.6 * cm, 3.0 * cm, 3.2 * cm, 4.2 * cm], keep=True)
add_figure(fig_d10_phasemap())
cap("Figure: committed D10 core phase map (classification per policy per grid "
    "point; S = safe_service, R = safe_rationing, C = collapse), generated from "
    "the summary JSON.")
P("P1 and the soft arm produce <b>identical</b> classification maps: at these "
  "demand levels the soft penalty changes nothing that matters. Collapse for "
  "P1/soft tracks the registered analytic boundaries &mdash; every core point "
  "with d/g<sub>max</sub> &ge; 0.9 collapses except at &eta; = 1.0 with "
  "d/g<sub>max</sub> &le; 0.9, plus the transport-starved corner (0.5, 0.5); "
  "safe service requires roughly d/g<sub>max</sub> &le; &eta; (deliverability) "
  "and d/g<sub>max</sub> &lt; 1 (the fold). P1C never collapses and never "
  "over-uses; where full service is deliverable it serves (25 points), where it "
  "is not it rations (10 points). Hypothesis H-D10-1 held at all tested points. "
  "18 runs (P1/soft at the hardest corners) diverged and exited the physical "
  "domain; all 18 domain exits are <b>recorded, not dropped</b>.")
cex("<b>P0&rsquo;s 35 &ldquo;safe rationing&rdquo; runs are not success.</b> No "
    "transport trivially preserves stock by serving nothing. Preservation must "
    "always be read <i>together with service</i>: P1C matches P1&rsquo;s "
    "service wherever service was safe, and refuses only the unsafe remainder.")

# =========================== 12. serialization ===========================
h1("12. Serialization provenance (Attempt 1, Attempt 2, the repair)")
P("The D9/D10 study has a fully documented execution history. <b>Attempt 1 "
  "failed</b> (harness-integrity defect found by Gate 2.4A before any "
  "scientific use) and is preserved verbatim (" + c("ATTEMPT_1_FAILURE.md")
  + "); it produced no scientific result. <b>Attempt 2 ran exactly once</b> "
  "(implementation commit " + c("12faa53&hellip;") + ", plan hash unchanged) and "
  "produced all 144 registered runs. <b>No physical trajectory was ever "
  "regenerated after that run.</b>")
P("On 15 diverging runs the two aggregate stability diagnostics "
  "(" + c("stability_tau") + ", " + c("stability_amp") + ") overflowed to "
  "infinity; under explicit authorization they were post-processed to JSON "
  "null &mdash; values only, no classification, trajectory, or other metric "
  "changed. Three further domain-exit records were <b>natively undefined</b> "
  "(exit before the 100-tick burn-in left an empty diagnostic window), so the "
  "committed summary contains 18 null diagnostic pairs: 15 repairs + 3 native "
  "(" + c("ATTEMPT_2_SERIALIZATION_REPAIR.md") + "). Gate 2.4B then made future "
  "serialization <b>fail closed</b>: strict JSON (allow_nan=False) everywhere, "
  "one narrowly scoped normalization for the two nullable diagnostics (with "
  "recorded reasons), and a hard error for a non-finite value in any state, "
  "flow, service, unmet-demand, crossing, classification, over-use, ledger, or "
  "timestep field (" + c("serialization_v29.py") + ", 46 checks).")

# =========================== 13. what failed ===========================
h1("13. What failed, and why it is kept")
P("Negative and partial results are retained as first-class outputs: "
  "<b>D5 failed to discriminate</b> (the fixture was too easy; D9 was designed "
  "from that failure). <b>The soft penalty failed in D9/D10</b> exactly as the "
  "algebra predicts: delay, not prevention. <b>Unconstrained P1 collapses and "
  "over-uses</b> across 25/35 of the D10 map &mdash; the honest baseline "
  "preservation must beat. <b>D8&rsquo;s monotone-growth sub-claim failed</b> "
  "(overshoot fired exactly at tick 1 but did not keep growing). <b>Attempt 1 "
  "of D9/D10 failed</b> on harness integrity and is preserved. <b>The stability "
  "diagnostics overflowed</b> on diverging runs &mdash; a serialization defect, "
  "fixed fail-closed (&sect;12). Inherited from V2.6 and still open: the "
  "guarded EBU ledger is <b>exploitable on at least one topology</b> (+260 EBU "
  "while every source dies); any future credit rule inherits that risk until "
  "re-audited.")

# =========================== 14. EBU relationship ===========================
h1("14. Relationship to future EBU accounting")
P("V2.9 is a <b>physical controller layer</b>, deliberately below any "
  "accounting. The objective-alignment documents design &mdash; but do "
  "<b>not</b> implement &mdash; the next layers: a <b>vector</b> "
  "ecological-debt ledger D = (D<sub>carbon</sub>, D<sub>water</sub>, &hellip;) "
  "with an irreversible component that never decreases and no netting between "
  "accounts; one-to-one EBU <b>restoration credit</b> only for verified net "
  "physical restoration; and the guardrails G1/G2 (&sect;1). The independent "
  "review&rsquo;s verdict on that design is &ldquo;pass with corrections&rdquo;, "
  "and it explicitly finds <b>scalar (fungible) EBU not currently justified</b> "
  "&mdash; a first implementation would use resource-specific vector accounts.")
thm("<b>None of this exists in code.</b> V2.9 contains no EBU issuance, no "
    "ecological-debt ledger, no wallet, no exchange, no scalarisation, no actor "
    "health or death, and no finite moving actor population. "
    + c("O_physical") + " is a physical over-use <i>diagnostic</i>, not issued "
    "debt.")

# =========================== 15. limitations ===========================
h1("15. Limitations and falsification criteria")
P("<b>Limitations (read before citing any result).</b> Deterministic toy worlds "
  "only (2&ndash;3 cells); no stochastic or confirmatory seed study for P1C "
  "yet; no random layouts. No finite moving actor population; no individual "
  "health or death; no complete society. No EBU issuance, debt ledger, wallets, "
  "exchange, or scalarisation. The preservation theorem is one-step, "
  "synchronous, and margin-conditional; reserve certification "
  "(R<sup>eff</sup>) is assumed given, and long-horizon viability &mdash; the "
  "infinite-horizon kernel &mdash; remains open. No proof under arbitrary "
  "uncertainty: the &epsilon; margins cover declared measurement error only, "
  "not model mis-specification. Not peer reviewed. All checks are numerical "
  "validation at declared points, never proof.")
P("<b>Falsification criteria</b> (registered in the alignment draft; fixture "
  "falsifiers in the plans). The architecture is falsified by, among others: "
  "(F-A) a trajectory labeled safe that in fact crosses a non-substitutable "
  "reserve or increases irreversible debt; (F-B) a safe-export certificate "
  "that, applied repeatedly under admissible drive, still drives a source below "
  "its reserve; (F-C) wallet transfers that reduce recorded physical debt; "
  "(F-D) damage-then-repair earning net positive credit without ending above "
  "the pre-damage baseline. A certificate architecture that cannot emit "
  "UNSUSTAINABLE/INFEASIBLE at all is rejected by construction. Within "
  "V2.9&rsquo;s committed studies, the registered falsifiers (e.g. F-D10-1: "
  "P1C collapsing while theorem assumptions hold) were <b>not</b> triggered.")

# =========================== 16. open problems ===========================
h1("16. Open mathematical and computational problems")
table([["#", "Problem"],
       ["1", "<b>Joint constrained theorem</b>: preservation PLUS a descent/dissipation inequality for the capped flux (the V2.8 analogue for P1C)."],
       ["2", "<b>Infinite-horizon controlled-invariant kernel</b> K<sub>&infin;</sub> and multi-step feasibility: when does one-step preservation compose forever?"],
       ["3", "Discrete overshoot margin for the reserve certificate (&delta;, &epsilon; sizing) and V2.7 Conjecture C-2 (reserve surrogate)."],
       ["4", "Multi-source, multi-edge joint invariance under proportional allocation (shared sinks, competing sources)."],
       ["5", "Stochastic and adversarial robustness of P1C (confirmatory seed study)."],
       ["6", "Ecological-debt attribution (overdraw &rarr; account map); an operational &ldquo;verified restoration&rdquo; predicate; multi-actor credit attribution; scalarisation weights &mdash; prerequisites for any EBU layer."],
       ["7", "Reserve certification itself: who computes R<sup>eff</sup>, how often, with what non-local ecological model (the three-timescale design in the review is a sketch, not a result)."]],
      [0.9 * cm, 14.7 * cm])

# =========================== 17. reproducibility ===========================
h1("17. Reproducibility")
P("Everything is deterministic; no seeds, no tuning knobs, no options. "
  "Validation suites (standard library, directly executable): "
  + c("test_v29.py") + " (D0 conformance, 141 checks / 15 groups), "
  + c("test_v29_behavior.py") + " (D1&ndash;D8, 108 / 9), "
  + c("test_v29_p1c.py") + " (P1C conformance, 83 / 12), "
  + c("test_v29_d9_d10.py") + " (D9/D10 harness, 114 / 20), "
  + c("test_v29_serialization.py") + " (strict serialization, 46 / 6). "
  "The committed studies are locked: " + c("exp_v29.py") + " and "
  + c("exp_v29_d9_d10.py") + " refuse to overwrite completed results, recompute "
  "their canonical plan hashes at run time, and take no options. Committed "
  "artifacts: " + c("results/v2.9/deterministic/") + " (24 runs) and "
  + c("results/v2.9/d9_d10/") + " (144 runs, gzip trace, manifest, attempt "
  "history, serialization repair audit). Python 3.14.2 was used for the "
  "committed runs. This PDF regenerates with "
  + c("venv/bin/python make_paper_v29.py") + ".")
gap(8)
S.append(KeepTogether([
    HRFlowable(width="100%", color=colors.HexColor("#C6D2DE"), thickness=0.6),
    Spacer(1, 6),
    Paragraph("<i>This note has not been peer reviewed. The one-step "
              "preservation theorem is an algebraic result under explicit "
              "hypotheses; every experimental statement is a deterministic "
              "observation at registered fixture points; the numerical suites "
              "validate, they never prove. No EBU, wallet, debt-ledger, or "
              "actor-health code exists in V2.9, and no general sustainability "
              "claim is made.</i>", THM)]))

# =========================== build ===========================
doc = SimpleDocTemplate(OUT, pagesize=A4,
                        leftMargin=2.2 * cm, rightMargin=2.2 * cm,
                        topMargin=2.0 * cm, bottomMargin=2.0 * cm,
                        title="EBU Foundation V2.9 (local preservation)",
                        author="Konrad Grzyb")
doc.build(S)
print(f"wrote {OUT}  ({_eqn[0]} typeset equations, {_fig[0]} figures, "
      f"{_tab[0]} tables)")
