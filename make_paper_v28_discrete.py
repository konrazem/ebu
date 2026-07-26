"""
Generate the V2.8 discrete mathematical foundation PDF:
  Foundation_v2.8_discrete.pdf

Content mirrors Foundation_v2.8_discrete_draft.md (the authoritative source) in
full: every Definition / Assumption / Lemma / Theorem / Corollary / Counterexample /
Conjecture, the Model D0 vs DE-family scope table, and all exclusions. Equations are
TYPESET (matplotlib mathtext -> PNG embedded in the reportlab flow); no external
LaTeX toolchain is required.

Run with the project venv:  venv/bin/python make_paper_v28_discrete.py

This is a documentation build only. It does NOT touch the physics or EBU engine,
and it does not upgrade any claim: the note is a proof attempt awaiting independent
expert review, and the companion test_v28.py is numerical validation, never proof.
"""
from __future__ import annotations
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
                                TableStyle, PageBreak, HRFlowable)

OUT = "Foundation_v2.8_discrete.pdf"
EQ_DPI = 220
EQ_DIR = tempfile.mkdtemp(prefix="v28eq_")
_eqn = [0]

sty = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=sty["Heading1"], fontSize=14, spaceBefore=14, spaceAfter=6,
                    textColor=colors.HexColor("#1F3A5F"))
H2 = ParagraphStyle("H2", parent=sty["Heading2"], fontSize=11.5, spaceBefore=10, spaceAfter=4,
                    textColor=colors.HexColor("#2C5580"))
BODY = ParagraphStyle("BODY", parent=sty["BodyText"], fontSize=9.7, leading=13.6,
                      alignment=TA_JUSTIFY, spaceAfter=6)
TITLE = ParagraphStyle("TITLE", parent=sty["Title"], fontSize=21, textColor=colors.HexColor("#1F3A5F"))
SUB = ParagraphStyle("SUB", parent=sty["Italic"], fontSize=11, alignment=TA_CENTER,
                     textColor=colors.HexColor("#2C5580"))
THM = ParagraphStyle("THM", parent=BODY, leftIndent=10, rightIndent=8, spaceBefore=4, spaceAfter=6,
                     borderColor=colors.HexColor("#C6D2DE"), borderWidth=0.6, borderPadding=6,
                     backColor=colors.HexColor("#F5F8FB"))
CEX = ParagraphStyle("CEX", parent=THM, borderColor=colors.HexColor("#D9C6C6"),
                     backColor=colors.HexColor("#FBF5F5"))
CELL = ParagraphStyle("CELL", parent=BODY, fontSize=8.3, leading=10.4, spaceAfter=0, alignment=TA_LEFT)
CELLH = ParagraphStyle("CELLH", parent=CELL, textColor=colors.white, fontName="Helvetica-Bold")

S = []
def P(t): S.append(Paragraph(t, BODY))
def h1(t): S.append(Paragraph(t, H1))
def h2(t): S.append(Paragraph(t, H2))
def thm(t): S.append(Paragraph(t, THM))
def cex(t): S.append(Paragraph(t, CEX))
def gap(h=6): S.append(Spacer(1, h))


def eq(latex, fontsize=13):
    """Render a LaTeX math string to a PNG via mathtext and add it centered."""
    _eqn[0] += 1
    path = os.path.join(EQ_DIR, f"eq{_eqn[0]}.png")
    fig = plt.figure()
    fig.text(0.5, 0.5, f"${latex}$", fontsize=fontsize, ha="center", va="center",
             color="#12243A")
    fig.savefig(path, dpi=EQ_DPI, transparent=True, bbox_inches="tight", pad_inches=0.04)
    plt.close(fig)
    from PIL import Image as PILImage
    with PILImage.open(path) as im:
        pw, ph = im.size
    dw = pw * 72.0 / EQ_DPI
    dh = ph * 72.0 / EQ_DPI
    maxw = 15.5 * cm
    if dw > maxw:
        s = maxw / dw
        dw, dh = dw * s, dh * s
    img = Image(path, width=dw, height=dh)
    img.hAlign = "CENTER"
    S.append(img)
    gap(6)


def table(data, colw):
    wr = [[Paragraph(str(c), CELLH if r == 0 else CELL) for c in row]
          for r, row in enumerate(data)]
    t = Table(wr, colWidths=colw)
    t.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#C8D2DC")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F3A5F"))]))
    S.append(t)
    gap(10)


C = "<font face='Courier'>%s</font>"
def c(t): return C % t


# ============================ title ============================
S.append(Spacer(1, 2.6 * cm))
S.append(Paragraph("The Energy Balance Project", TITLE)); gap(6)
S.append(Paragraph("Discrete Mathematical Foundation &mdash; Version 2.8", SUB))
S.append(Paragraph("A synchronous discrete energy&ndash;dissipation inequality for "
                   "Model D0, with explicit finite-step remainder", SUB))
gap(16)
S.append(HRFlowable(width="60%", color=colors.HexColor("#1F3A5F"), thickness=1)); gap(16)
P("<b>Status: mathematics only, NOT YET PEER REVIEWED.</b> Every derivation in this "
  "note is a proof attempt awaiting independent expert review. No physical engine, "
  "test of prior versions, or EBU-accounting behaviour is changed by this stage.")
P("<b>Numerical validation is not mathematical proof.</b> The companion "
  + c("test_v28.py") + " (11 groups, 132 numerical checks, standard library only, "
  "deterministic seed 20260726) validates the statements below on declared fixtures, "
  "deterministic samples, and negative controls. A passing run means the claims hold "
  "at the tested points; it establishes no theorem, and the check count is not a "
  "count of theorems.")
P("<b>Scope in one sentence.</b> V2.7 proved a <i>continuous-time</i> "
  "energy&ndash;dissipation identity for the smooth, unconstrained, simultaneous "
  "Onsager flow (Model C). V2.8 derives a <i>discrete-time</i> counterpart for the "
  "simplest compatible synchronous system (<b>Model D0</b>: frozen-state, "
  "simultaneous, unconstrained, loss-aware explicit Euler) &mdash; and states "
  "precisely why that result does <b>not</b> yet cover the production Python engine "
  "family (the DE family, &sect;3). Proving D0 is a first brick, not the building.")
P("Epistemic labels are used strictly: <b>Definition / Assumption / Lemma / Theorem / "
  "Corollary / Proof / Counterexample / Conjecture / Numerical validation</b>. "
  "This PDF is generated from " + c("Foundation_v2.8_discrete_draft.md") + " (the "
  "authoritative source) by " + c("make_paper_v28_discrete.py") + "; equations are "
  "typeset with the matplotlib mathtext engine.")
S.append(PageBreak())

# ============================ 1. purpose ============================
h1("1. Purpose and relationship to V2.7")
P("V2.7 (Theorem 7.1) established, in continuous time, for the derived Onsager flow "
  + c("dx/dt = u(x) + S J(x)") + ":")
eq(r"\frac{dV}{dt}=\sum_i \mu_i u_i-\sum_e\left(\frac{J_e^2}{M_e}+\theta_e J_e\right)"
   r"\ \leq\ \sum_i \mu_i u_i")
