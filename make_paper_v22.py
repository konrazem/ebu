"""
Generate the V2.2 research paper PDF (supersedes v2.1):
  Energy_Balance_Project_Foundation_v2.2.pdf

All numbers below come from the actual runs in test_v22.py and experiments_v22.py.
Run with the project venv:  .../venv/bin/python make_paper_v22.py
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Preformatted, Image, Table, TableStyle,
    PageBreak, HRFlowable,
)
from PIL import Image as PILImage

OUT = "Energy_Balance_Project_Foundation_v2.2.pdf"

styles = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=styles["Heading1"], fontSize=15, spaceBefore=14,
                    spaceAfter=6, textColor=colors.HexColor("#1F3A5F"))
H2 = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=12, spaceBefore=10,
                    spaceAfter=4, textColor=colors.HexColor("#2C5580"))
BODY = ParagraphStyle("BODY", parent=styles["BodyText"], fontSize=10, leading=14,
                      alignment=TA_JUSTIFY, spaceAfter=6)
TITLE = ParagraphStyle("TITLE", parent=styles["Title"], fontSize=22,
                       textColor=colors.HexColor("#1F3A5F"))
SUB = ParagraphStyle("SUB", parent=styles["Italic"], fontSize=11, alignment=TA_CENTER,
                     textColor=colors.HexColor("#2C5580"))
EQ = ParagraphStyle("EQ", fontName="Courier", fontSize=9, leading=12,
                    backColor=colors.HexColor("#F0F3F7"), borderColor=colors.HexColor("#D5DEE8"),
                    borderWidth=0.5, borderPadding=6, leftIndent=8, rightIndent=8,
                    spaceBefore=4, spaceAfter=8)
CAP = ParagraphStyle("CAP", parent=BODY, fontSize=8.5, alignment=TA_CENTER,
                     textColor=colors.HexColor("#555555"), spaceBefore=2, spaceAfter=12)

S = []
def P(t):  S.append(Paragraph(t, BODY))
def h1(t): S.append(Paragraph(t, H1))
def h2(t): S.append(Paragraph(t, H2))
def eq(t): S.append(Preformatted(t, EQ))
def gap(h=6): S.append(Spacer(1, h))


def figure(path, caption, width=15 * cm):
    im = PILImage.open(path); w, h = im.size
    S.append(Image(path, width=width, height=width * h / w))
    S.append(Paragraph(caption, CAP))


CELL = ParagraphStyle("CELL", parent=BODY, fontSize=8.5, leading=10.5, spaceAfter=0,
                      alignment=TA_LEFT)
CELLH = ParagraphStyle("CELLH", parent=CELL, textColor=colors.white,
                       fontName="Helvetica-Bold")


def table(data, colw):
    # wrap every cell in a Paragraph so long text wraps instead of overflowing
    wrapped = [[Paragraph(str(c), CELLH if ri == 0 else CELL) for c in row]
               for ri, row in enumerate(data)]
    t = Table(wrapped, colWidths=colw)
    t.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#C8D2DC")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F3A5F")),
    ]))
    S.append(t); gap(10)


# ============================================================ TITLE
S.append(Spacer(1, 3 * cm))
S.append(Paragraph("The Energy Balance Project", TITLE)); gap(6)
S.append(Paragraph("Homeostatic Field Model and Local Actor-Motion Law", SUB))
S.append(Paragraph("Foundation Document &mdash; Version 2.2 (Conservation Ledger and Safe Movement Law)", SUB))
gap(18); S.append(HRFlowable(width="60%", color=colors.HexColor("#1F3A5F"), thickness=1)); gap(18)
P("<b>Status:</b> engine hardened and re-tested. This version adds an explicit conservation "
  "ledger and a safe discrete movement law, then reports a three-model comparison, a phase map, "
  "grid-size invariance, and a supply-shock recovery test. All claims below are backed by the "
  "accompanying test suite and experiment scripts.")
gap(8)
P("<b>Headline results.</b> (1) The safe rule &mdash; gradient proposal plus an exact discrete "
  "acceptance check and a line-searched transfer size &mdash; improves on the raw gradient rule "
  "overall (lower burden and unmet demand) and is provably unable to increase burden within a tick; "
  "it is not, however, a strict improvement on every metric. (2) On a well-mixed field it holds "
  "~99.4% of cells viable with mean burden ~0.004, approximately size-insensitive across the sizes "
  "tested. (3) Homeostasis is not a point but a bounded phase region requiring supply matched to "
  "leakage. (4) When sources are clustered away from demand, both rules essentially fail (~51% "
  "viable, barely above no-rule) &mdash; a failure whose cause (locality, delay, and dissipation) is "
  "separated by the V2.2.1 audit and not yet attributed to any single factor.")
S.append(PageBreak())

# ============================================================ ABSTRACT
h1("Abstract")
P("V2.1 showed the potential-gradient movement law could sustain a distributed field indefinitely, "
  "but relied on informal accounting and on a marginal (linear) acceptance rule that can overshoot. "
  "V2.2 hardens the engine before adding any new theory. Every tick now balances an explicit "
  "conservation ledger, dX = S + G - D - Lambda - transport_loss - spill, with unmet demand recorded "
  "separately; the identity is asserted at every step and over 500-tick runs. The movement law is "
  "made safe: the gradient only proposes a direction, and a transfer executes only if an exact "
  "discrete calculation confirms B_with &lt; B_without, with the transfer size chosen by a line "
  "search that minimises the pair's combined burden. Seven new hardening tests pass (fifteen tests "
  "in total). We then compare three models &mdash; no redistribution, raw gradient, and safe &mdash; "
  "on checkerboard, random, and clustered worlds, across grid sizes, and under a supply shock, and "
  "summarise outcomes as a phase map over supply ratio and leakage.")

# ============================================================ 1
h1("1. Purpose and Relationship to Earlier Versions")
P("V2.0 specified the model; V2.1 implemented it, corrected the leakage term to be state-dependent, "
  "and gave a first empirical verdict. V2.2 does not add new physics. Following the project "
  "discipline &mdash; harden the accounting and the movement law until they are unquestionably "
  "correct before introducing regeneration or EBU accounting &mdash; it strengthens two things: the "
  "flow accounting (a conservation ledger) and the decision rule (a safe discrete acceptance test "
  "with adaptive transfer size). Actors remain stationary local processes, closest to circulation "
  "in a body.")

# ============================================================ 2
h1("2. V2.2 Corrections")
h2("2.1 Conservation ledger")
P("Each tick records every flow separately and checks the continuity identity (Law 2) exactly. "
  "Amounts are the realised values: a cell cannot leak or consume more than it holds, and capacity "
  "above K spills:")
eq("dX  =  S + G - D - Lambda - transport_loss - spill\n"
   "unmet_demand  recorded separately (demand that could not be met)\n\n"
   "per cell:  pre = x + s + g\n"
   "           actual_leak   = min(leak, pre)\n"
   "           actual_demand = min(d, pre - actual_leak)\n"
   "           unmet         = d - actual_demand\n"
   "           spill         = max(0, (pre - actual_leak - actual_demand) - K)")
P("A unit test asserts dX_realised equals the ledger sum every tick and cumulatively over a run "
  "(verified: 500 ticks, X change -67.80 == ledger dX -67.80).")

h2("2.2 Safe discrete movement law")
P("The potential gradient F_ij = mu_i - mu_j - theta_ij still selects a candidate direction, but it "
  "no longer sets the transfer amount and no longer authorises execution. Two safeguards are added.")
P("<b>Adaptive size (line search).</b> The transfer amount minimises the pair's combined burden "
  "along the transfer direction (a golden-section search on the convex piecewise-quadratic penalty), "
  "instead of the raw q = M[F]_+ which overshoots:")
eq("q*  =  argmin_{0 <= q <= q_hi}  [ ell_i(x_i - c0 - q) + ell_j(x_j + eta_ij q) ]\n"
   "q_hi = min( q_a^max,  x_i - x_i^min - c0,  (K_j - x_j)/eta_ij )")
P("<b>Exact acceptance.</b> The transfer executes only if it strictly reduces burden on the live "
  "state (V2.0 Sec. 9 with H=1):")
eq("execute  iff   B_with_action  <  B_without_action  -  epsilon")
P("Because every accepted transfer strictly reduces B and rejected ones leave the state unchanged, "
  "redistribution can never increase B within a tick. Hence Impact = B_without - B_with &gt;= 0 by "
  "construction &mdash; a provable discrete-monotonicity guarantee, confirmed empirically (worst "
  "redistribution impact over 500 dynamic ticks: +0.00e+00). The trade-off versus strict "
  "simultaneous resolution is that transfers are applied greedily, strongest force first; each is "
  "re-verified against the live state, so the guarantee holds regardless of order.")

# ============================================================ 3
h1("3. Verification")
P("All fifteen tests pass: the eight V2.0/V2.1 physics tests (bounds, conservation, loss accounting, "
  "finite and regenerative sources, the ideal-flow monotonicity proof, reproducibility, "
  "counterfactual separation) and the seven V2.2 hardening tests below.")
table([
    ["#", "V2.2 hardening test", "Result"],
    ["1", "Overflow above K recorded as spill; x capped; ledger balances", "PASS (spill=5.0, x=20)"],
    ["2", "Demand beyond capacity recorded as unmet; x floors at 0", "PASS (consumed 3, unmet 7)"],
    ["3", "Ledger balances every tick and cumulatively (500 ticks)", "PASS (dX = -67.80)"],
    ["4", "Harmful gradient proposal is rejected by the safe rule", "PASS (grad -21.56 vs safe +1.00)"],
    ["5", "Discrete monotonicity: safe B never increases (100 ticks)", "PASS (B -> 0.0000)"],
    ["6", "Redistribution impact >= 0 in the full dynamic world", "PASS (worst +0.0)"],
    ["7", "0 <= x_i <= K_i under the safe rule (500 ticks)", "PASS"],
], colw=[1 * cm, 10.5 * cm, 4 * cm])

# ============================================================ 4
h1("4. Experiments")
h2("4.1 Three models on three worlds")
P("A fixed total supply budget (supply_ratio = 2.0 x total demand, distributed among producers) so "
  "that only spatial structure differs; kappa = 0.02, eta = 0.95, n = 10, 2000 ticks.")
table([
    ["World", "Model", "viable %", "mean B", "transport loss", "unmet", "regime"],
    ["checkerboard", "none",     "50.0", "1040.0", "0",      "39599", "-"],
    ["checkerboard", "gradient", "94.6", "0.330",  "2582",   "0",     "homeostatic"],
    ["checkerboard", "safe",     "99.4", "0.004",  "2694",   "0",     "homeostatic"],
    ["random",       "none",     "47.0", "1073.6", "0",      "41975", "-"],
    ["random",       "gradient", "63.7", "200.0",  "10808",  "1248",  "deficit"],
    ["random",       "safe",     "81.5", "9.81",   "4604",   "0",     "deficit"],
    ["clustered",    "none",     "49.0", "1051.2", "0",      "40391", "-"],
    ["clustered",    "gradient", "51.6", "550.3",  "9201",   "14762", "deficit"],
    ["clustered",    "safe",     "51.0", "427.5",  "7952",   "7332",  "deficit"],
], colw=[2.9 * cm, 1.9 * cm, 1.7 * cm, 1.7 * cm, 2.6 * cm, 1.7 * cm, 2.6 * cm])
P("The safe rule gives lower burden and unmet demand overall, and higher viability in the mixed "
  "worlds. It is not a strict Pareto improvement, however: on the clustered world its viability is "
  "essentially tied with the gradient rule (51.0% vs 51.6%), and on the checkerboard it uses "
  "slightly more transport (2694 vs 2582). Structure dominates outcome: on the well-mixed "
  "checkerboard the safe rule is excellent; on a random field it rescues most cells but ~18% still "
  "starve locally; with clustered sources both rules are barely better than doing nothing (~51% vs "
  "49%).")

h2("4.2 Grid-size invariance")
P("On the checkerboard the safe rule is approximately size-insensitive across the three sizes "
  "tested: viability stays ~99.5% and mean burden stays &lt;0.01 for n = 6, 10, and 14 (36, 100, "
  "196 cells). This is evidence of size-insensitivity over the tested range, not a proof of scale "
  "invariance in general.")

h2("4.3 Phase map")
P("Sweeping supply ratio against the leakage coefficient shows homeostasis is a bounded region, not "
  "a single tuned point. Too little supply gives deficit collapse; too much supply (or too little "
  "leakage to absorb it) gives excess accumulation; a diagonal band between them is homeostatic. No "
  "oscillation regime appeared under the safe rule in this range &mdash; the acceptance safeguard "
  "makes the dynamics notably stable.")
figure("figures/phase_map.png",
       "Figure 1. Phase map of the safe rule (checkerboard, 8x8). Homeostasis (green) requires supply "
       "matched to leakage; it is flanked by deficit collapse (red) and excess accumulation (gold).")

h2("4.4 Recovery after a supply shock")
P("Inflow is set to zero for ticks 400&ndash;600. With no redistribution the field never recovers; "
  "the gradient rule recovers to 90% viability by tick 671; the safe rule recovers fastest and "
  "tightest, by tick 632. All models fall to zero viability during a total supply cut &mdash; "
  "correctly, since there is nothing to redistribute.")
figure("figures/shock_recovery.png",
       "Figure 2. Viable-cell fraction through a supply interruption (grey band). Safe (green) "
       "recovers fastest; gradient (orange) is noisier and slower; no-rule (red) does not recover.")

figure("figures/heatmap_snapshots.png",
       "Figure 3. Field capacity on the checkerboard (from V2.1). Top: the local rule holds a "
       "balanced field. Bottom: without it, producers pin at K and consumers die at 0.")

# ============================================================ 5
h1("5. Verdict")
P("<b>The V2.2 engine is trustworthy, and the safe movement law is an overall improvement.</b> The "
  "ledger makes every tick auditable and is asserted to balance; fifteen tests pass, including the "
  "ideal-flow monotonicity proof and the new discrete-monotonicity guarantee. The safe rule cannot "
  "make the field worse within a tick, rejects harmful overshoot that the raw gradient executes, and "
  "gives lower burden and unmet demand overall. It is not a strict Pareto improvement: clustered "
  "viability is statistically tied with the gradient rule, and it uses slightly more transport on "
  "the checkerboard.")
P("<b>But the model does not guarantee survival, and now shows exactly when it fails.</b> Re-checking "
  "the falsification criteria (V2.0 Sec. 13):")
table([
    ["Criterion (Sec. 13)", "V2.2 finding", "Status"],
    ["Persistent shuttling / oscillation with no benefit", "No oscillation regime under the safe rule; stable", "Not triggered"],
    ["Transport loss exceeds homeostatic benefit", "Apparent for clustered sources (~51% viable); cause not yet separated from myopia/distance", "Under audit"],
    ["Burden hides local collapse behind aggregate", "Guarded: per-cell viability + unmet demand now reported", "Mitigated"],
    ["Small coefficient change reverses conclusions", "Outcome is a bounded phase region in (supply, kappa)", "Characterised"],
    ["Counterfactual costs more than it detects", "H=1 acceptance is cheap; line search ~24 evals/transfer", "Acceptable"],
    ["Short horizon destroys long-horizon regeneration", "Not yet testable (no regenerative/Allee sources)", "Open"],
    ["EBU incentives cause gaming", "EBU not implemented", "Open"],
], colw=[6.3 * cm, 7.2 * cm, 2 * cm])
P("<b>Bottom line.</b> With the ledger and the safe rule, the movement law is a correct and honest "
  "model of local-rule homeostasis. It answers the central question conditionally: purely local, "
  "potential-driven, safety-checked transfers do sustain a distributed field indefinitely &mdash; "
  "provided (a) total supply is matched to total loss, and (b) sources are spatially close to "
  "demand. The clustered-source failure is the most valuable result, but its cause is not yet "
  "isolated: it may stem from locality, from the delay of moving capacity through neutral "
  "intermediate cells under a one-tick (H=1) acceptance rule, from transport dissipation, or from a "
  "combination. The V2.2.1 audit (multi-seed layouts, an eta=1 lossless test, and H=3/10/30 "
  "foresight) is designed to separate these causes before any conclusion is drawn.")

# ============================================================ 6
h1("6. Limitations and Next Steps")
P("1. Introduce regeneration properly &mdash; logistic resources, a minimum-regeneration (Allee) "
  "threshold, and irreversible stocks &mdash; then implement the H-tick regeneration-aware actor "
  "(Model D) and test whether short-horizon action destroys long-horizon regenerative capacity "
  "(the project's central conjecture).<br/>"
  "2. Add long-range transport variants and a distance/terrain-dependent theta to map exactly where "
  "the clustered-source failure begins.<br/>"
  "3. Sensitivity sweeps on eta, M, theta, alpha, beta to complete the phase characterisation.<br/>"
  "4. Only after the physics is trusted, add the EBU ledger as an optional overlay and test for "
  "gaming and repeated credit.")
gap(6)
P("<b>Version status.</b> V2.2 keeps the V2.0 one-field formulation and seven hard laws, and the "
  "V2.1 state-dependent leakage. It adds an audited conservation ledger and a provably safe discrete "
  "movement law. The next revision should follow only after regeneration and the H-horizon actor "
  "(Model D) are implemented and tested.")


def build():
    doc = SimpleDocTemplate(OUT, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                            topMargin=1.8 * cm, bottomMargin=1.8 * cm,
                            title="The Energy Balance Project - Foundation Model V2.2",
                            author="Energy Balance Project")
    doc.build(S)
    print("wrote", OUT)


if __name__ == "__main__":
    build()
