"""
Generate the V2.7 mathematical foundation PDF:
  Foundation_v2.7_math.pdf

Content mirrors Foundation_v2.7_math.md. Equations are TYPESET (not monospaced):
each display equation is rendered with matplotlib's mathtext engine to a PNG and
embedded in the reportlab flow (no external LaTeX toolchain is required or available).

Run with the project venv:  venv/bin/python make_paper_v27_math.py

This is a documentation build only. It does NOT touch the physics or EBU engine.
"""
from __future__ import annotations
import io
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
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Preformatted,
                                Image, Table, TableStyle, PageBreak, HRFlowable)

OUT = "Foundation_v2.7_math.pdf"
EQ_DPI = 220
EQ_DIR = tempfile.mkdtemp(prefix="v27eq_")
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
CAP = ParagraphStyle("CAP", parent=BODY, fontSize=8.5, alignment=TA_CENTER,
                     textColor=colors.HexColor("#555555"), spaceBefore=2, spaceAfter=10)
CELL = ParagraphStyle("CELL", parent=BODY, fontSize=8.3, leading=10.4, spaceAfter=0, alignment=TA_LEFT)
CELLH = ParagraphStyle("CELLH", parent=CELL, textColor=colors.white, fontName="Helvetica-Bold")

S = []
def P(t): S.append(Paragraph(t, BODY))
def h1(t): S.append(Paragraph(t, H1))
def h2(t): S.append(Paragraph(t, H2))
def thm(t): S.append(Paragraph(t, THM))
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


# ============================ title ============================
S.append(Spacer(1, 3 * cm))
S.append(Paragraph("The Energy Balance Project", TITLE)); gap(6)
S.append(Paragraph("Mathematical Foundation Note &mdash; Version 2.7", SUB))
S.append(Paragraph("Variational derivation of the local actor law, "
                   "and a continuous-time energy&ndash;dissipation theorem", SUB))
gap(16)
S.append(HRFlowable(width="60%", color=colors.HexColor("#1F3A5F"), thickness=1)); gap(16)
P("<b>Status: mathematical specification only. No change is made to the physical "
  "engine or the EBU accounting implementation.</b> Claims are labelled by epistemic "
  "status (Theorem / Proof sketch / Numerical observation / Regression check / "
  "Conjecture). The companion <font face='Courier'>test_math.py</font> (8 groups, 34 "
  "numerical regression checks) <i>validates</i> the derivations at tested points; a "
  "passing run is not a proof, and the check count is not a count of theorems.")
P("This PDF is generated from <font face='Courier'>Foundation_v2.7_math.md</font> by "
  "<font face='Courier'>make_paper_v27_math.py</font>; equations are typeset with the "
  "matplotlib mathtext engine.")
S.append(PageBreak())

# ============================ 1. dynamics ============================
h1("1. Two clearly separated models")
h2("1.1 Model D &mdash; the discrete map the engine runs")
P("State <font face='Courier'>x = (x_i)</font>, <font face='Courier'>x_i &isin; [0, K_i]</font>, "
  "on a lattice with von Neumann neighbourhood. One tick is the composition "
  "<font face='Courier'>T = A(N(x))</font> (apply N then A) of an on-site natural map and "
  "an actor transport map. The homeostatic penalty and its marginal:")
eq(r"\ell_i(x)=\alpha_i\,[\,L_i-x\,]_+^2+\beta_i\,[\,x-U_i\,]_+^2,\qquad "
   r"\mu_i=\ell_i'(x)=-2\alpha_i(L_i-x)_+ + 2\beta_i(x-U_i)_+")
P("Natural map (order: inflow, regeneration, demand, leak, clip to "
  "<font face='Courier'>[0,K_i]</font>):")
eq(r"(Nx)_i=\Pi_i\!\left(x_i+s_i+g_i(x_i)-d_i-\lambda_i-\kappa_i x_i\right)")
P("Actor map on <font face='Courier'>y = Nx</font>: each actor picks the steepest "
  "feasible out-edge by the engine force, then sizes the transfer by the raw flux "
  "(<i>gradient</i> mode) or the line search (<i>safe</i> mode); accepted transfers are "
  "applied <b>sequentially</b> against the live state (load-bearing for &sect;6):")