P("The Python engine does not run this flow. It advances in ticks of size "
  + c("&Delta;t = 1") + ", applies <b>natural drive and transport as two ordered "
  "sub-steps</b>, evaluates whatever transport force it computes <b>loss-blind</b> "
  "(" + c("&mu;_i &minus; &mu;_j &minus; &theta;") + "; the forced harness of &sect;3 "
  "computes none), applies transfers <b>sequentially against live state</b>, and "
  "<b>clips</b> to " + c("[0, K]") + ". Theorem 7.1 explicitly excluded all of that.")
P("This note takes the first step across that gap: a <b>synchronous, unconstrained, "
  "loss-aware, explicit-Euler</b> discretisation (Model D0), for which we prove a "
  "discrete descent inequality with an <i>explicit</i> finite-step remainder, a "
  "one-edge sufficient step-size condition, conservative graph-level conditions "
  "(spectral, active-set, and state-specific), a conservation/loss ledger, and a "
  "one-tick locality theorem &mdash; while cataloguing, with counterexamples, exactly "
  "where the result stops.")

# ============================ 2. notation ============================
h1("2. Notation and standing assumptions")
P("<b>Definition 2.1 (state and functional).</b> State " + c("x &isin; R<super>n</super>")
  + " (unconstrained here &mdash; no " + c("[0, K]") + " box; see &sect;11). Separable "
  "state functional and local potential:")
eq(r"V(x)=\sum_i v_i(x_i),\qquad \mu_i(x)=\frac{\partial V}{\partial x_i}=v_i'(x_i),"
   r"\qquad \mu(x)=\nabla V(x)")
P("For the burden functional of the project (viable band " + c("[L_i, U_i]") + ", "
  "regenerative reserve " + c("R_i") + "):")
eq(r"v_i(x)=\alpha_i\,[\,L_i-x\,]_+^2+\beta_i\,[\,x-U_i\,]_+^2+\chi_i\,[\,R_i-x\,]_+^2")
P("so " + c("&nabla;V") + " is piecewise-linear and continuous and "
  + c("V &isin; C&sup1;") + " (each " + c("v_i &isin; C&sup1;") + ", "
  + c("v_i''") + " a step function).")
P("<b>Definition 2.2 (directed lossy edge).</b> For an edge " + c("e = (i, j)") + " with "
  "efficiency " + c("&eta;_e &isin; [0, 1]") + ", the state-change column "
  + c("S_e &isin; R<super>n</super>") + " has " + c("&minus;1") + " in slot i and "
  + c("+&eta;_e") + " in slot j; a scalar transfer " + c("q_e") + " maps "
  + c("x_i &rarr; x_i &minus; q_e") + ", " + c("x_j &rarr; x_j + &eta;_e q_e") + ". "
  "Stacking columns into " + c("S") + " and fluxes into " + c("J") + ", total transport "
  "is " + c("S J = &Sigma;_e J_e S_e") + ".")
P("<b>Definition 2.3 (loss-aware force and Onsager flux).</b> The force is the negative "
  "directional derivative of V along the transfer direction; with threshold "
  + c("&theta;_e &ge; 0") + " and mobility " + c("M_e &gt; 0") + " the raw Onsager "
  "flux follows:")
eq(r"f_e(x)=-\nabla V(x)^{\top}S_e=\mu_i-\eta_e\,\mu_j,\qquad "
   r"J_e(x)=M_e\,[\,f_e(x)-\theta_e\,]_+")
P("The sign/convention is <i>derived</i>, not assumed; Counterexample D (&sect;10) "
  "shows " + c("&mu;_i &minus; &mu;_j") + " is the <b>wrong</b> force when "
  + c("&eta;_e &lt; 1") + ".")
P("<b>Definition 2.4 (natural drive).</b> " + c("u_i(x) = s_i + g_i(x_i) &minus; d_i "
  "&minus; &lambda;_i &minus; &kappa;_i x_i") + ", collecting supply, regeneration, "
  "demand, constant and proportional leak (unconstrained: no saturation or clipping "
  "here).")
thm("<b>Assumption 2.5 (L-smoothness of V, with the CORRECTED constant).</b> "
    + c("&nabla;V") + " is " + c("L_V") + "-Lipschitz in the Euclidean norm. The exact "
    "branchwise slope of the gradient is")
eq(r"v_i'(x)=-2\alpha_i(L_i-x)_+ + 2\beta_i(x-U_i)_+ - 2\chi_i(R_i-x)_+")
eq(r"v_i''(x)=2\,[\,\alpha_i\,1_{x<L_i}+\beta_i\,1_{x>U_i}+\chi_i\,1_{x<R_i}\,]")
thm("Because the homeostatic deficit branch (" + c("x &lt; L_i") + ") and the reserve "
    "branch (" + c("x &lt; R_i") + ") &mdash; or the excess branch ("
    + c("x &gt; U_i") + ") and the reserve branch &mdash; can be <b>active "
    "simultaneously</b>, the slope is a <b>sum</b> of active weights, not their "
    "maximum. The exact global Lipschitz constant and its convenient safe upper bound "
    "(using " + c("L_i &le; U_i") + ", so at most one homeostatic branch is active) are:")
eq(r"L_V=\max_i\;\sup_x\;2\,[\,\alpha_i 1_{x<L_i}+\beta_i 1_{x>U_i}+\chi_i 1_{x<R_i}\,]"
   r"\ \leq\ 2\,\max_i\,[\,\max(\alpha_i,\beta_i)+\chi_i\,]")
P("The former draft's constant " + c("2 max_i max(&alpha;_i, &beta;_i, &chi;_i)") + " is "
  "<b>too small</b> whenever a homeostatic and the reserve penalty overlap &mdash; see "
  "Counterexample E (&sect;10). The symbol " + c("L_V") + " is used consistently in "
  "every descent, one-edge, graph, and driven bound below. All norms are Euclidean; "
  "the matrix norm is the spectral norm.")

# ============================ 3. three models ============================
h1("3. Three models kept strictly separate")
P("<b>Definition 3.1 (Model C &mdash; continuous Onsager law, V2.7).</b> "
  + c("dx/dt = u(x) + S J(x)") + ", all quantities at the instantaneous "
  + c("x(t)") + "; smooth, unconstrained, simultaneous. Subject of V2.7 Theorem 7.1.")
thm("<b>Definition 3.2 (Model D0 &mdash; ideal synchronous discrete law, THIS note).</b> "
    "Frozen-state, simultaneous, explicit (forward) Euler discretisation of C:")
eq(r"x^{n+1}=x^{n}+\Delta t\,\left(u(x^{n})+S\,J(x^{n})\right)\qquad\mathrm{(D0)}")
thm("<b>All</b> forces and fluxes are evaluated from the single state "
    + c("x<super>n</super>") + "; no clipping, no constraints, loss-aware force "
    "(Def 2.3). This is the subject of the new theorems.")
