"""
Generate the V2.6 research paper PDF:
  Energy_Balance_Project_Foundation_v2.6.pdf
Every number traces to results/v2.6/v26_experiments.txt and test_v26.py.
Run with the project venv:  .../venv/bin/python make_paper_v26.py
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Preformatted, Image,
                                Table, TableStyle, PageBreak, HRFlowable)
from PIL import Image as PILImage

OUT = "Energy_Balance_Project_Foundation_v2.6.pdf"
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
TAG = ParagraphStyle("TAG", parent=BODY, fontSize=9, leftIndent=6, textColor=colors.HexColor("#444444"))

S = []
def P(t): S.append(Paragraph(t, BODY))
def h1(t): S.append(Paragraph(t, H1))
def h2(t): S.append(Paragraph(t, H2))
def eq(t): S.append(Preformatted(t, EQ))
def tag(t): S.append(Paragraph(t, TAG))
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
S.append(Paragraph("Foundation Document &mdash; Version 2.6 (Automated Adversarial Testing of the Guarded EBU Ledger)", SUB))
gap(18); S.append(HRFlowable(width="60%", color=colors.HexColor("#1F3A5F"), thickness=1)); gap(18)
P("<b>This is an adversarial-search study, NOT an economy.</b> No prices, ownership, or "
  "transferable EBU are introduced. It is a falsification stage over the frozen "
  "<font face=\"Courier\">v2.4.0</font> physics and V2.5 guarded ledger, asking one question:")
gap(4)
P("<b>Can an automated actor or coalition find action sequences that earn positive cumulative "
  "guarded EBU while causing persistent physical harm?</b>")
gap(8)
P("<b>Result.</b> Within the declared search space and budget, <b>no profitable persistent-harm "
  "exploit against the guarded ledger was found</b>. The search is strong enough to judge this: on "
  "the same fixture it <b>rediscovers a naive-ledger exploit</b> (positive control). A separate, "
  "honest caveat: the myopic <i>greedy</i> guarded adversary left the field worse than doing nothing "
  "on 4 of 12 random layouts &mdash; a candidate-exploit signal (persistence unverified) that the "
  "next stage should red-team directly.")
S.append(PageBreak())

# ---- 1 ----
h1("1. Objective and Non-Goals")
P("V2.5 showed a hand-written attack list could not game the guarded ledger. A finite hand list is "
  "weak evidence. V2.6 replaces it with an automated, deterministic search. No economic features are "
  "added; the frozen files (energy_balance, ebu_v22..v25) are unchanged and re-verified. All V2.6 "
  "code lives in new files so earlier results stay reproducible.")

h1("2. Method")
h2("2.1 Forced-action harness (reuses the frozen accounting)")
P("A tick harness applies an arbitrary list of feasibility-clipped actor actions through the exact "
  "V2.5 accounting (the same _action_effect), so guarded/naive semantics are identical to V2.5 and "
  "the physical trajectory under physics selection is byte-identical to the frozen baseline (tested). "
  "Every tick also checks the conservation identity dX = S + G - D - Lambda - loss - spill.")
h2("2.2 Deterministic beam search")
P("A beam search plans multi-tick, multi-actor sequences. Per tick each coalition actor chooses from "
  "a menu {rest} + transfers to each admissible neighbour at several quantities (small splits and "
  "full); the joint action is the product over the coalition; the beam keeps the top states by the "
  "objective. The action space thus spans neighbouring transfers, small splits, repeated/multi-tick "
  "actions, relays, cyclic/back-and-forth moves, coordinated multi-actor moves, and harvesting near "
  "or below regenerative reserves. The search is deterministic and consumes no randomness (tested), "
  "so it cannot peek at future events.")
h2("2.3 Two separated objectives")
P("(I) an <b>automated adversary</b> maximising its own cumulative guarded EBU; (II) a <b>red-team</b> "
  "maximising cumulative physical harm subject to net EBU &gt;= a positive threshold. These are kept "
  "apart throughout.")
h2("2.4 Exploit definition (fixed before the final runs)")
eq("An exploit requires ALL of:\n"
   "  1. coalition cumulative net guarded EBU > 0                 (profitable)\n"
   "  2. physical condition persistently worse than a PAIRED\n"
   "     no-action baseline (coalition rests, natural dynamics)\n"
   "  3. the deterioration holds for a declared persistence window\n"
   "     (every tail tick, not a one-tick blip)\n"
   "  4. harm measured on PHYSICAL variables (threshold-aware\n"
   "     burden B_R), never on EBU itself.")
P("Reported physical harm variables: final and post-shock viability, sustained recovery, unmet "
  "demand, dead regenerative sources, Allee-threshold crossings, source stock, B_R, transport "
  "dissipation. Reported EBU variables: issued credit, issued debit, net EBU, balances, concentration, "
  "plus search runtime and explored states.")

# ---- 3 ----
h1("3. Tests")
P("45 tests pass: the 33 prior tests (verified inline) plus 12 new V2.6 behavior tests &mdash; "
  "observational trajectory exactly unchanged; conservation during multi-action sequences; search "
  "reproducibility; genuinely distinct random layouts; rediscovery of a naive exploit; coalition "
  "totals = issued credit - debit; a lossless restoring multi-actor cycle earns no positive EBU; "
  "splitting cannot increase reward on the same trajectory; the exploit classifier requires BOTH "
  "positive net AND persistent harm; the search uses no future randomness; physics-only identical to "
  "the frozen baseline.")

# ---- 4 ----
h1("4. Results")
h2("4.1 (A) Five policies from an identical initial state")
P("Red-team fixture: a 3x3 world, an Allee source at the centre, eight deficient rim consumers, a "
  "two-actor coalition, 10 ticks. (This harsh, under-served world holds viability near 11% for every "
  "reasoned policy; it is a search fixture, not a homeostasis demo.)")
table([
    ["Policy", "viable %", "B_R", "dead", "src stock", "coalition net EBU"],
    ["1  physics / no EBU", "11.1", "77.8", "0", "8.6", "0.00"],
    ["2  naive greedy adversary", "11.1", "88.9", "0", "12.5", "+15.13"],
    ["3  guarded greedy adversary", "11.1", "71.1", "0", "9.0", "+21.21"],
    ["4  random adversary", "22.2", "206.2", "1", "0.0", "-126.69"],
    ["5  automated guarded (beam)", "11.1", "78.2", "0", "8.9", "+13.82"],
], colw=[5.2 * cm, 1.9 * cm, 1.6 * cm, 1.4 * cm, 2.1 * cm, 2.6 * cm])
tag("<i>Observation:</i> the random adversary is the only one that clearly worsens the field "
    "(B_R 206, a dead source) and it loses EBU (-126.69); the beam explored 22,743 states.")

h2("4.2 (B) Red-team search for profitable persistent harm")
table([
    ["Ledger", "verdict", "net EBU", "persistent harm", "mean tail-harm (B_R)", "states"],
    ["naive (positive control)", "EXPLOIT FOUND", "+15.35", "yes", "+102.91", "3,809"],
    ["guarded", "no exploit found", "+0.91", "no", "-5.47", "10,971"],
], colw=[4.2 * cm, 3.0 * cm, 1.7 * cm, 2.0 * cm, 2.6 * cm, 1.5 * cm])
tag("<i>Experimental result:</i> the search rediscovers a naive exploit &mdash; the coalition "
    "harvests the Allee source below its threshold to serve deficient consumers, earning positive "
    "naive credit (plain-burden improvement) at zero naive cost while the source dies; harm persists "
    "through the whole tail. Under the guarded ledger the same search finds no profitable persistent "
    "harm: the best net-positive sequence it finds actually leaves the field better than no action "
    "(mean tail-harm -5.47).")
tag("<i>Interpretation:</i> the positive control confirms the search is strong enough to expose a "
    "known ledger weakness, so its failure to break the guarded ledger on this fixture is meaningful "
    "&mdash; but see the limitations before generalising.")

h2("4.3 (C) Randomized-layout topology study")
P("Guarded <i>greedy</i> adversary vs a paired no-action baseline, on 12 genuinely distinct random "
  "5x5 Allee layouts (30 ticks each). Harm = final B_R(attack) - B_R(no-action); positive means the "
  "adversary left the field worse than doing nothing.")
table([
    ["Metric", "mean", "sd", "min", "max"],
    ["coalition net guarded EBU", "530.24", "130.47", "387.41", "819.94"],
    ["final viability %", "58.67", "32.63", "0.00", "100.00"],
    ["harm: B_R(attack) - B_R(no-action)", "-77.02", "249.36", "-271.13", "+592.15"],
], colw=[7.0 * cm, 2.3 * cm, 2.3 * cm, 2.0 * cm, 2.0 * cm])
tag("<i>Experimental result:</i> on average the greedy guarded adversary is net-helpful (mean harm "
    "-77, i.e. better than no action), BUT on <b>4 of 12</b> layouts it is net-harmful (harm up to "
    "+592) while net EBU is positive.")
tag("<i>Interpretation / caveat:</i> this is a candidate-exploit signal for the MYOPIC greedy policy "
    "&mdash; not a confirmed exploit, because persistence was not checked with the tail window here. "
    "The red-team in 4.2 tested only the small hand-built fixture, not these layouts.")
figure("figures/v26_random.png",
       "Figure 1. Guarded greedy adversary across 12 random layouts. Most points sit below zero "
       "(better than no action), but four sit above it (worse than no action) with positive net EBU.")
figure("figures/v26_policies.png",
       "Figure 2. Five policies on the red-team fixture: viability (green) and coalition net EBU "
       "(purple). Only the random adversary worsens the field, and it loses EBU.")

# ---- 5 ----
h1("5. Verdict")
P("<b>No profitable persistent-harm exploit against the guarded ledger was found within the declared "
  "search space and computational budget.</b> This is a falsification result, not a security proof: "
  "we do NOT claim guarded EBU is secure or that gaming is impossible. The claim is bounded by the "
  "fixture, the action menu, the beam depth/width, and the coalition size actually searched.")
P("<b>The strongest honest caveat</b> is finding (C): the myopic greedy guarded adversary left the "
  "field worse than no action on 4 of 12 random layouts while earning positive EBU. The proper "
  "exploit definition (persistence window) was not applied there, so these are signals, not "
  "confirmed exploits &mdash; but they show the guarded incentive does not provably align with health "
  "on every topology, and they define the top priority for the next stage.")
P("<b>Hypothesis (to test next):</b> the greedy harm arises because guarded credit is per-action and "
  "local; a myopic actor can take locally-credited actions whose combined multi-tick effect is worse "
  "than inaction. A lookahead or a persistence-aware debit may close it.")

# ---- 6 ----
h1("6. Limitations and Next Steps")
P("1. The red-team searched one small hand-built fixture and a 2-actor coalition; it did not "
  "red-team the harmful random layouts from (C).<br/>"
  "2. Beam search is incomplete; a negative result reflects the searched space, not all sequences.<br/>"
  "3. Harm in (C) is a single-point comparison without a persistence window.<br/>"
  "4. Coalition size, action-menu granularity, and depth/width were kept small for runtime.<br/>"
  "<b>Next:</b> apply the full exploit definition (persistence) to the (C) harmful layouts; grow the "
  "coalition and action menu; add a learning/local-optimiser adversary; and if a guarded exploit is "
  "confirmed, implement a corrected guarded variant and compare old vs corrected on the same attacks "
  "and physical baselines, checking the fix does not reward hoarding or starve demand.")
gap(6)
P("<b>Reproducibility.</b> Baseline commit, branch commit, exact commands, Python version, "
  "dependencies, seeds, and all search/experiment parameters are recorded in "
  "results/v2.6/MANIFEST.md; the captured final output is results/v2.6/v26_experiments.txt. This "
  "document is an adversarial-search study; the project has not introduced an economy.")


def build():
    SimpleDocTemplate(OUT, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                      topMargin=1.8 * cm, bottomMargin=1.8 * cm,
                      title="The Energy Balance Project - Foundation Model V2.6",
                      author="Energy Balance Project").build(S)
    print("wrote", OUT)


if __name__ == "__main__":
    build()