eq(r"F_{ij}=\mu_i-\mu_j-\theta\qquad "
   r"q_{\mathrm{safe}}=\mathrm{arg\,min}_{\,0\leq q\leq q_{hi}}\;[\,\ell_i(y_i-q)+\ell_j(y_j+\eta q)\,]")
h2("1.2 Model C &mdash; continuous-time approximation (labelled as such)")
P("Reading Model D as forward Euler with <font face='Courier'>&Delta;t = 1</font>, the "
  "<font face='Courier'>&Delta;t &rarr; 0</font> limit is")
eq(r"\dot x_i=s_i+g_i(x_i)-d_i-\lambda_i-\kappa_i x_i+\sum_{j\in N(i)}"
   r"(\eta_{ji}J_{ji}-J_{ij})")
P("Model C is an approximation, not the engine. The flip bifurcation (&sect;3) and "
  "transport overshoot (&sect;5) are <font face='Courier'>&Delta;t = 1</font> artifacts "
  "absent from Model C; engine-behaviour results use Model D.")

# ============================ 2. functional & law ============================
h1("2. State functional, dissipation potential, derived law")
P("Keep the <b>state</b> functional separate from transport <b>dissipation</b>; only "
  "the state functional takes cell-state arguments. Transport is not placed inside a "
  "state functional (no edge-state variable exists).")
eq(r"V_{\mathrm{state}}(x)=B_{\mathrm{hom}}+B_{\mathrm{reg}}"
   r"=\sum_i\ell_i(x_i)+\sum_{i:\rho_i>0,A_i>0}\chi_i\,[\,R_i-x_i\,]_+^2,\quad R_i=A_i+\delta_i")
eq(r"\Psi(J)=\sum_{e\in E}[\frac{J_e^2}{2M_e}+\theta_e J_e],\qquad J_e\geq 0")
P("Local chemical potential (state marginal), on-site by construction:")
eq(r"\mu_i^{\mathrm{tot}}=\frac{\partial V_{\mathrm{state}}}{\partial x_i}"
   r"=\ell_i'(x_i)+r_i'(x_i),\qquad r_i'(x)=-2\chi_i(R_i-x)\ \ (x<R_i)")
P("For a directed edge <font face='Courier'>e=(i&rarr;j)</font> a flux removes "
  "<font face='Courier'>J_e</font> from i and deposits <font face='Courier'>&eta;_e J_e</font> "
  "at j (lossy continuity). Hence the &eta;-weighted thermodynamic force and the "
  "Onsager/gradient-flow flux:")
eq(r"\frac{dV_{\mathrm{state}}}{dt}=-\sum_e J_e\,f_e,\quad f_e:=\mu_i^{\mathrm{tot}}-\eta_e\mu_j^{\mathrm{tot}};"
   r"\qquad J_e=M_e\,[\,f_e-\theta_e\,]_+")
thm("<b>Derived local law.</b> Edge force "
    "<font face='Courier'>F_e = &mu;_i^tot &minus; &eta;_e &mu;_j^tot &minus; &theta;_e</font>. "
    "It reads only <font face='Courier'>x_i</font>, adjacent <font face='Courier'>x_j</font>, and "
    "cell/edge-local constants. The engine force "
    "<font face='Courier'>&mu;_i &minus; &mu;_j &minus; &theta;</font> matches it <b>only when "
    "&eta;_e = 1 and &chi; = 0</b>; for &eta;_e &lt; 1 the two differ by "
    "<font face='Courier'>(1&minus;&eta;_e)&mu;_j</font>.")