P("<b>Definition 3.3 (the DE engine family &mdash; three distinct update laws).</b> The "
  "Python operators actually run are <b>not one identical map</b>; they share related "
  "state accounting but differ. What all three share is only this: a natural-update "
  "stage N applied <b>first</b>, followed by <b>sequentially applied actions</b> "
  "against live state, at fixed " + c("&Delta;t = 1") + ". Whether &mdash; and how "
  "&mdash; a force is computed differs per member: <b>DE-core</b> computes proposals "
  "from &mu; at the post-drive state " + c("y = N(x<super>n</super>)") + " using the loss-blind "
  "force " + c("F = &mu;_i &minus; &mu;_j &minus; &theta;") + "; the <b>DE24-family</b> "
  "(six rules) computes proposals from marginals m at " + c("y = N(x<super>n</super>)") + " with "
  "the same loss-blind destination term (" + c("F = m_i &minus; m_j &minus; &theta;")
  + ", no &eta; weight on " + c("m_j") + "; reserve-aware modes add the on-site reserve "
  "marginal to m); <b>DE26-forced</b> computes <b>no force and no proposal</b> &mdash; "
  "it executes externally supplied actions subject only to feasibility caps.")
table([
    ["Member", "Function", "Transport sizing", "Conflict scaling", "Constraints"],
    ["DE-core", "energy_balance.step", "raw q = M[F]<sub>+</sub>",
     "proportional source scaling", "feasibility caps + clip to [0,K]"],
    ["DE24-family", "ebu_v24.step_v24 (6 rules)",
     "rule-dependent: golden-section line search or horizon-optimised q; "
     "gated by strict decrease or horizon impact",
     "none (sequential, sorted by F)",
     "per-proposal q_hi; hard reserve floor in hard_reserve only"],
    ["DE26-forced", "ebu_v26.forced_tick",
     "externally supplied quantities; no force or search computed", "none",
     "feasible_q caps (q_max, source floor, dest headroom)"],
], [2.2 * cm, 3.6 * cm, 4.7 * cm, 2.6 * cm, 3.6 * cm])
thm("<b>Assumption 3.4 (non-transfer of results).</b> A theorem about <b>D0</b> does "
    "<b>not</b> automatically hold for any member of the DE family. <b>D0 is the "
    "forward-Euler discretisation of Model C; the DE members are not.</b> The "
    "loss-blind raw law (DE-core) and the approximate coordinate-search rules "
    "(DE24-family) are not faithful discretisations of the loss-aware Onsager law C "
    "&mdash; their proposal forces are loss-blind (Counterexample D) and, for the "
    "DE24-family, the sizing rule differs entirely; DE26-forced computes no force at "
    "all &mdash; it is an execution harness for arbitrary feasible actions. D0 and "
    "the DE family differ in at least: operator splitting; the state at which the "
    "proposal force is frozen (" + c("x<super>n</super>") + " vs " + c("N(x<super>n</super>)") + "); "
    "loss-aware vs loss-blind proposal force vs no force; simultaneous vs sequential "
    "application; conflict scaling (DE-core) or line-search/horizon sizing "
    "(DE24-family); unconstrained vs clipped; and &Delta;t free vs &Delta;t = 1.")

# ============================ 4. one-edge derivation ============================
h1("4. One-edge derivation: exact identities and the descent inequality")
h2("4.1 Exact first-order identity")
thm("<b>Lemma 4.1 (first-order contribution).</b> For the D0 update, writing "
    + c("&Delta;x = x<super>n+1</super> &minus; x<super>n</super> = &Delta;t(u + SJ)")
    + " (all at " + c("x<super>n</super>") + "),")
eq(r"\nabla V(x^{n})^{\top}\Delta x=\Delta t\;\nabla V(x^{n})^{\top}u(x^{n})"
   r"\;-\;\Delta t\sum_e f_e\,J_e")
P("<b>Proof.</b> " + c("&nabla;V<super>T</super>&Delta;x = &Delta;t(&nabla;V<super>T</super>u + "
  "&nabla;V<super>T</super>SJ)") + ". Per edge, " + c("&nabla;V<super>T</super>S_e = &minus;f_e")
  + " by Def 2.3, so " + c("&nabla;V<super>T</super>SJ = &minus;&Sigma;_e f_e J_e") + ". &#9633;")
thm("<b>Lemma 4.2 (edge dissipation identity).</b> For every edge,")
eq(r"f_e\,J_e=\frac{J_e^2}{M_e}+\theta_e\,J_e")
P("<b>Proof.</b> If the edge is <b>active</b> (" + c("f_e &gt; &theta;_e") + ", so "
  + c("J_e = M_e(f_e &minus; &theta;_e) &gt; 0") + "), then "
  + c("f_e = J_e/M_e + &theta;_e") + "; multiply by " + c("J_e") + ". If "
  "<b>inactive</b> (" + c("f_e &le; &theta;_e") + ", so " + c("J_e = 0") + "), both "
  "sides are 0 regardless of the sign of " + c("f_e") + ". &#9633;")
P("Combining, the first-order transport term is "
  + c("&minus;&Delta;t &Sigma;_e (J_e&sup2;/M_e + &theta;_e J_e) &le; 0")
  + " (each summand &ge; 0 since " + c("J_e &ge; 0, &theta;_e &ge; 0") + ").")
h2("4.2 Discrete descent inequality with explicit remainder")
thm("<b>Lemma 4.3 (descent lemma).</b> Under Assumption 2.5, for any x, y in the "
    "region: " + c("V(y) &le; V(x) + &nabla;V(x)<super>T</super>(y &minus; x) + "
    "(L_V/2)||y &minus; x||&sup2;") + ".")
thm("<b>Theorem 4.4 (one-step discrete inequality).</b> Under Assumption 2.5, the D0 "
    "update satisfies, with " + c("&Delta;x = &Delta;t(u + SJ)") + ":")
eq(r"V(x^{n+1})-V(x^{n})\ \leq\ \Delta t\,\nabla V(x^{n})^{\top}u(x^{n})"
   r"\;-\;\Delta t\sum_e\left(\frac{J_e^2}{M_e}+\theta_e J_e\right)\;+\;R_n"
   r"\qquad(\bigstar)")
eq(r"R_n:=\frac{L_V}{2}\,\Vert\Delta x\Vert^2=\frac{L_V\,\Delta t^2}{2}\,"
   r"\Vert u+S J\Vert^2"
   r"=\frac{L_V\,\Delta t^2}{2}\left(\Vert u\Vert^2+2\,u^{\top}SJ+\Vert SJ\Vert^2\right)")
thm("The remainder splits explicitly, exposing the <b>drive&ndash;transport cross "
    "term</b> " + c("2u<super>T</super>SJ") + ". <b>Proof.</b> Apply Lemma 4.3 with "
    + c("x = x<super>n</super>, y = x<super>n+1</super>") + "; substitute Lemma 4.1 for the "
    "first-order term and Lemma 4.2 for the edge sum; expand "
    + c("||u + SJ||&sup2;") + ". &#9633;")
P("<b>Remark 4.5 (remainder notation &mdash; two objects, kept apart).</b> The "
  "<b>exact Taylor remainder</b> of the functional along the step is")
