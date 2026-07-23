"""
Generate the V2.3 research paper PDF (supersedes v2.2):
  Energy_Balance_Project_Foundation_v2.3.pdf
All numbers come from audit_v231.py, exp_v23.py, and test_v23.py.
Run with the project venv:  .../venv/bin/python make_paper_v23.py
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Preformatted, Image, Table, TableStyle,
    PageBreak, HRFlowable)
from PIL import Image as PILImage

OUT = "Energy_Balance_Project_Foundation_v2.3.pdf"
styles = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=styles["Heading1"], fontSize=15, spaceBefore=14, spaceAfter=6,
                    textColor=colors.HexColor("#1F3A5F"))
H2 = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=12, spaceBefore=10, spaceAfter=4,
                    textColor=colors.HexColor("#2C5580"))
BODY = ParagraphStyle("BODY", parent=styles["BodyText"], fontSize=10, leading=14,
                      alignment=TA_JUSTIFY, spaceAfter=6)
TITLE = ParagraphStyle("TITLE", parent=styles["Title"], fontSize=22, textColor=colors.HexColor("#1F3A5F"))
SUB = ParagraphStyle("SUB", parent=styles["Italic"], fontSize=11, alignment=TA_CENTER,
                     textColor=colors.HexColor("#2C5580"))
EQ = ParagraphStyle("EQ", fontName="Courier", fontSize=9, leading=12,
                    backColor=colors.HexColor("#F0F3F7"), borderColor=colors.HexColor("#D5DEE8"),
                    borderWidth=0.5, borderPadding=6, leftIndent=8, rightIndent=8,
                    spaceBefore=4, spaceAfter=8)
CAP = ParagraphStyle("CAP", parent=BODY, fontSize=8.5, alignment=TA_CENTER,
                     textColor=colors.HexColor("#555555"), spaceBefore=2, spaceAfter=12)
CELL = ParagraphStyle("CELL", parent=BODY, fontSize=8.5, leading=10.5, spaceAfter=0, alignment=TA_LEFT)
CELLH = ParagraphStyle("CELLH", parent=CELL, textColor=colors.white, fontName="Helvetica-Bold")

S = []
def P(t):  S.append(Paragraph(t, BODY))
def h1(t): S.append(Paragraph(t, H1))
def h2(t): S.append(Paragraph(t, H2))
def eq(t): S.append(Preformatted(t, EQ))
def gap(h=6): S.append(Spacer(1, h))
def figure(path, cap, width=15 * cm):
    im = PILImage.open(path); w, h = im.size
    S.append(Image(path, width=width, height=width * h / w)); S.append(Paragraph(cap, CAP))
def table(data, colw):
    wrapped = [[Paragraph(str(c), CELLH if ri == 0 else CELL) for c in row]
               for ri, row in enumerate(data)]
    t = Table(wrapped, colWidths=colw)
    t.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#C8D2DC")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F3A5F"))]))
    S.append(t); gap(10)


# ============================================================ TITLE
S.append(Spacer(1, 3 * cm))
S.append(Paragraph("The Energy Balance Project", TITLE)); gap(6)
S.append(Paragraph("Homeostatic Field Model and Local Actor-Motion Law", SUB))
S.append(Paragraph("Foundation Document &mdash; Version 2.3 (Audit of Foresight and Regeneration)", SUB))
gap(18); S.append(HRFlowable(width="60%", color=colors.HexColor("#1F3A5F"), thickness=1)); gap(18)
P("<b>Status:</b> two controlled stages completed. Stage 1 (V2.2.1 audit) isolates the cause of the "
  "V2.2 clustered-world failure. Stage 2 (V2.3) adds regeneration and tests whether immediate "
  "homeostatic improvement destroys future regenerative capacity. All claims are backed by scripts "
  "and by a 19-test suite.")
gap(8)
P("<b>Two headline results, both counter to the naive expectation.</b> (1) The clustered failure is "
  "driven mainly by <b>myopia, not dissipation</b>: lossless transport (eta=1) lifts clustered "
  "viability only 51&rarr;57%, while adding foresight (H=10) lifts it 54&rarr;80%. (2) In a closed "
  "regenerative (Allee) economy, a longer foresight horizon of the specified single-action form does "
  "<b>not</b> protect regeneration &mdash; it <b>destroys</b> it. Myopic rules keep every source "
  "alive through a shock; naive H=10 drives all 32 sources below their Allee threshold to "
  "irreversible collapse. The cause is a systematic bias in the single-action counterfactual.")
S.append(PageBreak())

# ============================================================ ABSTRACT
h1("Abstract")
P("V2.2 left one open question (why clustered sources fail) and one overclaim (“strict "
  "dominance”), both corrected here. We first audit the clustered failure by separating three "
  "possible causes &mdash; layout variance, transport dissipation, and short-horizon myopia &mdash; "
  "and find myopia dominant. We then add the four V2.0 source behaviours (external flow, logistic "
  "stock, Allee stock, finite stock) and pose the project's central question in a closed economy "
  "whose only supply is regeneration. Contrary to expectation, the regeneration-aware actor of V2.0 "
  "Section 9 (a longer local counterfactual) is biased toward over-harvest: because it evaluates a "
  "single action in isolation, longer horizons credit a harvest more (the source appears to "
  "regenerate freely and the fed cell appears permanently rescued), so it over-harvests and drives "
  "Allee sources below their recovery threshold after a disturbance. Short-horizon rules are "
  "accidentally protective. This empirically validates the V2.0 design note (Sec. 7.2) that a "
  "critical regeneration threshold belongs in the burden and regeneration dynamics, not in a longer "
  "isolated lookahead.")

# ============================================================ 1
h1("1. Corrections carried from V2.2")
P("Before new work, the V2.2 claims were corrected: “strictly dominates” became "
  "“lower burden and unmet demand overall, but not a strict Pareto improvement” (clustered "
  "viability is tied, 51.0% vs 51.6%, and the safe rule uses slightly more transport on the "
  "checkerboard); “scale-invariant” became “approximately size-insensitive across the "
  "three sizes tested”; the falsification table was reflowed to remove overlapping text; and "
  "the clustered failure was left attributed to “locality, delay, and dissipation” pending "
  "this audit.")

# ============================================================ 2
h1("2. Stage 1 &mdash; Audit of the Clustered Failure (V2.2.1)")
P("Using the same engine and the same three worlds, only the decision rule changes. Three questions, "
  "each isolating one factor.")
h2("2.1 Is the failure robust across layouts?")
P("Over 30 seeds on the random world, the safe rule beats the gradient rule robustly (85.6% "
  "&plusmn;10.1 vs 71.7% &plusmn;8.2 viable). The clustered numbers below have zero variance because "
  "the current builder places the producer block deterministically; the 30 clustered “seeds” "
  "are therefore identical. The clustered conclusion rests on one layout plus the sweeps in 2.2&ndash;2.3, "
  "not on 30 distinct layouts &mdash; a limitation fixed in future work by randomising the cluster.")
table([
    ["World", "Model", "viable % (mean ± sd over 30 seeds)"],
    ["random", "gradient", "71.7 ± 8.2"],
    ["random", "safe", "85.6 ± 10.1"],
    ["clustered", "gradient", "51.6 ± 0.0 (deterministic layout)"],
    ["clustered", "safe", "51.1 ± 0.0 (deterministic layout)"],
], colw=[3 * cm, 3 * cm, 9.5 * cm])
h2("2.2 Is it transport dissipation? (vary eta)")
P("On the clustered world, making transport more efficient barely helps. Even perfectly lossless "
  "transport recovers only a few points of viability:")
table([
    ["transport efficiency eta", "0.90", "0.95", "0.98", "1.00"],
    ["clustered viable %", "47.1", "51.1", "54.7", "57.3"],
], colw=[5.5 * cm, 2.5 * cm, 2.5 * cm, 2.5 * cm, 2.5 * cm])
h2("2.3 Is it myopia? (vary horizon H)")
P("Adding foresight helps a great deal. Moving from a one-tick to a ten-tick local counterfactual "
  "lifts clustered viability from 54% to 80% (a wider evaluation radius adds nothing beyond H, so "
  "horizon length, not radius, is the active variable):")
table([
    ["foresight horizon H", "1", "3", "10", "30", "10 (radius 4)"],
    ["clustered viable %", "54.0", "62.2", "80.1", "78.2", "80.1"],
], colw=[5.5 * cm, 2 * cm, 2 * cm, 2 * cm, 2 * cm, 3 * cm])
figure("figures/audit.png",
       "Figure 1. Isolating the clustered failure. Lossless transport (left) barely helps; foresight "
       "(right) helps substantially. The failure is chiefly myopia: the one-tick safe rule will not "
       "move capacity through neutral intermediate cells toward a distant deficit.")
P("<b>Stage 1 conclusion.</b> The V2.2 clustered failure was principally short-horizon myopia, not "
  "transport loss. This corrects the V2.2 wording, which had left dissipation as a candidate cause.")

# ============================================================ 3
h1("3. Stage 2 &mdash; Regeneration (V2.3)")
h2("3.1 Four source behaviours")
P("The four V2.0 source classes are expressed through existing parameters (s, rho) plus an Allee "
  "threshold A_i, with the natural-update ledger extended to accept signed regeneration:")
eq("external flow :  s_i > 0,  rho_i = 0\n"
   "logistic stock:  g_i(x) = rho_i x (1 - x/K_i)                 (A_i = 0)\n"
   "Allee stock   :  g_i(x) = rho_i x (1 - x/K_i) (x/A_i - 1)      (A_i > 0)\n"
   "finite stock  :  g_i(x) = 0\n\n"
   "Allee note: g_i(x) < 0 for 0 < x < A_i  (a source declining below its threshold)")
h2("3.2 The Allee trap and the central question")
P("A closed economy (no external inflow) on an 8x8 checkerboard: producer cells are Allee stocks, "
  "consumer cells have demand. The only supply is regeneration. Crucially A = 8 while the viable "
  "floor L = 4, so a source can sit inside the viable band (x &gt;= L) yet below its regeneration "
  "threshold (x &lt; A) and be dying. The question:")
eq("Does immediate homeostatic improvement destroy future regenerative capacity?")
P("We compare the raw gradient, the safe H=1 rule, and the regeneration-aware Model D at H = 3, 10, "
  "30. A shock at tick 500 knocks every source down by 55%, landing them just above A, to test which "
  "rule lets them recover.")
h2("3.3 Result: longer naive foresight destroys regeneration")
table([
    ["Model", "viable % (end)", "viable % (2nd half)", "source stock", "dead sources", "cum. unmet", "disc. burden"],
    ["gradient", "100.0", "100.0", "585.8", "0 / 32", "0", "65,881"],
    ["safe (H=1)", "100.0", "100.0", "587.1", "0 / 32", "0", "65,352"],
    ["horizon H=3", "100.0", "100.0", "584.7", "0 / 32", "0", "63,539"],
    ["horizon H=10", "0.0", "19.2", "0.0", "32 / 32", "6,658", "224,105"],
    ["horizon H=30", "37.5", "48.8", "132.8", "24 / 32", "4,557", "165,333"],
], colw=[2.6 * cm, 1.9 * cm, 2.2 * cm, 1.9 * cm, 1.8 * cm, 1.7 * cm, 1.9 * cm])
figure("figures/v23_src_stock.png",
       "Figure 2. Remaining regenerative stock. All rules coexist while sources are healthy. After "
       "the shock, myopic rules (gradient/safe/H=3) let sources recover above the Allee threshold; "
       "naive H=10 keeps harvesting and drives them to zero (irreversible), H=30 bleeds out slowly.")
figure("figures/v23_viable.png",
       "Figure 3. Viable-cell fraction. Short-horizon rules hold 100% through the shock; long-horizon "
       "rules collapse during recovery.")
h2("3.4 Mechanism: the single-action counterfactual over-credits harvest")
P("The reversal is not a bug. The Section 9 counterfactual evaluates one action in isolation, "
  "assuming no other actions before or after. In a closed economy every actor harvests every tick, "
  "so this assumption is violated in two directions: the no-action branch over-states the fed "
  "cell's future deficit (it will in fact be re-supplied next tick), and the action branch lets the "
  "harvested source regenerate freely (it will in fact be re-harvested). Both biases grow with the "
  "horizon. A controlled single-harvest measurement shows the predicted impact rising steeply with "
  "H, so longer horizons accept ever-more-aggressive harvesting:")
table([
    ["horizon H", "1", "3", "10", "30"],
    ["predicted impact of one harvest", "0.00", "+0.14", "+34.2", "+104.8"],
], colw=[5.5 * cm, 2.5 * cm, 2.5 * cm, 2.5 * cm, 2.5 * cm])
P("Near the Allee threshold this is fatal: after the shock, sources sit just above A; the myopic "
  "rules harvest gently (harvesting a low source carries high immediate burden, so they back off) "
  "and the sources climb back above A, whereas the long-horizon rule harvests hard and pushes them "
  "below A into irreversible decline. Short-horizon caution is here an accidental but effective form "
  "of regeneration protection.")

# ============================================================ 4
h1("4. Verdict")
P("<b>The engine is correct</b> (ledger balances every tick, now including signed Allee "
  "regeneration; 19 tests pass across three suites). <b>The two stages answer the questions posed "
  "and both overturn the naive intuition.</b>")
P("<b>On foresight.</b> Foresight is not uniformly good or bad. For pure transport/routing "
  "(clustered sources, no regeneration) a longer horizon helps: it lets capacity move through "
  "neutral cells toward distant deficits. For managing a regenerating resource, a longer horizon of "
  "the single-action form is harmful: it systematically over-credits harvest and destroys the "
  "resource after a disturbance.")
P("<b>On the central question.</b> In this experiment immediate homeostatic improvement did NOT "
  "destroy future regenerative capacity &mdash; the naive long-horizon rule did. The correct reading "
  "is not “add foresight” but the V2.0 design note (Sec. 7.2): a critical regeneration "
  "threshold should be represented in the burden and regeneration dynamics (e.g. a penalty as x "
  "approaches A, or a sustainable-yield constraint), not delegated to a longer isolated counterfactual. "
  "The experiment is the evidence for that design choice.")
P("<b>Falsification criteria touched (V2.0 Sec. 13).</b> “Short-horizon actors destroy "
  "long-horizon regeneration” was tested and, for the myopic rules, NOT triggered; the naive "
  "long-horizon rule triggered its mirror image. “Counterfactual costs more than it detects” "
  "is now concrete: the H-horizon evaluation is both expensive and, here, actively misleading.")

# ============================================================ 5
h1("5. Limitations and Next Steps")
P("1. <b>Threshold-aware burden.</b> Add a penalty (or regeneration-reserve constraint) as x "
  "approaches A_i and re-run Stage 2; expected to give sustainable harvest without a long "
  "counterfactual. This is the priority.<br/>"
  "2. <b>Fix the clustered layout.</b> Randomise cluster position/shape so the audit's variance "
  "claim rests on genuinely distinct layouts.<br/>"
  "3. <b>Better counterfactual.</b> If a lookahead is kept, model repeated/aggregate actions (or a "
  "mean-field of other actors) so it stops assuming a single isolated harvest.<br/>"
  "4. <b>Then EBU.</b> Only once a threshold-aware rule sustains regeneration should the EBU ledger "
  "be added, and tested for gaming.")
gap(6)
P("<b>Version status.</b> V2.3 keeps the V2.0 laws, the V2.1 state-dependent leakage, and the V2.2 "
  "ledger and safe rule. It adds the four source behaviours and the H-horizon actor, and reports the "
  "audit and the regeneration experiment. The naive Model D is shown insufficient; the next revision "
  "should implement a threshold-aware burden before any further scaling.")


def build():
    SimpleDocTemplate(OUT, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                      topMargin=1.8 * cm, bottomMargin=1.8 * cm,
                      title="The Energy Balance Project - Foundation Model V2.3",
                      author="Energy Balance Project").build(S)
    print("wrote", OUT)


if __name__ == "__main__":
    build()