h2("2.1 Three distinct laws (do not conflate)")
P("<b>(1) Continuous Onsager law:</b>")
eq(r"J_e=M_e\,[\,f_e-\theta_e\,]_+")
P("<b>(2) Raw discrete explicit-Euler rule:</b>")
eq(r"q_e=\Delta t\,M_e\,[\,f_e-\theta_e\,]_+")
P("<b>(3) Current safe rule (gated coordinate descent):</b>")
eq(r"q_e^{*}=\mathrm{arg\,min}_{\,0\leq q\leq q_{hi}}\;V_{\mathrm{state}}(x+S_e q)")
P("Law (3) minimises the <i>state functional</i> along the edge; it <b>excludes</b> the "
  "linear cost <font face='Courier'>&theta;_e q</font> and the quadratic dissipation "
  "<font face='Courier'>q&sup2;/(2M_e)</font> of the Onsager objective (&theta; enters (3) "
  "only via edge eligibility; M not at all). So (3) is <b>gated coordinate descent, not "
  "the Onsager flux</b> &mdash; different from (1)/(2) even at &eta; = 1.")

# ============================ 3. logistic ============================
h1("3. Logistic harvest &mdash; existence is not sustainability")
P("Isolated logistic source with constant net harvest h; interior of Model D:")
eq(r"h^\ast=\frac{\rho K}{4},\quad D=1-\frac{4h}{\rho K},\quad "
   r"x_\pm(h)=\frac{K}{2}(1\pm\sqrt{D}),\quad \varphi'(x_\pm)=1\mp\rho\sqrt{D}")
thm("<b>Theorem 3 (corrected).</b> <font face='Courier'>h &le; &rho;K/4</font> gives "
    "<i>existence</i> of equilibria, not sustainability. Persistence needs all three: "
    "(i) <font face='Courier'>h &le; &rho;K/4</font>; (ii) basin "
    "<font face='Courier'>x(0) &gt; x_&minus;(h)</font> (the always-unstable lower root is "
    "the collapse threshold); (iii) discrete stability "
    "<font face='Courier'>&rho;&radic;D &lt; 2</font> (else a flip/period-doubling "
    "bifurcation, equilibrium not attracting).")
P("<i>Numerical observation</i> (&rho;=0.4, K=20): equilibrium matches "
  "<font face='Courier'>x_+(h)</font> to 4 dp; start just below "
  "<font face='Courier'>x_&minus;</font> collapses; &rho;=2.6 (&rho;&radic;D=2.18) gives a "
  "sustained 2-cycle.")

# ============================ 4. Allee ============================
h1("4. Allee reserve under driving &mdash; the reserve is not x = A")
P("For the isolated <i>undriven</i> Allee source the basin boundary is "
  "<font face='Courier'>x = A</font>. Under drive it becomes the unstable middle root "
  "<font face='Courier'>x_r</font> of")
eq(r"G(x)=\rho x(1-\frac{x}{K})(\frac{x}{A}-1)+s-d-\lambda-\kappa x-h=0")
eq(r"\frac{\partial x_r}{\partial h}=\frac{\partial x_r}{\partial d}"
   r"=\frac{\partial x_r}{\partial \lambda}=\frac{1}{G'(x_r)}>0,\qquad "
   r"\frac{\partial x_r}{\partial \kappa}=\frac{x_r}{G'(x_r)}>0,\qquad "
   r"\frac{\partial x_r}{\partial s}=-\frac{1}{G'(x_r)}<0")
P("Harvest, demand and leakage <b>raise</b> the reserve; supply <b>lowers</b> it; "
  "transport out acts as harvest, transport in as supply. <i>Verified</i> "
  "(&rho;=0.6, K=20, A=5): h=0.5&rarr;5.99, &kappa;=0.05&rarr;5.58 (both &gt;A); "
  "s=0.5&rarr;3.58 (&lt;A).")

# ============================ 5. descent ============================
h1("5. Descent condition &mdash; corrected for loss and curvature")
P("Along the lossy transfer, the pair burden "
  "<font face='Courier'>&psi;(q)=&ell;_i(y_i&minus;q)+&ell;_j(y_j+&eta;q)</font> is convex. In "
  "the operating branch (source in excess, destination in deficit):")
eq(r"\psi''=2\,(\beta_{\mathrm{src}}+\eta^2\alpha_{\mathrm{dst}})\qquad\Longrightarrow\qquad "
   r"M\leq \frac{1}{\max(\alpha_i,\beta_i)+\eta^2\max(\alpha_j,\beta_j)}")