eq(r"r_n:=V(x^{n+1})-V(x^{n})-\nabla V(x^{n})^{\top}\Delta x,\qquad "
   r"|\,r_n\,|\ \leq\ \frac{L_V}{2}\Vert\Delta x\Vert^2\ =\ R_n")
P("(the two-sided quadratic bound for an " + c("L_V") + "-Lipschitz gradient). "
  + c("R_n") + " <b>equals</b> its expression by definition &mdash; it is not itself "
  "'bounded by' it &mdash; and " + c("R_n = O(&Delta;t&sup2;)") + ". Neither "
  + c("r_n") + " nor " + c("R_n") + " is the local truncation error of the state "
  "trajectory; &sect;7 keeps the three error notions separate.")

# ============================ 5. graph derivation ============================
h1("5. Step-size bounds: one edge, graph, active set, state-specific")
h2("5.1 Undriven descent, one edge")
thm("<b>Theorem 5.1 (one-edge step-size bound, u = 0).</b> For a single active edge "
    + c("e = (i, j)") + " with " + c("u &equiv; 0") + ", the D0 step satisfies "
    + c("V(x<super>n+1</super>) &le; V(x<super>n</super>)") + " whenever")
eq(r"\Delta t\ \leq\ \frac{2}{L_V\,M_e\,(1+\eta_e^2)}")
thm("Including " + c("&theta;_e") + " only relaxes this: the true admissible range is "
    + c("&Delta;t &le; (2/(L_V(1+&eta;_e&sup2;)))(1/M_e + &theta;_e/J_e)") + ". "
    "<b>Proof.</b> With u = 0, (&#9733;) gives "
    + c("V(x<super>n+1</super>) &minus; V(x<super>n</super>) &le; &minus;&Delta;t(J&sup2;/M_e + "
    "&theta;_e J) + (L_V &Delta;t&sup2;/2)||S_e||&sup2;J&sup2;") + " with "
    + c("||S_e||&sup2; = 1 + &eta;_e&sup2;") + "; drop the non-negative "
    + c("&theta;_e J") + " term and solve. &#9633;")
P("<b>Consistency with V2.7 &sect;5.</b> Setting " + c("&Delta;t = 1") + " gives "
  + c("M_e &le; 2/(L_V(1+&eta;_e&sup2;))") + "; with " + c("L_V = 2w") + " (a single "
  "homeostatic branch of weight w, no reserve overlap) this is "
  + c("M_e &le; 1/(w(1+&eta;&sup2;))") + " &mdash; identical to the V2.7 &sect;5.2 "
  "symmetric single-transfer bound. Counterexample A (&sect;10) shows the bound is "
  "<b>tight</b> (necessary and sufficient) in the symmetric <i>pure-quadratic</i> "
  "fixture defined there.")
h2("5.2 Undriven descent, graph")
thm("<b>Theorem 5.2 (spectral step-size bound, u = 0).</b> Let "
    + c("D_M = diag(M_e)") + ". If")
eq(r"\Delta t\ \leq\ \frac{2}{L_V\,\Vert S\,D_M^{1/2}\Vert_2^{\,2}}")
thm("then the D0 step satisfies " + c("V(x<super>n+1</super>) &le; V(x<super>n</super>)")
    + " for u = 0. The matrix inequality in the proof is <b>uniform over all vectors "
    "J</b>, so in particular it holds for every <b>Onsager-generated</b> flux vector "
    "(Def 2.3); the descent conclusion still relies on that flux law (via Lemma 4.2), "
    "not on an arbitrary J.")
P("<b>Proof.</b> From (&#9733;) with u = 0, after dropping the non-negative &theta; "
  "term, a sufficient condition is "
  + c("J<super>T</super>D_M<super>&minus;1</super>J &ge; (L_V&Delta;t/2) J<super>T</super>S<super>T</super>SJ") + ". "
  "Substituting " + c("y = D_M<super>&minus;1/2</super>J") + " this reads "
  + c("||y||&sup2; &ge; (L_V&Delta;t/2) y<super>T</super>(D_M<super>1/2</super>S<super>T</super>S D_M<super>1/2</super>)y")
  + " for all y, i.e. "
  + c("(L_V&Delta;t/2) &lambda;_max(D_M<super>1/2</super>S<super>T</super>S D_M<super>1/2</super>) &le; 1")
  + ". Since " + c("D_M<super>1/2</super>S<super>T</super>S D_M<super>1/2</super> = "
  "(S D_M<super>1/2</super>)<super>T</super>(S D_M<super>1/2</super>)") + ", its largest eigenvalue is the "
  "squared spectral norm; rearrange. Uniformity over J is a convenience &mdash; it "
  "does <b>not</b> assert that an arbitrary flux vector dissipates; only the "
  "Onsager-law flux does, through Lemma 4.2. &#9633;")
P("<b>Corollary 5.3 (one-edge special case).</b> For a single edge "
  + c("||S D_M<super>1/2</super>||&sup2; = M_e(1 + &eta;_e&sup2;)") + ", recovering "
  "Theorem 5.1 exactly.")
P("<b>Remark 5.4 (structure of S<super>T</super>S, and a degree-weighted Gershgorin bound).</b> "
  + c("(S<super>T</super>S)_ee' = S_e&middot;S_e'") + ": diagonal " + c("1 + &eta;_e&sup2;")
  + "; +1 for two edges sharing their <b>source</b>; " + c("&eta;_e&eta;_e'") + " for "
  "two sharing their <b>destination</b>; " + c("&minus;&eta;") + " when one edge's "
  "destination is the other's source. Using the <b>similarity</b> (equal spectra) "
  + c("D_M<super>1/2</super>S<super>T</super>S D_M<super>1/2</super> ~ D_M S<super>T</super>S") + " and applying "
  "Gershgorin to the rows of the (generally non-symmetric) " + c("D_M S<super>T</super>S") + ":")
eq(r"\Vert S\,D_M^{1/2}\Vert_2^{\,2}=\lambda_{\max}(D_M S^{\top}S)"
   r"\ \leq\ \max_e\;M_e\left[(1+\eta_e^2)+\sum_{e'\neq e}\left|S_e\cdot S_{e'}\right|\right]")
thm("<b>Theorem 5.5 (active-set spectral bound, u = 0).</b> Let "
    + c("A(x<super>n</super>) = { e : f_e(x<super>n</super>) &gt; &theta;_e }") + " be the active edge "
    "set, and " + c("S_A, D_M,A") + " the restrictions to it. Because inactive edges "
    "carry " + c("J_e = 0") + ", the proof of Theorem 5.2 applies verbatim restricted "
    "to A. Hence")
eq(r"\Delta t\ \leq\ \frac{2}{L_V\,\Vert S_A\,D_{M,A}^{1/2}\Vert_2^{\,2}}")
thm("guarantees " + c("V(x<super>n+1</super>) &le; V(x<super>n</super>)") + " for the current "
    "step. Since " + c("A(x<super>n</super>) &sube; E") + ", the active-set norm never exceeds "
    "the full norm, so Theorem 5.5 is never worse than Theorem 5.2 and often strictly "
    "better.")
