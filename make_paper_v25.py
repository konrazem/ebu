"""
Generate the V2.5 research paper PDF:
  Energy_Balance_Project_Foundation_v2.5.pdf
Numbers from exp_v25.py and test_v25.py.
Run with the project venv:  .../venv/bin/python make_paper_v25.py
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Preformatted, Image,
                                Table, TableStyle, PageBreak, HRFlowable)
from PIL import Image as PILImage

OUT = "Energy_Balance_Project_Foundation_v2.5.pdf"
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
S.append(Paragraph("Foundation Document &mdash; Version 2.5 (EBU Accounting: Naive vs Guarded under Adversaries)", SUB))
gap(18); S.append(HRFlowable(width="60%", color=colors.HexColor("#1F3A5F"), thickness=1)); gap(18)
P("<b>Status:</b> an EBU accounting/incentive layer added on top of the frozen V2.4 threshold-aware "
  "physics (baseline tag <font face=\"Courier\">v2.4.0</font>). The physics equations are unchanged. "
  "Backed by 9 new ledger-property tests (33 tests total) run before any experiment.")
gap(8)
P("<b>Headline (falsifiable) result.</b> A naive EBU ledger is exploitable in specific, enumerated "
  "ways: adversaries maximising their naive balance destroy the system entirely (0% viable, 32/32 "
  "sources dead) while being paid a huge amount of credit (~730,000). A guarded ledger &mdash; "
  "live-state causal credit against the threshold-aware burden, issued sequentially, with symmetric "
  "burden-increase debits and explicit debits for transport loss and irreversible extraction &mdash; "
  "closes or bounds every tested attack and keeps adversaries at 100% viability: maximising guarded "
  "EBU coincides with doing real homeostatic work. Residual, non-exploitable credit is characterised.")
S.append(PageBreak())

# ---- 1 ----
h1("1. Architecture")
P("The EBU layer may observe actions and their verified consequences, maintain per-actor accounts, "
  "and influence selection among physically admissible actions. It must NOT change regeneration, "
  "transport, demand, or conservation. The physics is exactly V2.4's threshold_penalty rule and its "
  "threshold-aware burden B_R. A property test confirms the physical trajectory is byte-identical "
  "whether the ledger is off or guarded (the layer is observational unless it drives selection).")

h1("2. The Guarded Ledger")
P("Credit is the live-state reduction in the threshold-aware burden B_R around each action, issued "
  "SEQUENTIALLY against the running state so natural inflow/regeneration are never credited and two "
  "actors cannot be paid for the same reduction (telescoping). Burden INCREASES are debited "
  "symmetrically; transport dissipation and irreversible extraction below the Allee threshold are "
  "debited explicitly:")
eq("credit_a = max(0,  B_R(before_a) - B_R(after_a))            (issued credit, >= 0)\n"
   "dEBU_a   =        B_R(before_a) - B_R(after_a)  - lambda_L L_a - lambda_F F_a\n"
   "         = credit_a - max(0, -(B_R diff)) - lambda_L L_a - lambda_F F_a\n\n"
   "L_a = (1-eta) q + c0         transport dissipation of the action\n"
   "F_a = increase in (A_i - x_i)_+ at a regenerative source i   (extraction below Allee)")
P("The symmetric burden-increase debit is a deliberate refinement of the plain "
  "C_a = max(0, .) formula: without it, an actor could do good, undo it, and keep the credit. With "
  "it, sum of account changes telescopes to B_R(before all actions) - B_R(after all actions) minus "
  "issued debits, which makes round-trips and damage-then-repair non-positive. The naive ledger, by "
  "contrast, credits apparent improvement in the PLAIN burden against the fixed pre-tick field, with "
  "no debits &mdash; so it credits natural regeneration, double-counts across actors, and is blind "
  "to transport loss and regenerative-reserve sacrifice.")

# ---- 3 ----
h1("3. Tests Before Experiments")
P("All nine guarded-ledger properties hold (part of a 33-test suite):")
table([
    ["Property", "Result"],
    ["No action &rarr; zero credit", "PASS"],
    ["Natural regeneration &rarr; not credited (guarded 1.75 vs naive 13.42)", "PASS"],
    ["Telescoping: issued credit == actual B_R reduction (no double credit)", "PASS"],
    ["Perfect (lossless) round trip returning to start &rarr; net EBU = 0", "PASS"],
    ["Pointless lossy move (in-band) &rarr; strictly negative EBU", "PASS"],
    ["Damage then exact repair &rarr; net EBU <= 0", "PASS"],
    ["Splitting one transfer into many &rarr; no increase in reward", "PASS"],
    ["Sum of account changes == issued credit - issued debit", "PASS"],
    ["Physics trajectory identical when the ledger is observational", "PASS"],
], colw=[13 * cm, 2.5 * cm])

# ---- 4 ----
h1("4. Four Comparisons")
P("Closed Allee economy (8x8, only supply is regeneration), 800 ticks, source shock at tick 400. "
  "The first three share one physics trajectory (EBU observational); the last two let actors choose "
  "actions to maximise their own EBU balance.")
table([
    ["Selection / ledger", "viable %", "dead", "B_R mean", "issued credit", "issued debit", "net EBU"],
    ["physics / none", "100.0", "0/32", "93.6", "0", "0", "0"],
    ["physics / naive (obs)", "100.0", "0/32", "93.6", "1,682", "0", "1,682"],
    ["physics / guarded (obs)", "100.0", "0/32", "93.6", "5,994", "71", "5,922"],
    ["adversarial / naive", "0.0", "32/32", "2,558", "730,913", "0", "730,913"],
    ["adversarial / guarded", "100.0", "0/32", "96.3", "5,513", "80", "5,433"],
], colw=[3.9 * cm, 1.7 * cm, 1.5 * cm, 1.8 * cm, 2.4 * cm, 2.2 * cm, 2 * cm])
P("The naive adversary earns ~730,000 EBU while collapsing every source &mdash; a total decoupling "
  "of reward from health. The guarded adversary cannot do this: maximising the guarded balance drives "
  "genuine homeostatic work, so it keeps 100% viability and earns only bounded, earned credit "
  "(comparable to the observational guarded case). The guarded adversary's positive net EBU (5,433) "
  "is real work, not gaming.")
figure("figures/v25_compare.png",
       "Figure 1. Health (green, left axis) vs net EBU issued (purple, right axis). Only "
       "adversarial/naive decouples them: zero viability with a ~730k EBU spike. Guarded keeps "
       "adversaries healthy; its EBU bars are negligible on this scale.")

# ---- 5 ----
h1("5. Attack Suite")
P("Net EBU an actor earns by executing each known gaming strategy, under each ledger. Guarded makes "
  "every attack non-positive or strictly smaller than naive.")
table([
    ["Attack", "naive EBU", "guarded EBU", "outcome"],
    ["Back-and-forth (round trip)", "4.94", "0.89", "reduced; residual is real net rebalancing (a true return-to-start nets 0)"],
    ["Damage then repair", "0.00", "0.00", "no gain either way (lossless)"],
    ["Split one transfer into four", "+11.36", "-0.06", "closed: splitting pays extra transport, no gain"],
    ["Sacrifice regen (harvest below A)", "0.00", "-38.02", "closed: naive is free, guarded strongly debits"],
    ["Claim natural regeneration", "13.42", "1.75", "closed: guarded credits only the action's live effect"],
    ["Duplicate credit (two actors, one fix)", "16.00", "8.00", "closed: guarded telescopes to the real reduction"],
], colw=[4.2 * cm, 1.8 * cm, 1.9 * cm, 7.2 * cm])
P("Honest characterisation of residuals: the back-and-forth guarded value (0.89) is positive only "
  "because that specific lossy sequence does not return the system to its start &mdash; it performs "
  "a small net rebalancing, which is genuine work; a true return-to-start round trip nets exactly "
  "zero (property test). The sacrifice-regen attack shows the sharpest contrast: naive assigns it "
  "zero cost (plain burden is blind to a source dropping below its Allee threshold while still above "
  "L), so under naive it is a free way to destroy sources; guarded debits it heavily.")

# ---- 6 ----
h1("6. Verdict")
P("<b>The meaningful result is not &lsquo;EBU works&rsquo;.</b> It is that <b>naive EBU is "
  "exploitable in the enumerated ways, while guarded EBU closes those attacks without changing the "
  "physical homeostasis</b> (the physics trajectory is provably identical when the ledger is "
  "observational, and the guarded adversary stays at 100% viability). Maximising the guarded balance "
  "is aligned with system health by construction: credit is the verified live-state burden reduction, "
  "and every way of manufacturing apparent value &mdash; churning, splitting, claiming regeneration, "
  "double-claiming, or sacrificing regenerative stock &mdash; is either uncredited or debited.")
P("<b>What is NOT claimed.</b> The attack set is finite; passing it is not a proof that no exploit "
  "exists. Guarded credit is local (per action, on the two affected cells); collusion, multi-hop "
  "laundering, and slow baseline manipulation across many ticks were not adversarially searched. The "
  "guarded adversary still earns positive EBU for real work &mdash; which is intended, not a leak.")

# ---- 7 ----
h1("7. Limitations and Next Steps")
P("1. Search for exploits automatically (a learning adversary) rather than testing a hand-written "
  "list, and add collusion / multi-actor laundering scenarios.<br/>"
  "2. Characterise the guarded residual formally: bound net EBU by realised, persistent B_R "
  "reduction minus dissipation.<br/>"
  "3. Stress the credit-locality assumption with long-range transport and shared sources.<br/>"
  "4. Only if guarded survives should EBU be allowed to influence physics-relevant parameters; for "
  "now it stays an incentive/selection layer over the fixed V2.4 baseline.")
gap(6)
P("<b>Version status.</b> V2.5 adds an EBU layer over the immutable <font face=\"Courier\">v2.4.0</font> "
  "physics. The physics is unchanged and re-verified. V2.4 result captures are archived under "
  "results/v2.4/ with a manifest. The next revision should add an automated adversary and collusion "
  "tests before trusting the guarded ledger in any deployment sense.")


def build():
    SimpleDocTemplate(OUT, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                      topMargin=1.8 * cm, bottomMargin=1.8 * cm,
                      title="The Energy Balance Project - Foundation Model V2.5",
                      author="Energy Balance Project").build(S)
    print("wrote", OUT)


if __name__ == "__main__":
    build()