P("The loss enters as &eta;&sup2; on the destination (earlier <font face='Courier'>2(&alpha;+&beta;)"
  "</font> was the &eta;=1 case). For symmetric weights the bound is tight: "
  "<font face='Courier'>M &le; 1/(w(1+&eta;&sup2;))</font>. This governs the <b>raw</b> rule "
  "(2) only; the safe line search (3) has no mobility bound (size set by "
  "<font face='Courier'>q_hi</font> and the acceptance gate).")
P("<i>Validation</i>: symmetric weights hit the bound exactly "
  "(e.g. w=1,&eta;=0.9 &rarr; 0.5525); asymmetric weights make it conservative (safe).")

# ============================ 6. causality ============================
h1("6. Finite causal speed &mdash; corrected for sequential execution")
thm("<b>Theorem 6.1.</b> <i>If</i> all edge fluxes are computed from the frozen state "
    "<font face='Courier'>y = Nx</font> and applied <b>simultaneously</b>, then "
    "<font face='Courier'>x_i(t+n)</font> depends only on cells within graph distance n: "
    "causal speed &le; 1 cell/tick. <i>Validated</i>: frozen-state leak = 0.")
P("<b>Observation 6.2:</b> the current engine freezes proposal <i>directions</i> but "
  "applies accepted transfers <b>sequentially</b> against live state, so a chain "
  "0&rarr;1&rarr;2 lets a perturbation at cell 0 reach cell 2 in one tick (measured "
  "+0.124). We adopt the honest weakened statement for the current engine (&le; 1 edge "
  "per micro-step; per tick bounded by the longest accepted-transfer chain) and record "
  "strict one-hop (frozen-state simultaneous update) as the target discipline. No engine "
  "change is made.")

# ============================ 7. verdict + theorem ============================
h1("7. Verdict: A, B_raw, B_safe, and discretisation (C)")
P("<b>A</b> &mdash; derived Onsager flux "
  "<font face='Courier'>J_e = M_e[&mu;_i^tot &minus; &eta;_e &mu;_j^tot &minus; &theta;_e]_+</font>. "
  "<b>B_raw</b> &mdash; engine raw rule (loss-blind direction, size "
  "<font face='Courier'>M[F]_+</font>, &chi;=0 default, sequential). "
  "<b>B_safe</b> &mdash; engine safe rule (same direction, size "
  "<font face='Courier'>argmin V_state</font>, sequential).")
thm("<b>C &mdash; when B_raw is the forward-Euler discretisation of A.</b> This is a "
    "statement about the <i>scheme</i>, not the trajectories: even under all conditions "
    "the finite-&Delta;t discrete trajectory is <b>not</b> identical to the continuous "
    "flow of A &mdash; forward Euler has local truncation error "
    "<font face='Courier'>O(&Delta;t&sup2;)</font> (global "
    "<font face='Courier'>O(&Delta;t)</font>), and the engine runs at &Delta;t = 1. "
    "Conditions: (1) &eta;_e = 1; (2) &chi; = 0 on active edges; (3) "
    "<b>c0 = 0</b> (a fixed activation cost is a discrete jump &rarr; hybrid); (4) no "
    "overlapping sequential transfers; (5) mobility bound (&sect;5).")
thm("<b>A &ne; B_safe in general</b>, even at &eta;=1, &chi;=0, c0=0, single transfer: "
    "B_safe minimises the state functional (exact minimiser), not the linear flux "
    "<font face='Courier'>M_e F_e</font>. It is a different (coordinate-descent) law.")

h2("7.1 C-1 promoted: continuous-time energy&ndash;dissipation theorem")
thm("<b>Theorem 7.1.</b> Assume continuous time (Model C); "
    "<font face='Courier'>c0 = 0</font>; fixed graph; local lossy continuity with "
    "<font face='Courier'>&eta;_e &isin; (0,1]</font>; Onsager flux. Each penalty is "
    "C&sup1;, so <font face='Courier'>V_state &isin; C&sup1;</font> and the RHS is <b>locally "
    "Lipschitz</b> (the regeneration terms are polynomial, not globally Lipschitz on "
    "R<super>n</super>), giving a unique C&sup1; solution locally in time. Global "
    "forward existence is not asserted in general; for the undriven case it follows from "
    "Corollary 7.2 via a compact invariant sublevel set. With drive "
    "<font face='Courier'>u_i = s_i + g_i(x_i) &minus; d_i &minus; &lambda;_i &minus; "
    "&kappa;_i x_i</font>:")