thm("<b>Lemma 5.6a (the Onsager flux has no nonzero null flow).</b> At any state, the "
    "Onsager flux J of Def 2.3 satisfies")
eq(r"\mu^{\top}S\,J\;=\;-\sum_e\left(\frac{J_e^2}{M_e}+\theta_e J_e\right)")
thm("Consequently " + c("SJ = 0 &rArr; J = 0") + ". <b>Proof.</b> By the per-edge "
    "computation of Lemma 4.1, " + c("&mu;<super>T</super>S_e = &minus;f_e") + ", so "
    + c("&mu;<super>T</super>SJ = &minus;&Sigma;_e f_e J_e") + "; by Lemma 4.2 (valid precisely "
    "because J is the Onsager flux), " + c("f_e J_e = J_e&sup2;/M_e + &theta;_e J_e")
    + " on every edge. If " + c("SJ = 0") + " the left side is 0, so the nonnegative "
    "sum vanishes term by term; since " + c("M_e &gt; 0") + ", "
    + c("J_e&sup2;/M_e = 0") + " forces " + c("J_e = 0") + " for all e. &#9633;")
P("<b>Scope.</b> An <b>arbitrary externally prescribed</b> flow may of course satisfy "
  + c("SJ = 0") + " with " + c("J &ne; 0") + " &mdash; e.g. an equal circulation "
  "around a lossless cycle &mdash; but such a flow is <b>not generated by the Onsager "
  "law</b> of Def 2.3 and lies outside Lemma 5.6a and Theorem 5.6 (cf. the uniformity "
  "remark in Theorem 5.2: only the Onsager-law flux dissipates through Lemma 4.2).")
thm("<b>Theorem 5.6 (direct state-specific bound, u = 0).</b> At a fixed state "
    + c("x<super>n</super>") + " with Onsager flux " + c("J = J(x<super>n</super>)") + ": if "
    + c("J = 0") + " (no active edge), the transport step is trivial and V is "
    "unchanged by transport; if " + c("J &ne; 0") + ", then necessarily "
    + c("SJ &ne; 0") + " (Lemma 5.6a), and")
eq(r"\Delta t\ \leq\ \frac{2\sum_e\left(J_e^2/M_e+\theta_e J_e\right)}"
   r"{L_V\,\Vert S J\Vert^2}")
thm("guarantees " + c("V(x<super>n+1</super>) &le; V(x<super>n</super>)") + " (the bound is "
    "well defined and strictly positive: " + c("||SJ|| &gt; 0") + " and the "
    "dissipation sum is &gt; 0 whenever " + c("J &ne; 0") + "). <b>Proof.</b> Direct "
    "from (&#9733;) with u = 0: if J = 0 the whole transport term vanishes; if "
    + c("J &ne; 0") + ", Lemma 5.6a gives " + c("||SJ|| &gt; 0") + ", and solving the "
    "quadratic-in-&Delta;t inequality for a nonpositive right-hand side yields the "
    "stated bound. &#9633;")
P("<b>Conjecture 5.7 (tightness &mdash; OPEN).</b> The active-set (5.5) and "
  "state-specific (5.6) bounds are <i>sufficient</i> current-step conditions. Whether "
  "either coincides with the <b>tight</b> admissible &Delta;t is open; the "
  "pure-quadratic one-edge fixture of Counterexample A is the only case where "
  "tightness is established. No empirical threshold is claimed as a theorem.")

# ============================ 6. driven ============================
h1("6. The discrete driven inequality (u &ne; 0)")
thm("<b>Theorem 6.1 (driven one-step inequality).</b> Under Assumption 2.5, (&#9733;) "
    "holds verbatim for " + c("u &ne; 0") + ". V is governed by the competition of "
    "three terms &mdash; drive, dissipation, remainder:")
eq(r"V(x^{n+1})-V(x^{n})\ \leq\ \Delta t\,\mu^{\top}u"
   r"\;-\;\Delta t\sum_e\left(\frac{J_e^2}{M_e}+\theta_e J_e\right)"
   r"\;+\;\frac{L_V\,\Delta t^2}{2}\,\Vert u+SJ\Vert^2")
thm("(first term: <b>drive</b>; second: <b>dissipation</b>; third: <b>finite-step "
    "remainder</b>.)")
thm("<b>Corollary 6.2 (sufficient one-step decrease).</b> "
    + c("V(x<super>n+1</super>) &le; V(x<super>n</super>)") + " holds if")
eq(r"\sum_e\left(\frac{J_e^2}{M_e}+\theta_e J_e\right)\ \geq\ \mu^{\top}u"
   r"\;+\;\frac{L_V\,\Delta t}{2}\,\Vert u+SJ\Vert^2")
P("Two readings: (i) if " + c("&mu;<super>T</super>u &le; 0") + " (drive already lowers V) and "
  "&Delta;t is small enough for dissipation to dominate the remainder, V decreases; "
  "(ii) if " + c("&mu;<super>T</super>u &gt; 0") + " (drive raises V), decrease requires "
  "transport dissipation to exceed the drive <b>plus</b> the remainder.")
P("<b>Non-result 6.3.</b> V is <b>not</b> monotone in the driven case in general "
  "&mdash; Counterexample C (&sect;10) exhibits a drive making V strictly increase in "
  "one step. We claim only the conditional Corollary 6.2, never unconditional descent.")

# ============================ 7. relationship to V2.7 ============================
h1("7. Relationship to V2.7 (Model C)")
P("<b>Consistency (&Delta;t &rarr; 0) &mdash; from the exact identity, not the "
  "inequality.</b> Because V is C&sup1;, the directional derivative is exact; applying "
  "the <b>exact</b> Lemma 4.1 and Lemma 4.2 gives "
  + c("dV/dt = &mu;<super>T</super>u &minus; &Sigma;_e(J_e&sup2;/M_e + &theta;_e J_e)") + ", "
  "which is exactly V2.7's Theorem 7.1. Equivalently the D0 forward difference "
  "converges to it because " + c("R_n/&Delta;t = (L_V&Delta;t/2)||u+SJ||&sup2; &rarr; 0")
  + ". Theorem 7.1 is recovered from the exact identity plus differentiability, with "
  "the inequality only bounding the finite-&Delta;t gap.")
P("<b>Three distinct error quantities (do not conflate).</b> (1) the <b>exact Taylor "
  "remainder r_n of V</b> (Remark 4.5), rigorously bounded by "
  + c("|r_n| &le; R_n = (L_V&Delta;t&sup2;/2)||u+SJ||&sup2; = O(&Delta;t&sup2;)")
  + "; (2) the <b>local truncation error of the state trajectory</b>, "
  + c("x(t_n+&Delta;t) &minus; x<super>n+1</super> = O(&Delta;t&sup2;)") + " &mdash; "
  "valid only in smooth regions away from the switching surfaces "
  + c("{x_i = L_i, U_i, R_i}") + " where &nabla;V is only Lipschitz, not C&sup1;; "
  "(3) the <b>accumulated global trajectory error</b> " + c("O(&Delta;t)") + " over a "
  "fixed interval, which additionally needs a locally Lipschitz field and a bounded "
  "solution. Item (1) is about the functional V; items (2)&ndash;(3) are about the "
  "trajectory; they are different objects.")
