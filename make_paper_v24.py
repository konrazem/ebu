"""
Generate the V2.4 research paper PDF (supersedes v2.3):
  Energy_Balance_Project_Foundation_v2.4.pdf
Numbers from exp_v24.py, exp_v24_clustered.py, test_v24.py.
Run with the project venv:  .../venv/bin/python make_paper_v24.py
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Preformatted, Image,
                                Table, TableStyle, PageBreak, HRFlowable)
from PIL import Image as PILImage

OUT = "Energy_Balance_Project_Foundation_v2.4.pdf"
sty = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=sty["Heading1"], fontSize=15, spaceBefore=14, spaceAfter=6, textColor=colors.HexColor("#1F3A5F"))
H2 = ParagraphStyle("H2", parent=sty["Heading2"], fontSize=12, spaceBefore=10, spaceAfter=4, textColor=colors.HexColor("#2C5580"))
BODY = ParagraphStyle("BODY", parent=sty["BodyText"], fontSize=10, leading=14, alignment=TA_JUSTIFY, spaceAfter=6)
TITLE = ParagraphStyle("TITLE", parent=sty["Title"], fontSize=22, textColor=colors.HexColor("#1F3A5F"))
SUB = ParagraphStyle("SUB", parent=sty["Italic"], fontSize=11, alignment=TA_CENTER, textColor=colors.HexColor("#2C5580"))
EQ = ParagraphStyle("EQ", fontName="Courier", fontSize=9, leading=12, backColor=colors.HexColor("#F0F3F7"),
                    borderColor=colors.HexColor("#D5DEE8"), borderWidth=0.5, borderPadding=6,
                    leftIndent=8, rightIndent=8, spaceBefore=4, spaceAfter=8)
CAP = ParagraphStyle("CAP", parent=BODY, fontSize=8.5, alignment=TA_CENTER, textColor=colors.HexColor("#555555"), spaceBefore=2, spaceAfter=12)
CELL = ParagraphStyle("CELL", parent=BODY, fontSize=8.5, leading=10.5, spaceAfter=0, alignment=TA_LEFT)
CELLH = ParagraphStyle("CELLH", parent=CELL, textColor=colors.white, fontName="Helvetica-Bold")

S = []
def P(t): S.append(Paragraph(t, BODY))
def h1(t): S.append(Paragraph(t, H1))
def h2(t): S.append(Paragraph(t, H2))
def eq(t): S.append(Preformatted(t, EQ))
def gap(h=6): S.append(Spacer(1, h))
def figure(path, cap, width=15 * cm):
    im = PILImage.open(path); w, h = im.size
    S.append(Image(path, width=width, height=width * h / w)); S.append(Paragraph(cap, CAP))
def table(data, colw):
    wr = [[Paragraph(str(c), CELLH if r == 0 else CELL) for c in row] for r, row in enumerate(data)]
    t = Table(wr, colWidths=colw)
    t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#C8D2DC")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3), ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F3A5F"))]))
    S.append(t); gap(10)

# ---- title ----
S.append(Spacer(1, 3 * cm))
S.append(Paragraph("The Energy Balance Project", TITLE)); gap(6)
S.append(Paragraph("Homeostatic Field Model and Local Actor-Motion Law", SUB))
S.append(Paragraph("Foundation Document &mdash; Version 2.4 (Foresight vs Artifact; Protective Harvest Rules)", SUB))
gap(18); S.append(HRFlowable(width="60%", color=colors.HexColor("#1F3A5F"), thickness=1)); gap(18)
P("<b>Status:</b> the V2.3 conclusion is refined by the control it was missing, and three protective "
  "harvest rules are added and compared. Backed by scripts and a 24-test suite.")
gap(8)
P("<b>Central correction.</b> V2.3 reported that long-horizon foresight destroyed a regenerating "
  "resource. That was imprecise: the horizon test there only <i>gated</i> a quantity chosen by the "
  "immediate (H=1) line search. When the quantity is instead chosen to <b>maximise</b> the H-tick "
  "impact (q_H* = argmax_q I^H(q)), harvesting is fully sustainable (0/32 sources lost, 100% of "
  "demand served). So the V2.3 collapse was an <b>artifact of gating an immediately-optimised "
  "quantity</b>, not evidence that foresight is inherently destructive.")
gap(4)
P("<b>Practical finding.</b> A cheap threshold-aware burden term matches the expensive "
  "horizon-optimised rule (both sustainable, demand fully served) at ~1/100th the cost, and causes "
  "zero regeneration-threshold crossings. And on genuinely randomised clustered layouts, foresight "
  "robustly improves routing (+22.3 points over the myopic rule, winning all 20 paired layouts).")
S.append(PageBreak())

# ---- 1 ----
h1("1. The Control V2.3 Lacked")
P("In V2.3 the regeneration-aware actor (Model D) selected the transfer amount with the immediate "
  "burden line search and then used the H-tick counterfactual only to accept or reject it. The "
  "acceptance test passes any q whose predicted impact is positive, including an over-large "
  "immediately-optimal q. The correct, narrower statement of the V2.3 result is therefore:")
eq("A long isolated-action ACCEPTANCE test applied to an immediately-optimised harvest\n"
   "quantity can encourage destructive harvesting.")
P("This does not establish that foresight itself is harmful. To decide that, the quantity must "
  "itself be chosen by the horizon objective.")

# ---- 2 ----
h1("2. Three Protective Rules and the Decisive Control")
h2("2.1 Threshold-aware burden (regenerative reserve)")
P("Give each regenerative source a reserve R_i above its Allee threshold and penalise dropping below "
  "it, preserving the convex piecewise-quadratic structure the line search needs:")
eq("R_i = A_i + delta_i\n"
   "B_regen = B + sum_i chi_i [R_i - x_i]_+^2\n"
   "mu_i^regen adds  -2 chi_i (R_i - x_i)   for x_i < R_i   (a depleted source now 'pulls')")
h2("2.2 Hard-reserve baseline")
P("A blunt but clear baseline: cap harvesting at the surplus above the reserve, and forbid it while "
  "the source is below its Allee threshold.")
eq("q_max^sustainable = max(0, x_i - R_i);   harvesting forbidden while x_i < A_i")
h2("2.3 Horizon-optimised quantity (the control)")
P("Rather than choose q immediately and ask the horizon yes/no, choose q to maximise the horizon "
  "objective directly:")
eq("q_H* = argmax_{0 <= q <= q_physical}  I^H(q)")
P("If this still over-harvests, the single-action counterfactual is fundamentally biased; if it is "
  "sustainable, only the accept/reject architecture was at fault.")

# ---- 3 ----
h1("3. Regeneration Results")
P("Closed Allee economy (8x8, only supply is regeneration, A=8 &gt; L=4), 1000 ticks, a 55% source "
  "shock at tick 500. Success requires preserving sources AND serving demand. We report both FINAL "
  "viability and the mean over the post-shock second half, because the mean alone can hide a late "
  "collapse. Sustained recovery (&ldquo;rec&rdquo;) counts only if viability returns to &gt;=90% of "
  "its pre-shock value AND source stock stays above the reserve for 100 consecutive ticks.")
table([
    ["Rule", "viable % (end)", "viable % (2nd half)", "served %", "dead", "A-cross", "stock", "rec"],
    ["safe (H=1)", "100.0", "100.0", "100.0", "0/32", "1", "587", "1t"],
    ["horizon_gate (V2.3)", "0.0", "42.8", "73.8", "32/32", "60", "0", "none"],
    ["horizon_opt (q_H*)", "100.0", "100.0", "100.0", "0/32", "2", "585", "5t"],
    ["threshold_penalty", "100.0", "100.0", "100.0", "0/32", "0", "587", "1t"],
    ["hard_reserve", "100.0", "100.0", "100.0", "0/32", "1", "587", "1t"],
    ["penalty_horizon", "100.0", "100.0", "100.0", "0/32", "0", "585", "3t"],
], colw=[3.2 * cm, 1.9 * cm, 2.2 * cm, 1.5 * cm, 1.4 * cm, 1.5 * cm, 1.3 * cm, 1.2 * cm])
P("Only horizon_gate fails, and the end/second-half split makes the failure explicit: its "
  "post-shock mean (42.8%) looks survivable, but final viability is 0% and it never sustainably "
  "recovers. The horizon-optimised rule is sustainable, proving foresight is not inherently "
  "destructive. The two burden-based rules (threshold_penalty, penalty_horizon) achieve zero "
  "threshold crossings &mdash; they never even approach the Allee boundary &mdash; and the cheap "
  "threshold_penalty matches the ~100x more expensive horizon_opt (benchmarked at 0.24 s vs 21.7 s "
  "per 200 ticks, ~91x). All sustainable rules serve 100% of demand, so none succeeds by simply "
  "refusing to harvest.")
figure("figures/v24_stock.png",
       "Figure 1. Remaining regenerative stock. After the shock only horizon_gate (orange) collapses; "
       "the horizon-optimised and burden-based rules all recover fully.")
figure("figures/v24_viable.png",
       "Figure 2. Viable-cell fraction. Five of six rules hold ~100%; only the V2.3 gate collapses.")

# ---- 4 ----
h1("4. Randomised Clustered Audit")
P("The V2.3 clustered layout was deterministic. Here every seed draws a distinct world (random "
  "cluster count, centre, radius, density) and every model runs on the identical world for that "
  "seed (paired). Producers are external-flow sources, so the regeneration rules do not apply; we "
  "compare transport rules.")
table([
    ["Rule", "viable % (mean ± sd)", "min", "max", "seeds"],
    ["none", "22.0 ± 11.1", "9.4", "54.7", "20"],
    ["gradient", "35.4 ± 12.8", "12.1", "64.0", "20"],
    ["safe (H=1)", "35.5 ± 13.5", "14.3", "63.2", "20"],
    ["horizon_gate (H=10)", "57.9 ± 11.4", "34.9", "85.2", "20"],
    ["horizon_opt (H=10)", "58.8 ± 14.5", "44.0", "86.3", "6"],
], colw=[3.6 * cm, 4 * cm, 1.7 * cm, 1.7 * cm, 1.7 * cm])
P("The Stage-1 (V2.2.1) finding survives layout randomisation: foresight substantially improves "
  "clustered routing. In the paired comparison, horizon_gate beats the myopic safe rule by +22.3 "
  "points on average and wins all 20/20 layouts. (horizon_opt was run on 6 seeds for cost.)")
figure("figures/v24_clustered.png",
       "Figure 3. Distribution of clustered viability across 20 randomised paired layouts. Foresight "
       "(horizon_gate / horizon_opt) clearly shifts the distribution upward.")

# ---- 5 ----
h1("5. Verdict")
P("<b>Foresight is not the villain; the accept/reject architecture was.</b> The precise lesson of "
  "V2.3&ndash;V2.4 is that pairing a long isolated-action acceptance test with an "
  "immediately-optimised quantity encourages over-harvest, but the same horizon objective used to "
  "CHOOSE the quantity harvests sustainably. Foresight helps for transport routing (clustered) and, "
  "correctly formulated, does no harm for resource management.")
P("<b>The recommended rule is the threshold-aware burden.</b> It preserves sources and serves all "
  "demand, produces zero Allee-threshold crossings, keeps the convex structure the line search needs, "
  "and costs ~100x less than the horizon-optimised search. This is exactly the V2.0 Sec. 7.2 design "
  "note &mdash; a critical regeneration threshold belongs in the burden and regeneration dynamics "
  "&mdash; now demonstrated rather than assumed. The hard-reserve baseline is equally safe but less "
  "flexible; the horizon rules are best reserved for transport routing, where their extra cost buys "
  "real benefit.")
P("<b>Success was defined as preserving sources AND serving demand,</b> so a do-nothing rule that "
  "hoards sources while starving consumers would not have counted; every sustainable rule here serves "
  "100% of demand.")

# ---- 6 ----
h1("6. Limitations and Next Steps")
P("1. The single-action counterfactual still assumes one isolated action; horizon_opt succeeds here "
  "because the objective, maximised over q, avoids pushing the source below threshold, but in "
  "adversarial or strategic settings a mean-field or repeated-action model may be needed.<br/>"
  "2. horizon_opt used a coarse grid + one refinement; a finer optimiser might shift its numbers "
  "slightly (not its qualitative sustainability).<br/>"
  "3. Clustered horizon_opt was only 6 seeds for cost; extend for tighter intervals.<br/>"
  "4. With a trusted threshold-aware rule in hand, the EBU accounting overlay can finally be added "
  "and tested for gaming, hoarding, and repeated credit.")
gap(6)
P("<b>Reproducibility.</b> Pure-stdlib core: energy_balance.py (+ tests). Engines: ebu_v22.py, "
  "ebu_v23.py, ebu_v24.py. Experiments: ecosystem.py, experiments_v22.py, audit_v231.py, exp_v23.py, "
  "exp_v24.py, exp_v24_clustered.py. Tests (24 total): test_energy_balance.py (8), test_v22.py (7), "
  "test_v23.py (4), test_v24.py (5). Figures and PDFs are regenerated by the make_paper_*.py scripts. "
  "The figure/PDF scripts require matplotlib + reportlab; the core and its physics tests need only "
  "the standard library.")


def build():
    SimpleDocTemplate(OUT, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                      topMargin=1.8 * cm, bottomMargin=1.8 * cm,
                      title="The Energy Balance Project - Foundation Model V2.4",
                      author="Energy Balance Project").build(S)
    print("wrote", OUT)


if __name__ == "__main__":
    build()