eq(r"\frac{dV_{\mathrm{state}}}{dt}=\sum_i\mu_i u_i-\sum_e[\frac{J_e^2}{M_e}+\theta_e J_e]"
   r"\ \leq\ \sum_i\mu_i u_i")
P("<b>Proof.</b> Continuity gives "
  "<font face='Courier'>dx_i/dt = u_i + &Sigma; incoming &eta;J &minus; &Sigma; outgoing J</font>. "
  "By the chain rule "
  "<font face='Courier'>dV/dt = &Sigma;_i &mu;_i (dx_i/dt) = &Sigma;_i &mu;_i u_i + T</font>. "
  "Reorganising T by edge, edge (i&rarr;j) contributes "
  "<font face='Courier'>&minus;J_e(&mu;_i &minus; &eta;_e &mu;_j) = &minus;J_e f_e</font>, so "
  "<font face='Courier'>T = &minus;&Sigma;_e f_e J_e</font>. On an active edge "
  "<font face='Courier'>J_e = M_e(f_e &minus; &theta;_e)</font>, hence "
  "<font face='Courier'>f_e J_e = J_e&sup2;/M_e + &theta;_e J_e</font>; on an inactive edge "
  "both sides vanish. Summing gives the identity; dropping the non-negative dissipation "
  "gives the inequality. &#9633;")
thm("<b>Excluded engine mechanisms (scope of Theorem 7.1).</b> The theorem covers the "
    "smooth, unconstrained, continuous-time flow only. It does <b>not</b> cover, and each "
    "needs its own nonsmooth / projected / hybrid / discrete analysis: clipping/projection "
    "at 0 and K; spill at K; unmet-demand saturation; hard-reserve constraints; the fixed "
    "activation cost c0; sequential live-state transfers (&sect;6); and finite-step "
    "(&Delta;t = 1) updates (an O(&Delta;t&sup2;) remainder).")
thm("<b>Corollary 7.2 (undriven case &mdash; LaSalle via a coercive sublevel set).</b> "
    "Assume <font face='Courier'>u_i &equiv; 0</font> and that V_state is <b>coercive</b> "
    "(<font face='Courier'>||x|| &rarr; &infin; &rArr; V_state &rarr; &infin;</font>). "
    "Coercivity is an <i>explicit assumption</i>, not a model property: the weights "
    "<font face='Courier'>&alpha;_i, &beta;_i</font> may be zero for some cells, leaving "
    "V_state flat in some direction. A <i>sufficient</i> example is "
    "<font face='Courier'>&alpha;_i &gt; 0</font> and <font face='Courier'>&beta;_i &gt; 0</font> "
    "for every cell (each coordinate penalised in both directions); we assume coercivity "
    "directly rather than impose this on the engine.")
thm("Then: (i) by Theorem 7.1 <font face='Courier'>dV_state/dt &le; 0</font>; (ii) hence "
    "<font face='Courier'>V_state(x(t)) &le; V_state(x(0))</font>, so the trajectory stays "
    "in the sublevel set <font face='Courier'>&Omega;_0 = { x : V_state(x) &le; V_state(x(0)) }</font>; "
    "(iii) V_state continuous and coercive makes <font face='Courier'>&Omega;_0</font> "
    "<b>compact</b>, and V_state non-increasing makes it <b>positively invariant</b>; "
    "(iv) the vector field is <b>locally Lipschitz</b> and the solution stays in the "
    "compact <font face='Courier'>&Omega;_0</font>, so it extends <b>globally</b> forward "
    "(no finite-time escape); (v) LaSalle then gives convergence to the <b>largest "
    "invariant subset</b> of "
    "<font face='Courier'>Z = { J_e = 0 &forall;e } = { f_e &le; &theta;_e &forall;e }</font> "
    "(with <font face='Courier'>u &equiv; 0</font> every point of Z is an equilibrium, so Z "
    "is invariant).")