P("<b>Finite-&Delta;t trajectories are not identical to C.</b> The Euler iterate "
  "departs from the continuous flow by the accumulated O(&Delta;t) error; equality "
  "holds only in the limit.")
P("<b>The safe search is an approximate minimiser, not the Onsager flux.</b> In the "
  "engine family, the line-sized rules of the DE24-family size a transfer by "
  + c("_golden_min") + ", a finite 24-iteration golden-section search &mdash; an "
  "<i>approximate bounded one-dimensional minimiser</i> of "
  + c("q &rarr; v_i(x_i &minus; q) + v_j(x_j + &eta;q)") + " on " + c("[0, q_hi]")
  + ", gated on strict decrease (the horizon-sized rules optimise a different, "
  "horizon-impact objective again). This is an (approximate) coordinate-descent-style "
  "step on V, <b>not</b> the explicit flux " + c("q = M_e[f_e &minus; &theta;_e]<sub>+</sub>")
  + ", and it is <b>not</b> proximal (no proximal objective or proof is claimed).")
P("<b>Proving D0 does not prove the DE family.</b> Beyond the flux-vs-search point, "
  "the DE members differ from D0 by operator splitting, the proposal state frozen at "
  + c("N(x<super>n</super>)") + " (where a proposal is computed at all), the loss-blind "
  "proposal force (DE-core, DE24-family; DE26-forced computes no force), sequential "
  "live state, conflict scaling (DE-core), and clipping (&sect;3, &sect;10 B and D). "
  "Each is out of scope (&sect;11).")

# ============================ 8. ledger ============================
h1("8. Conservation and loss ledger")
thm("<b>Theorem 8.1 (synchronous stock balance).</b> With <b>1</b> the all-ones "
    "vector, the D0 step changes total stock by")
eq(r"\mathbf{1}^{\top}(x^{n+1}-x^{n})=\Delta t\,\left[\;\mathbf{1}^{\top}u(x^{n})"
   r"\;-\;\sum_e\,(1-\eta_e)\,J_e(x^{n})\;\right]")
thm("<b>Proof.</b> " + c("1<super>T</super>&Delta;x = &Delta;t(1<super>T</super>u + 1<super>T</super>SJ)") + " and "
    + c("1<super>T</super>S_e = (&minus;1) + &eta;_e = &minus;(1 &minus; &eta;_e)") + ". &#9633;")
P("<b>Corollary 8.2 (loss is explained, not destroyed).</b> Since "
  + c("&eta;_e &le; 1, J_e &ge; 0") + ", transport removes exactly "
  + c("&Sigma;_e(1 &minus; &eta;_e)J_e &ge; 0") + " units of stock &mdash; the "
  "<b>efficiency loss</b>, an accounted outflow. Lossless edges ("
  + c("&eta;_e = 1") + ") conserve stock exactly; all stock change is then "
  "attributable to the natural drive.")
P("<b>Remark 8.3 (two different statements).</b> Stock balance (Theorem 8.1, about "
  + c("1<super>T</super>x") + ") and Lyapunov descent (Theorems 4.4/6.1, about V) are "
  "independent: V is not a stock, and a lossy transfer that <i>reduces</i> V still "
  "<i>removes</i> physical stock. Keep them separate.")

# ============================ 9. locality ============================
h1("9. Locality and causal speed")
P("<b>Definition 9.0 (undirected dependency graph).</b> " + c("G_u") + " joins i and j "
  "iff a directed transfer edge (i,j) or (j,i) exists; " + c("dist") + " is graph "
  "distance in " + c("G_u") + ". <b>Assumption 9.0&prime; (on-site drive).</b> Each "
  + c("u_i(x)") + " depends only on " + c("x_i") + " (Def 2.4). A drive coupling "
  "several cells would break the result below.")
thm("<b>Theorem 9.1 (one-tick dependency radius, D0).</b> Under the synchronous "
    "frozen-state update with Assumption 9.0&prime;, "
    + c("x<super>n+1</super>_i") + " depends only on "
    + c("{ x<super>n</super>_k : dist(i,k) &le; 1 }") + ". By induction, "
    + c("x<super>n+m</super>_i") + " depends only on cells within distance m: "
    "information propagates at most one edge per tick. <b>Proof.</b> "
    + c("u_i") + " is on-site (0 hops); each incident "
    + c("J_e = M_e[&mu;_a &minus; &eta;_e&mu;_b &minus; &theta;_e]<sub>+</sub>")
    + " depends only on the two endpoints of e (1 hop). Compose and induct. &#9633;")
cex("<b>Counterexample / Observation 9.2 (sequential live state breaks this).</b> "
    "Every member of the DE family applies its transfers (accepted proposals, or "
    "externally supplied actions in DE26-forced) <b>sequentially against live "
    "state</b>. Then a transfer on (i,j) mutates " + c("x_j") + " <i>before</i> a "
    "later transfer on (j,k) reads it, so " + c("x<super>n+1</super>_k") + " can "
    "depend on " + c("x<super>n</super>_i") + " &mdash; a <b>2-hop</b> influence in a single "
    "nominal tick (V2.7 &sect;6 measured +0.124 at distance 2 on a 0&rarr;1&rarr;2 "
    "chain, vs exactly 0 under frozen-state simultaneous application). Theorem 9.1 "
    "holds for <b>D0 only</b>; the DE family's causal speed per tick is bounded by "
    "the longest chain of transfers sharing cells in application order, not by 1.")

# ============================ 10. counterexamples ============================
h1("10. Counterexamples (necessity witnesses)")
cex("<b>Counterexample A (step above the bound increases V; tightness).</b> "
    "Pure-quadratic fixture with no flat band: " + c("L_i = U_i = L_j = U_j = 0") + ", "
    + c("&chi; = 0") + ", equal weights " + c("&alpha; = &beta; = w") + ", so "
    + c("v(x) = w x&sup2;") + " globally and " + c("L_V = 2w") + ". One edge, "
    + c("&eta; = 1, &theta; = 0") + ", state " + c("(d, &minus;d)") + ". Then "
    + c("f = 4wd, J = 4Mwd") + ", and exactly")
eq(r"V_{\mathrm{after}}=2wd^2\,(1-4Mw\,\Delta t)^2\ \Rightarrow\ "
   r"V_{\mathrm{after}}>V_{\mathrm{before}}\Longleftrightarrow \Delta t>\frac{1}{2Mw}")
cex("The Theorem 5.1 bound here is " + c("2/(2w&middot;M&middot;2) = 1/(2Mw)") + " "
    "&mdash; <b>exactly tight</b> on this fixture: any &Delta;t above it strictly "
    "increases V (e.g. w = M = 1, d = 1, &Delta;t = 0.6: V goes 2 &rarr; 3.92). "
    "Tightness is claimed for this fixture only; a positive-width viable band makes "
    "the bound merely sufficient (Conjecture 5.7).")
