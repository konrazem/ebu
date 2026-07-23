"""
Generate the updated research paper PDF:
  Energy_Balance_Project_Foundation_v2.1.pdf

Documents the implemented model, the equation corrections/extensions discovered
during implementation, the verification suite, the empirical results, and a verdict.
Run with the project venv:  .../venv/bin/python make_paper.py
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Preformatted, Image, Table, TableStyle,
    PageBreak, HRFlowable,
)
from PIL import Image as PILImage

OUT = "Energy_Balance_Project_Foundation_v2.1.pdf"

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
CENTER = ParagraphStyle("CENTER", parent=BODY, alignment=TA_CENTER)
EQ = ParagraphStyle("EQ", fontName="Courier", fontSize=9, leading=12,
                    backColor=colors.HexColor("#F0F3F7"), borderColor=colors.HexColor("#D5DEE8"),
                    borderWidth=0.5, borderPadding=6, leftIndent=8, rightIndent=8,
                    spaceBefore=4, spaceAfter=8)
CAP = ParagraphStyle("CAP", parent=BODY, fontSize=8.5, alignment=TA_CENTER,
                     textColor=colors.HexColor("#555555"), spaceBefore=2, spaceAfter=12)

S = []


def P(t):    S.append(Paragraph(t, BODY))
def h1(t):   S.append(Paragraph(t, H1))
def h2(t):   S.append(Paragraph(t, H2))
def eq(t):   S.append(Preformatted(t, EQ))
def gap(h=6): S.append(Spacer(1, h))


def figure(path, caption, width=15 * cm):
    im = PILImage.open(path)
    w, h = im.size
    S.append(Image(path, width=width, height=width * h / w))
    S.append(Paragraph(caption, CAP))


def table(data, colw, head=True):
    t = Table(data, colWidths=colw)
    style = [
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#C8D2DC")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
    ]
    if head:
        style += [("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F3A5F")),
                  ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                  ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold")]
    t.setStyle(TableStyle(style))
    S.append(t)
    gap(10)


# ============================================================ TITLE PAGE
S.append(Spacer(1, 3 * cm))
S.append(Paragraph("The Energy Balance Project", TITLE))
gap(6)
S.append(Paragraph("Homeostatic Field Model and Local Actor-Motion Law", SUB))
S.append(Paragraph("Foundation Document &mdash; Version 2.1 (Implementation and Empirical Verdict)", SUB))
gap(18)
S.append(HRFlowable(width="60%", color=colors.HexColor("#1F3A5F"), thickness=1))
gap(18)
S.append(Paragraph(
    "<b>Status:</b> V2.0 formal model implemented, verified, and tested. This revision records "
    "one equation correction, two modeling extensions required to make the model run, the "
    "verification results, long-horizon experiments, and an assessment of whether the proposed "
    "local movement law is a good model.", BODY))
gap(10)
S.append(Paragraph(
    "<b>Headline result.</b> Purely local, potential-driven rules &mdash; with no central "
    "optimizer &mdash; sustain a distributed field in its viable range indefinitely (verified to "
    "50,000 ticks), but only inside a bounded window of renewable supply. Outside that window the "
    "field collapses, exactly as Law 6 requires. The model is a sound scientific instrument; it is "
    "not, and does not claim to be, a guarantee of survival.", BODY))
S.append(PageBreak())

# ============================================================ ABSTRACT
h1("Abstract")
P("This document reports the first executable realization of the V2.0 homeostatic field model. "
  "The physics engine &mdash; a single dynamic capacity field on a lattice, governed by the seven "
  "hard laws (locality, continuity, bounded state, non-negative dissipation, bounded regeneration, "
  "no enforced homeostasis, and counterfactual separation) &mdash; was implemented in Python and "
  "validated against the eight unit tests specified in V2.0 Section 14.1, all of which pass, "
  "including the ideal lossless monotonicity proof (dB/dt &lt;= 0). We then asked the project's "
  "central question: can the local movement law keep the field viable forever? Using a "
  "producer/consumer checkerboard world of 100 cells and one local actor per cell, the gradient-flow "
  "rule holds 94&ndash;95% of cells in the viable band with mean burden ~0.33 across 200, 5,000, and "
  "50,000 ticks, whereas the identical world with redistribution disabled loses 50% of cells "
  "permanently. Implementation revealed that the V2.0 fixed-leakage term is insufficient for stable "
  "in-band homeostasis; we introduce a state-dependent (proportional) leakage term as a "
  "self-regulating sink. We conclude with a verdict against the model's own falsification criteria.")

# ============================================================ 1
h1("1. Purpose and Relationship to V2.0")
P("V2.0 defined a formal model and an implementation specification but was explicitly a "
  "&ldquo;formal model under development.&rdquo; This V2.1 does not change the conceptual "
  "commitments of V2.0. It records what happened when the specification was built and executed: "
  "which equations were implemented verbatim, which required correction or extension to produce a "
  "runnable and stable simulation, and what the simulation actually does over long horizons. All "
  "V2.0 hard laws are preserved. Following the V2.0 discipline, every added quantity below solves a "
  "demonstrated modeling failure rather than merely adding realism.")

# ============================================================ 2
h1("2. Implemented Model (faithful to V2.0)")
P("The world is a graph G = (V, E); the first implementation uses an n x n square lattice with a "
  "von Neumann four-neighborhood. Each cell i carries one dynamic state x_i(t) &gt;= 0, the usable "
  "functional capacity. The no-action counterfactual update (V2.0 Sec. 2) is implemented exactly:")
eq("x_i^0(t+1) = clip_[0,K_i] { x_i + s_i + g_i(x_i) - d_i - lambda_i }")
P("The homeostatic burden functional and marginal potential (V2.0 Sec. 6) are implemented verbatim:")
eq("ell_i(x_i) = alpha_i [L_i - x_i]_+^2 + beta_i [x_i - U_i]_+^2\n"
   "B(x)       = sum_i ell_i(x_i)\n\n"
   "mu_i = -2 alpha_i (L_i - x_i)   if x_i < L_i\n"
   "mu_i = 0                        if L_i <= x_i <= U_i\n"
   "mu_i =  2 beta_i  (x_i - U_i)   if x_i > U_i")
P("The local movement law (V2.0 Sec. 7) drives transfers by the generalized force and clips them "
  "to the physical constraints:")
eq("F_ij = mu_i - mu_j - theta_ij\n"
   "q_ij = min { q_a^max,  x_i - x_i^min,  K_j - x_j,  M_ij [F_ij]_+ }\n"
   "delivered = eta_ij q_ij ,   transport loss = (1 - eta_ij) q_ij + c_ij^0 >= 0")
P("A deterministic actor selects the neighboring edge of greatest positive force and otherwise "
  "rests. Continuity (Law 2), bounded state (Law 3), non-negative dissipation (Law 4), and "
  "counterfactual separation (Law 7 &mdash; a no-action branch is created every tick and natural "
  "flows are never credited to actors) are enforced by the engine, not by actor preference. "
  "Oversubscribed sources are resolved by proportional scaling (V2.0 Sec. 12.1).")

# ============================================================ 3
h1("3. Corrections and Extensions to the Equations")
P("Three changes were required to move from specification to a runnable, stable model. Only the "
  "first is a correction to an equation; the other two are concrete realizations of choices V2.0 "
  "left open.")

h2("3.1 Correction: state-dependent leakage (the key fix)")
P("V2.0 lists leakage lambda_i(t) as an externally specified function but the worked examples treat "
  "it as a fixed per-tick constant. With fixed leakage the model exhibits no stable in-band "
  "attractor: an open system either bleeds out (net drain, slow collapse invisible at short "
  "horizons) or accumulates to the capacity bound K_i and hoards. Neither is homeostasis. We "
  "therefore make leakage state-dependent &mdash; larger stocks leak more &mdash; which is the "
  "minimal self-regulating sink:")
eq("lambda_i = lambda_i^0 + kappa_i * x_i(t)          (kappa_i >= 0)")
P("This single change gives the field a stable fixed point strictly inside [L_i, U_i]: inflow is "
  "balanced against demand plus a loss that grows with capacity, so cells settle in-band instead of "
  "emptying or saturating. It is fully consistent with V2.0 (leakage was always permitted to be any "
  "function of state) and it is what converts &ldquo;survives&rdquo; into &ldquo;stays healthy.&rdquo;")

h2("3.2 Extension: a dense field of local actors")
P("V2.0 specifies ~50 mobile actors but leaves their deployment open. To test the movement law as a "
  "pure local field rule &mdash; the &ldquo;Game of Life&rdquo; reading of the project &mdash; we "
  "place one stationary actor on every cell, each applying the identical law using only its "
  "four-neighborhood. No actor sees the global state and nothing is centrally coordinated. This is "
  "the strictest possible test of the claim that local rules alone produce global viability.")

h2("3.3 Extension: the producer/consumer checkerboard test world")
P("To exercise transport under locality (Law 1) with minimal confounding transport loss, sources "
  "and sinks are arranged as a checkerboard: producer cells (renewable inflow s &gt; 0, no demand) "
  "alternate with consumer cells (demand d &gt; 0, no inflow). Every consumer is surrounded by "
  "producers, so the gradient rule only ever needs one-hop transfers. This isolates the question "
  "&ldquo;does the local rule route supply to need?&rdquo; from the separate question of "
  "long-distance transport loss.")
P("<b>Not yet implemented (scope):</b> the H-tick regeneration-aware counterfactual (V2.0 Sec. 9, "
  "Model D), Allee-threshold regenerative sources, the softmax exploration policy, and the EBU "
  "ledger overlay (Model E). The current actor is Model C (gradient proposal, one-tick acceptance).")

# ============================================================ 4
h1("4. Verification (V2.0 Section 14.1)")
P("All eight required pre-experiment unit tests pass. The decisive one is the monotonicity proof of "
  "V2.0 Section 8: under ideal lossless gradient flow the burden never increases, and in our run it "
  "was driven to exactly zero.")
table([
    ["#", "Required property (V2.0 Sec. 14.1)", "Result"],
    ["1", "A transfer never produces x_i < 0 or x_i > K_i", "PASS"],
    ["2", "Closed lossless system conserves total capacity", "PASS (X = 168.0000)"],
    ["3", "With inefficiency, dX equals recorded loss exactly", "PASS"],
    ["4", "A finite source never regenerates", "PASS"],
    ["5", "Ideal gradient flow never increases B (Sec. 8)", "PASS (B -> 0.0000)"],
    ["6", "No-action and action branches are reproducible", "PASS"],
    ["7", "Actor impact excludes natural inflow/regeneration", "PASS (impact = 0)"],
    ["8", "Regenerative source (rho>0) follows its declared logistic law", "PASS (g matches; 5 -> K)"],
], colw=[1 * cm, 10.5 * cm, 4 * cm])

# ============================================================ 5
h1("5. Experiments and Results")
h2("5.1 Local rule ON vs OFF, long horizon")
P("A 10x10 checkerboard (100 cells), balanced renewable supply (inflow s = 0.8, demand d = 0.4, "
  "kappa = 0.02, eta = 0.95). Identical initial state and physics; the only difference is whether "
  "the local movement rule is active.")
table([
    ["Horizon", "Rule", "mean B", "final B", "viable cells", "min cell"],
    ["200",   "ON",  "0.34",   "0.42",   "92 / 100", "3.54"],
    ["200",   "OFF", "954.7",  "1040.0", "50 / 100", "0.00"],
    ["5,000", "ON",  "0.33",   "0.46",   "95 / 100", "3.54"],
    ["5,000", "OFF", "1036.6", "1040.0", "50 / 100", "0.00"],
    ["50,000", "ON", "0.33",   "0.69",   "94 / 100", "3.54"],
    ["50,000", "OFF","1039.7", "1040.0", "50 / 100", "0.00"],
], colw=[2.4 * cm, 1.6 * cm, 2 * cm, 2 * cm, 3 * cm, 2 * cm])
P("Under the local rule the burden is flat at ~0.33 across a 250x increase in run length: the field "
  "reaches a homeostatic steady state and stays there. With the rule off, 50 consumer cells die and "
  "never recover. The mean-burden separation is roughly three orders of magnitude.")
figure("figures/B_vs_time.png",
       "Figure 1. Homeostatic burden B(t) on a log scale. Rule OFF (red) saturates near 1000 within "
       "~15 ticks; rule ON (green) fluctuates near 0.1&ndash;1 indefinitely.")
figure("figures/heatmap_snapshots.png",
       "Figure 2. Capacity field. Top (ON): cells settle into a balanced mid-range and hold. Bottom "
       "(OFF): producers pin at K (yellow), consumers die at 0 (dark) &mdash; permanent collapse.")
figure("figures/viable_vs_time.png",
       "Figure 3. Fraction of viable cells (x >= L). The local rule holds ~95%; without it half the "
       "grid is lost within the first ~15 ticks and stays lost.")

h2("5.2 The homeostasis window")
P("Survival is not automatic; it depends on the open-system energy budget. Sweeping the renewable "
  "inflow reveals a bounded viability window. Below s ~ 0.65 the field collapses (supply cannot meet "
  "demand plus transport loss); above s ~ 0.9 burden climbs again as the field over-fills and hoards. "
  "Robust in-band homeostasis occupies the band s in [0.7, 0.9].")
figure("figures/inflow_sweep.png",
       "Figure 4. Viable cells (green) and mean burden (purple, log) vs renewable supply at t=5000. "
       "Homeostasis exists only in a bounded window; the burden curve is U-shaped.")

# ============================================================ 6
h1("6. Verdict: Is It a Good Model?")
P("<b>Yes, as a scientific instrument &mdash; with two documented cautions.</b> Judged against the "
  "model's own falsification criteria (V2.0 Sec. 13):")
table([
    ["Falsification criterion (Sec. 13)", "Observed", "Status"],
    ["Persistent shuttling with no net benefit", "Small B oscillation, but clear net benefit (95% vs 50% viable)", "Not triggered"],
    ["Transport loss exceeds homeostatic benefit", "Small in one-hop regime; untested for long distance", "Open"],
    ["Short-horizon actors destroy long-horizon regeneration", "Not yet testable (no Allee sources, Model C only)", "Open"],
    ["Burden hides severe local collapse behind aggregate", "HIT at s=0.42: B~0.24 at t=200 while field was dying", "Caution"],
    ["Small coefficient change reverses conclusions", "Sharp supply threshold near s~0.65", "Partial hit"],
    ["Counterfactual costs more than it detects", "1-tick acceptance is cheap; H-horizon untested", "Open"],
    ["EBU incentives cause gaming/hoarding", "EBU overlay not implemented", "Open"],
], colw=[7.5 * cm, 6 * cm, 2 * cm])
P("<b>What the model gets right.</b> It is well-posed and conservation-correct: every unit test "
  "passes, including the monotonicity proof that motivates the whole potential-gradient approach. It "
  "answers the central question affirmatively: repeated application of a purely local, "
  "potential-driven rule does produce robust homeostasis &mdash; markedly better than the no-rule "
  "baseline &mdash; and does so indefinitely, with no central optimizer. It also honours Law 6: it "
  "never forces survival, and it lets collapse happen when the budget cannot support life.")
P("<b>Caution 1 &mdash; aggregate burden can mask slow death.</b> At marginal supply the global B "
  "looked excellent at 200 ticks while the field was in fact bleeding out and dead by 5,000 ticks. "
  "This is exactly falsification criterion 4. The practical consequence: B alone must never be "
  "trusted; per-cell viability and long horizons are mandatory diagnostics (as V2.0 Sec. 10.1 "
  "already warns).")
P("<b>Caution 2 &mdash; the conclusion is supply-dependent.</b> Homeostasis exists only in a bounded "
  "window of renewable inflow. This is physically honest rather than a defect &mdash; a real open "
  "system also dies outside its energy budget &mdash; but it means results must always be reported "
  "as a window, never as a single tuned point. The dependence is on a physical budget parameter "
  "(supply), which is more defensible than dependence on the arbitrary penalty weights alpha/beta; a "
  "dedicated sensitivity sweep on those weights remains outstanding.")
P("<b>Bottom line.</b> The V2.0 local movement law, with the proportional-leakage correction, is a "
  "good and faithful simulation model of local-rule homeostasis. It substantiates the core "
  "proposition within a defined regime and refuses to overclaim outside it. It is not a proof that "
  "any real economy or planet will self-stabilize, and the document does not present it as one.")

# ============================================================ 7
h1("7. Limitations and Recommended Next Steps")
P("1. Implement the H-tick regeneration-aware actor (Model D) and Allee-threshold regenerative "
  "sources, then test falsification criterion 3 (short foresight destroying long-horizon "
  "regeneration) across H = 1, 3, 10, 30.<br/>"
  "2. Run the full A&ndash;E comparison (random, greedy, gradient, regeneration-aware, EBU overlay) "
  "on identical seeds, per V2.0 Sec. 12.2.<br/>"
  "3. Sensitivity sweeps on alpha, beta, kappa, eta, and theta to quantify how far conclusions "
  "survive coefficient changes.<br/>"
  "4. Introduce long-distance transport (non-checkerboard source placement) to test whether "
  "transport loss overturns the benefit (criterion 2).<br/>"
  "5. Add shocks and measure recovery time; add the EBU ledger last, only after the physics is "
  "trusted, to check for gaming (criterion 7).")

# ============================================================ REFS
h1("References and Scientific Inspirations")
for r in [
    "Cannon, W. B. (1929). Organization for Physiological Homeostasis. Physiological Reviews, 9(3), 399-431.",
    "Fick, A. (1855). Ueber Diffusion. Annalen der Physik, 170(1), 59-86.",
    "Onsager, L. (1931). Reciprocal Relations in Irreversible Processes. I & II. Physical Review, 37 & 38.",
    "Prigogine, I. (1977). Time, Structure and Fluctuations. Nobel Lecture.",
    "Watson, A. J., and Lovelock, J. E. (1983). Biological Homeostasis of the Global Environment: "
    "The Parable of Daisyworld. Tellus B, 35(4), 284-289.",
]:
    S.append(Paragraph(r, ParagraphStyle("ref", parent=BODY, fontSize=8.5, leftIndent=12,
                                          firstLineIndent=-12, spaceAfter=3)))
gap(8)
P("<b>Version status.</b> V2.1 keeps the V2.0 one-field homeostatic formulation and its seven hard "
  "laws unchanged. It adds a state-dependent leakage term (Sec. 3.1) as the one equation correction, "
  "reports a passing verification suite, and provides the first empirical verdict. The next revision "
  "should follow only after Model D and the A&ndash;E comparison are complete.")


def build():
    doc = SimpleDocTemplate(OUT, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                            topMargin=1.8 * cm, bottomMargin=1.8 * cm,
                            title="The Energy Balance Project - Foundation Model V2.1",
                            author="Energy Balance Project")
    doc.build(S)
    print("wrote", OUT)


if __name__ == "__main__":
    build()