thm("<b>Retained limitations.</b> This does <b>not</b> prove V_state = 0, complete "
    "homeostasis, a unique equilibrium, or that the physical interval "
    "<font face='Courier'>[0,K]</font> is positively invariant &mdash; Theorem 7.1 excludes "
    "clipping/projection at 0 and K, so invariance of <font face='Courier'>[0,K]</font> is "
    "not established by the unconstrained flow. The reached point of Z may depend on the "
    "initial condition; boundedness comes from the coercive sublevel set "
    "<font face='Courier'>&Omega;_0</font>, not from the physical bounds.")
P("<i>Numerical validation of Theorem 7.1</i>: fine-&Delta;t integration matched the "
  "identity to O(&Delta;t) (max residual 6.2&times;10<super>-5</super> at &Delta;t=10<super>-4</super>); "
  "dV/dt turned positive once the drive exceeded the dissipation, consistent with the "
  "inequality biting only when the drive is non-positive.")

# ============================ 8. conjectures + validation ============================
h1("8. Open conjectures and regression validation")
P("<b>Conjecture C-1&prime; (discrete driven bound).</b> A discrete counterpart of the "
  "identity holds for B_raw under the mobility bound: "
  "<font face='Courier'>V(x_{t+1}) &minus; V(x_t) &le; &Sigma;_i &mu;_i u_i &minus; D_t</font> "
  "with <font face='Courier'>D_t &ge; 0</font> (the continuous case is now Theorem 7.1; the "
  "discrete case remains open pending the step-size remainder and the &sect;6 "
  "sequential-execution caveat).")
P("<b>Conjecture C-2 (reserve surrogate).</b> V2.4's constant "
  "<font face='Courier'>R_i = A_i + &delta;_i</font> dominates the driven reserve "
  "<font face='Courier'>x_r</font> (hence is safe) iff "
  "<font face='Courier'>&delta;_i &ge; x_r &minus; A_i</font> over the operating envelope.")
gap(4)
P("<b>Regression validation.</b> <font face='Courier'>test_math.py</font> contains 8 "
  "groups holding 34 numerical regression checks. The check count is a harness detail, "
  "not a count of theorems; a passing run validates the tested points only.")
table([
    ["Group", "Guards"],
    ["1. fold &amp; basin", "equilibrium = x_+(h); basin straddle of x_&minus;(h) (Thm 3)"],
    ["2. flip", "2-cycle appears once &rho;&radic;D &gt; 2 (Thm 3)"],
    ["3. driven reserve", "middle root moves in the signed directions (Thm 4)"],
    ["4. descent bound", "M &le; 1/[max(&alpha;,&beta;)_i + &eta;&sup2;max(&alpha;,&beta;)_j] safe; tight if symmetric"],
    ["5. force gap", "engine vs derived force coincide iff &eta; = 1"],
    ["6. causality", "sequential leak &gt; 0; frozen-state simultaneous leak = 0"],
    ["7. energy identity", "dV/dt identity residual is O(&Delta;t) (Thm 7.1)"],
    ["8. three-law split", "q_safe &ne; M&middot;F even at &eta;=1, &theta;=0"],
], [4.2 * cm, 11.3 * cm])
P("<b>Corrections applied in this note</b> (relative to the first informal draft): "
  "logistic existence &ne; sustainability; the Allee reserve shifts off A under drive; "
  "the descent bound carries an &eta;&sup2; loss factor and uses the max-over-branch "
  "curvature; the derived force is loss-weighted (&mu;_i &minus; &eta;&mu;_j &minus; "
  "&theta;); transport is a dissipation potential, not a state term; one-hop causality "
  "holds only under frozen-state simultaneous updates; the engine splits into B_raw and "
  "B_safe; and C-1 is now a continuous-time theorem.")

# ============================ build ============================
doc = SimpleDocTemplate(OUT, pagesize=A4,
                        leftMargin=2.2 * cm, rightMargin=2.2 * cm,
                        topMargin=2.0 * cm, bottomMargin=2.0 * cm,
                        title="EBU Foundation V2.7 (mathematics)",
                        author="Konrad Grzyb")
doc.build(S)
print(f"wrote {OUT}  ({_eqn[0]} typeset equations)")