cex("<b>Counterexample B (sequential 3-cell over-propagation).</b> See Observation "
    "9.2: the 0&rarr;1&rarr;2 chain under sequential live-state application transmits "
    "a cell-0 perturbation to cell 2 within one nominal tick, exceeding the "
    "one-edge-per-tick propagation Theorem 9.1 proves for the synchronous law. This "
    "invalidates any attempt to extend Theorem 9.1 to the DE family unchanged.")
cex("<b>Counterexample C (drive increases V).</b> A single supplied cell c with "
    + c("v_c(x) = &beta;[x &minus; U]<sub>+</sub>&sup2;") + ", no active transport edges, "
    "initial state " + c("x<super>n</super>_c = U") + " (so " + c("&mu;_c = 0") + "), constant "
    "supply s &gt; 0. The D0 step gives "
    + c("V(x<super>n+1</super>) &minus; V(x<super>n</super>) = &beta;(&Delta;t s)&sup2; &gt; 0")
    + ". Driven V is not monotone in general (supports Non-result 6.3); only the "
    "conditional Corollary 6.2 survives.")
cex("<b>Counterexample D (the loss-blind force is wrong for &eta; &lt; 1).</b> Take "
    + c("&eta;_e = 0.5") + " and endpoint potentials " + c("&mu;_i = &minus;3, "
    "&mu;_j = &minus;4") + " (both cells in deficit, j more deficient). The "
    "<b>loss-blind</b> rule sees " + c("&mu;_i &minus; &mu;_j = 1 &gt; 0") + " and "
    "would transfer i &rarr; j. But the <b>true</b> loss-aware force is "
    + c("f_e = &minus;3 &minus; 0.5(&minus;4) = &minus;1 &lt; 0") + ": by Lemma 4.1 "
    "the first-order change from this edge is "
    + c("&minus;f_e(&Delta;tJ) = +&Delta;tJ &gt; 0") + " &mdash; the loss-blind "
    "transfer <b>increases</b> V, because at &eta; = 0.5 the efficiency loss wastes "
    "more than the deficit relief it buys. This criticism applies exactly to the "
    "members that <b>compute</b> a loss-blind proposal force &mdash; DE-core and the "
    "DE24-family &mdash; and is why D0 must use the loss-aware force. DE26-forced "
    "computes no force, so this particular criticism does not apply to it.")
cex("<b>Counterexample E (the former Lipschitz constant is too small).</b> A "
    "counterexample to the <i>former</i> constant "
    + c("2 max_i max(&alpha;,&beta;,&chi;)") + ", not to the corrected theorem. Take "
    + c("L = R = 0, &alpha; = &chi; = 1") + " (&beta; inactive), so for x &lt; 0: "
    + c("v(x) = 2x&sup2;, v''= 4") + ". One edge, " + c("&eta; = M = 1, &theta; = 0, "
    "&Delta;t = 0.4") + ", states " + c("(&minus;1, &minus;2)") + ". Then "
    + c("&mu; = (&minus;4, &minus;8), f = 4, J = 4") + ", the step maps "
    + c("(&minus;1, &minus;2) &rarr; (&minus;2.6, &minus;0.4)") + ", and V "
    "<b>increases</b>: 10 &rarr; 13.84. The former constant would read L = 2, whose "
    "one-edge bound &Delta;t &le; 0.5 <i>incorrectly permits</i> &Delta;t = 0.4; the "
    "corrected " + c("L_V = 2(&alpha; + &chi;) = 4") + " gives &Delta;t &le; 0.25 and "
    "correctly forbids it. This is exactly why " + c("L_V") + " must sum "
    "simultaneously-active weights (Assumption 2.5).")
P("<b>Effect on the theorems.</b> A, C, D confirm the <b>necessity</b> of "
  "(respectively) the step-size condition, the driven caveat, and the loss-aware "
  "force &mdash; they do not invalidate the corrected D0 results. E refutes only the "
  "former Lipschitz constant and motivates the corrected " + c("L_V") + ". B "
  "invalidates only the <i>extension</i> of the locality theorem to the sequential DE "
  "family, which is accordingly restricted to D0.")

# ============================ 11. scope ============================
h1("11. Exact scope and exclusions")
P("<b>The D0 theorems (4.4, 5.1, 5.2, 5.5, 5.6, 6.1, 8.1, 9.1) and Lemma 5.6a hold "
  "only for the synchronous, unconstrained, loss-aware, explicit-Euler law of "
  "Def 3.2.</b> Each mechanism below is <b>excluded</b>, with the framework its "
  "rigorous treatment will likely need:")
table([
    ["Excluded mechanism", "Likely framework"],
    ["clipping / projection at 0 and K", "projected dynamical systems / variational inequalities"],
    ["spill at K", "one-sided projection / complementarity"],
    ["unmet-demand saturation (min(d, &middot;))", "nonsmooth / Filippov / piecewise-smooth analysis"],
    ["hard-reserve constraints", "constrained optimisation (KKT) / barrier methods"],
    ["fixed activation cost c<sub>0</sub>", "hybrid / impulsive systems (discontinuous jumps)"],
    ["golden-section / coordinate line search (DE24-family line-sized rules)",
     "coordinate-descent theory (approximate 1-D minimisation); not proximal unless a proximal objective and proof are supplied"],
    ["sequential live-state transfers", "Gauss&ndash;Seidel operator splitting (vs Jacobi)"],
    ["horizon optimisation", "optimal control / dynamic programming"],
    ["global / instantaneous field solves", "elliptic PDE / implicit (nonlocal) solves"],
    ["ledger incentives, EBU issuance", "mechanism design &mdash; no dynamical-descent claim applies"],
], [7.2 * cm, 8.3 * cm])
P("Also excluded from D0 but present in the DE family and unaddressed here: "
  "<b>operator splitting</b> (drive N then transport A) and <b>&mu; frozen at "
  "N(x<super>n</super>)</b> rather than x<super>n</super>. These alone make D0 &ne; (any DE member) "
  "even before constraints; a Lie/Strang splitting-error analysis is the natural "
  "next tool.")

# ============================ 12. numerical validation ============================
h1("12. Numerical validation (NOT proof)")
P("The validation plan of the draft is implemented by " + c("test_v28.py") + " "
  "(standard library only; deterministic seed 20260726; a self-contained D0 reference "
  "implementation, deliberately independent of every engine module). It contains "
  "<b>132 checks in 11 groups</b>, including an independently validated symmetric "
  "Jacobi eigensolver (analytic fixtures, eigenpair residuals, PSD and convergence "
  "guards) for the spectral bounds, and <b>four negative controls</b> that must fail "
  "if a corrected constant or scope restriction is silently reverted:")
table([
    ["Group", "Validates"],
    ["1. marginals + curvature", "analytic &mu; vs central differences on every smooth interval; branchwise slope; corrected exact and safe L_V (18 checks)"],
    ["2. Counterexample E", "negative control: the former max-form constant permits a V-increasing step; corrected L_V forbids it (8)"],
    ["3. exact identities", "Lemma 4.1 and Lemma 4.2 on active/inactive, lossy/lossless, &theta; = 0 / &theta; &gt; 0 edges (11)"],
    ["4. remainder inequality", "|r_n| &le; R_n and the full (&#9733;) inequality, driven and undriven, cross terms, overlapping curvature (22)"],
    ["5. one-edge bound + CE-A", "144 deterministic sweep combos below the bound; exact tightness of the CE-A threshold (9)"],
    ["6. spectral bound", "Jacobi eigensolver validation; Gershgorin bound; descent at 0.95x the graph bound on seeded random graphs (19)"],
    ["7. active-set + state-specific", "Theorems 5.5/5.6; Lemma 5.6a (J &ne; 0 &rArr; SJ &ne; 0); J = 0 leaves the state exactly unchanged (22)"],
    ["8. Counterexample D", "negative control: executing the loss-blind transfer increases V; the D0 flux correctly stays zero (6)"],
    ["9. stock/loss ledger", "Theorem 8.1 to machine precision, lossless/lossy/mixed with drive (6)"],
    ["10. locality", "one-hop dependency under D0; negative control: a sequential live-state tick leaks to distance 2 (4)"],
    ["11. O(&Delta;t&sup2;) scaling", "halving sequence: remainder bound holds; |r_n|/&Delta;t&sup2; bounded; ~4x shrinkage per halving (7)"],
], [4.6 * cm, 10.9 * cm])
P("Maximum residuals observed in the release run: "
  + c("max(|r_n| &minus; R_n) = 2.4&times;10<super>&minus;15</super>") + " and max descent "
  "margin " + c("7.1&times;10<super>&minus;15</super>") + " (both pure floating-point "
  "roundoff at the exact-equality fixtures), max exact-identity residual "
  + c("7.1&times;10<super>&minus;15</super>") + ", max eigenpair residual "
  + c("1.8&times;10<super>&minus;13</super>") + ". The captured run is archived in "
  + c("results/v2.8/v28_validation.txt") + ". <b>None of this is a proof</b>: the "
  "checks validate implementation consistency at the tested points only.")

# ============================ 13. open problems ============================
h1("13. Unresolved conjectures and proof gaps")
P("1. <b>Conjecture 5.7 (tightness)</b> &mdash; whether the active-set (5.5) or "
  "state-specific (5.6) sufficient bound is the tight admissible &Delta;t is open; "
  "only the pure-quadratic one-edge case (Counterexample A) is settled.")
P("2. <b>Driven global behaviour</b> &mdash; Corollary 6.2 is a one-step condition; "
  "multi-step boundedness/convergence under persistent drive (a discrete analogue of "
  "the coercive sublevel-set / LaSalle argument of V2.7 Cor 7.2) is <b>open</b>.")
P("3. <b>Splitting error (D0 &rarr; DE family, step 1)</b> &mdash; bound the "
  "discrepancy from the engine's A(N(&middot;)) splitting with &mu; at N(x<super>n</super>) via "
  "Lie/Strang splitting analysis. <b>Open.</b>")
P("4. <b>Loss-blind engine force</b> &mdash; DE-core and the DE24-family compute the "
  "loss-blind proposal force; characterise the set of states on which this is "
  "(non-)descending under &eta; &lt; 1 (Counterexample D is one witness). DE26-forced "
  "computes no force and is outside this item. <b>Open.</b>")
P("5. <b>Constrained descent</b> &mdash; a projected-dynamics analogue of Theorem 4.4 "
  "admitting clipping/spill/reserve while retaining a dissipation inequality. "
  "<b>Open.</b>")
P("6. <b>&theta; and the flat viable band</b> &mdash; the bounds drop the "
  "&theta;_e J_e term and ignore the flat (v'' = 0) interior; a curvature-aware, "
  "band-aware bound would be less conservative. <b>Open.</b>")

# ============================ 14. plain language ============================
h1("14. Plain-language interpretation")
P("Think of V as a 'stress score' for the whole grid and &mu;_i as the local pressure "
  "at cell i. Moving resource down a pressure gradient lowers stress &mdash; but "
  "along a lossy pipe only a fraction &eta; arrives, so the <i>right</i> pressure "
  "difference to act on is " + c("&mu;_i &minus; &eta;&mu;_j") + ", <b>not</b> "
  + c("&mu;_i &minus; &mu;_j") + ". Use the naive difference and you can 'help' a "
  "starving neighbour while wasting so much in transit that the grid is worse off "
  "(Counterexample D).")
P("In continuous time (V2.7) stress falls at a rate equal to how hard the drive "
  "pushes minus how much the pipes dissipate. In discrete ticks you also pay a "
  "<b>step-size penalty</b>: take too big a step and you overshoot and <i>increase</i> "
  "stress (Counterexample A) &mdash; exactly like too large a learning rate in "
  "gradient descent. For one pipe the safe step is "
  + c("&Delta;t &le; 2/(L_V M(1+&eta;&sup2;))") + "; for a network it is governed by "
  "a spectral norm of the pipe layout. Physical <i>stock</i> is a separate ledger: "
  "transport never destroys resource mysteriously &mdash; whatever doesn't arrive is "
  "the named efficiency loss (1 &minus; &eta;).")
P("Two honest caveats. First, if the outside world keeps pumping resource in "
  "(drive), the score need not fall every tick; we can only say when dissipation "
  "beats drive plus the step penalty. Second &mdash; and most important &mdash; this "
  "all concerns the <b>idealised synchronous law (D0)</b>. The <b>real engine family "
  "(DE)</b> applies drive and transport in two ordered passes, moves resource one "
  "transfer at a time against a changing state (which can carry information two "
  "cells in a single tick), uses the naive loss-blind force wherever it computes a "
  "force at all (DE-core and the DE24-family; the forced harness DE26-forced just "
  "executes given actions), and clamps values to a physical range. <b>Proving D0 is "
  "a first brick, not the building: the engine's own guarantees still have to be "
  "earned separately.</b>")
gap(8)
from reportlab.platypus import KeepTogether
S.append(KeepTogether([
    HRFlowable(width="100%", color=colors.HexColor("#C6D2DE"), thickness=0.6),
    Spacer(1, 6),
    Paragraph("<i>This note has not been peer reviewed. All theorems are proof "
              "attempts awaiting independent expert review; the numerical suite "
              "validates them at tested points only and proves nothing. No "
              "production engine, physics, or EBU-accounting behaviour is "
              "introduced or changed by V2.8.</i>", THM),
]))

# ============================ build ============================
doc = SimpleDocTemplate(OUT, pagesize=A4,
                        leftMargin=2.2 * cm, rightMargin=2.2 * cm,
                        topMargin=2.0 * cm, bottomMargin=2.0 * cm,
                        title="EBU Foundation V2.8 (discrete mathematics)",
                        author="Konrad Grzyb")
doc.build(S)
print(f"wrote {OUT}  ({_eqn[0]} typeset equations)")
