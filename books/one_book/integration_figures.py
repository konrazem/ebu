"""Deterministic vector schematics for Book 1; no model, sampling, or RNG.

Run with the existing book-artifact environment (ReportLab). The established
build_book.py remains the PDF build entry point. These figures are explanatory
relationships, not scientific data or generated outcomes.
"""
from pathlib import Path
from math import atan2, cos, sin
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, white
from reportlab.pdfbase.pdfmetrics import stringWidth

OUT = Path(__file__).resolve().parent / 'figures'
NAVY = HexColor('#123F56'); TEAL = HexColor('#008C8C')
PALE = HexColor('#EDF5F5'); GREY = HexColor('#627786')

def start(name, height):
    c = canvas.Canvas(str(OUT / (name + '.pdf')), pagesize=(360, height), invariant=1)
    c.setTitle('EBU Book 1: ' + name.replace('_', ' '))
    c.setAuthor('Energy Balance Project')
    return c

def label(c, x, y, text, size=9, color=NAVY, bold=False):
    c.setFillColor(color); c.setFont('Helvetica-Bold' if bold else 'Helvetica', size)
    c.drawString(x, y, text)

def box(c, x, y, w, h, title, lines, color=TEAL):
    c.setFillColor(PALE); c.setStrokeColor(color); c.setLineWidth(.7)
    c.roundRect(x, y, w, h, 4, fill=1, stroke=1)
    assert stringWidth(title, 'Helvetica-Bold', 9) <= w-14, title
    label(c, x+7, y+h-15, title, 9, color, True)
    for i, line in enumerate(lines):
        assert stringWidth(line, 'Helvetica', 8) <= w-14, line
        label(c, x+7, y+h-29-11*i, line, 8)

def arrow(c, x1,y1,x2,y2, color=NAVY):
    c.setStrokeColor(color); c.setLineWidth(.9); c.line(x1,y1,x2,y2)
    a=atan2(y2-y1,x2-x1)
    for s in (-1,1):
        c.line(x2,y2,x2-5*cos(a)+s*2.5*sin(a),y2-5*sin(a)-s*2.5*cos(a))

c=start('continuity_chain',452)
box(c,7,386,216,57,'STATE AND FIXED POTENTIAL', ['Complete represented state x', 'One declared, single-valued V'])
box(c,7,307,216,59,'FINITE ENDPOINT VALUE', ['E = V(before) - V(after)', 'Regular path: E = negative integral of dV'])
arrow(c,115,386,115,368)
box(c,239,310,114,104,'GENERATOR', ['Declared generator', 'Unique admissible flow', 'Duration and controls', 'supply endpoints'], GREY)
arrow(c,239,337,225,337, GREY)
box(c,7,230,120,57,'SEQUENTIAL HISTORY', ['Joined state boundaries', 'Receipts telescope'])
box(c,141,230,212,57,'COMPLETE COALITION TABLE', ['One field and comparison protocol', 'Every required subset has an endpoint'])
arrow(c,73,307,67,289)
arrow(c,197,307,247,289)
box(c,7,153,346,57,'INTERACTION AND EXACT DISCRETE TAYLOR', ['Alternating differences = Mobius coefficients', 'Recursion; unique multilinear reconstruction without remainder'])
arrow(c,247,230,180,212)
box(c,7,76,346,57,'CANONICAL DENSITY: ADDITIONAL ASSUMPTIONS', ['Positive p = exp(-V) / Z in one fixed reference measure', 'EBU and its interactions become log-density contrasts'])
arrow(c,180,153,180,135)
box(c,7,0,346,56,'P4 ENTROPY: NARROWER PHYSICAL SCOPE', ['Fixed conservative single-reservoir equilibrium; no omitted work', 'Medium entropy change = k_B E; system change = -k_B E'])
arrow(c,180,76,180,58)
c.save()

c=start('interaction_origins',290)
box(c,5,218,166,66,'POTENTIAL V(x)', ['State geometry', 'Curvature and higher derivatives'])
box(c,189,218,166,66,'RESPONSE x(z)', ['Action-to-state mechanism', 'Mixed control dependence'])
arrow(c,88,218,139,193);arrow(c,272,218,221,193)
box(c,56,127,248,65,'COMPOSITE G(z) = V(x(z))', ['Smooth chain rule combines both sources.', 'Finite interaction belongs to this composite.'])
arrow(c,180,127,180,105)
box(c,5,36,350,68,'WHAT THE ENDPOINT TABLE IDENTIFIES', ['The total coefficient: m_E(T) = - Delta_T G(0)', 'A unique multilinear representation on the Boolean cube', 'The origin split also uses the declared smooth response.'])
label(c,13,12,'Quadratic V + nonlinear response can have higher-order interaction.',8)
c.save()

c=start('recursion',306)
box(c,5,228,169,69,'PAIR WITHOUT C', ['E(AB) - E(A) - E(B) + E(empty)', 'Same pair; C absent'])
box(c,186,228,169,69,'PAIR WITH C', ['E(ABC) - E(AC) - E(BC) + E(C)', 'Same pair; C present'])
arrow(c,89,228,146,191);arrow(c,271,228,214,191)
box(c,42,119,276,71,'TRIPLE = CHANGE IN THE PAIR', ['Pair with C minus pair without C', 'm_E(ABC) = I(AB | C) - I(AB | empty)', 'Lower-order terms are subtracted before naming the remainder.'])
arrow(c,180,119,180,94)
box(c,20,18,320,74,'FOURTH ORDER = CHANGE IN THE TRIPLE', ['Compare the same triple with and without D.', 'Continue recursively for higher orders.', 'One complete, common-baseline table throughout.'])
c.save()

c=start('generator_bridge',332)
box(c,7,268,346,58,'DECLARE THE RESPONSE', ['Initial state, controls, background and physical boundary', 'One well-posed generator; one evaluation horizon'])
arrow(c,180,268,180,247)
box(c,7,181,213,65,'COMPLETE ENDPOINTS', ['A trajectory for each coalition', 'Include pending stock and valued sinks', 'Retain the no-action background'])
box(c,234,181,119,65,'TEMPORAL MODES', ['Rates and eigenvalues', 'Decay and oscillation', 'Timing of the response'],GREY)
arrow(c,266,268,293,248,GREY)
arrow(c,114,181,114,160)
box(c,7,99,346,59,'ONE FINITE COMPARISON', ['E(S) = V(initial) - V(endpoint of S)', 'Relative table: subtract the common no-action change'])
arrow(c,180,99,180,78)
box(c,7,8,346,68,'COALITION INTERACTION', ['Apply the same Mobius differences to endpoint values.', 'Common linear response + quadratic V: no orders above pairs.', 'Temporal modes do not determine coalition order.'])
c.save()

c=start('feedback_memory',295)
box(c,7,209,102,67,'SOURCE', ['Maintained supply', 'Dispatch D', 'Shortage signal'])
box(c,128,209,104,67,'PENDING Q', ['Already dispatched', 'Arrival A = Q / tau'])
box(c,251,209,102,67,'RECEIVER X', ['Usable stock', 'Consumption h'])
arrow(c,109,242,126,242);arrow(c,232,242,249,242)
# Controller return, separate from physical carrier arrows.
c.setStrokeColor(GREY);c.setLineWidth(.8);c.line(302,209,302,179);c.line(302,179,58,179)
arrow(c,58,179,58,207,GREY)
label(c,108,162,'Declared feedback: D = nu (L - X)',8,GREY)
box(c,7,65,346,75,'ELIMINATE THE PENDING DEVIATION q', ['Visible response = initial-history term + causal memory integral', 'K(r) = -(nu / tau) exp(-r / tau), for r >= 0', 'q(0) = 0 means the operating pipeline stock, not an empty pipe.'])
arrow(c,180,155,180,142)
label(c,13,41,'Explicit pending state and its memory representation are equivalent.',8)
label(c,13,24,'Deleting both would lose commitments already made.',8)
c.save()

c=start('modes_and_interaction',257)
label(c,9,242,'TEMPORAL BEHAVIOUR AND COALITION ORDER',10,NAVY,True)
box(c,7,137,167,86,'MONOTONE / SINGLETONS', ['dy/dt = sum of action inputs', 'Linear V(y)', 'Only singleton terms'])
box(c,186,137,167,86,'OSCILLATING / PAIRS', ['Common linear pending tank', 'Quadratic V', 'Pairs allowed; triples exactly zero'])
box(c,7,30,167,86,'MONOTONE / TRIPLE', ['dy/dt = a1 a2 a3', 'Linear V(y)', 'Triple = -T_f'])
box(c,186,30,167,86,'OSCILLATING / TRIPLE', ['Pending tank; input = eps a1 a2 a3', 'Linear receiver V = X', 'Triple = -eps g(T_f), when nonzero'])
label(c,12,10,'Four declared examples; no sampled trajectory or performance ranking.',8)
c.save()
print('Created 6 deterministic vector diagrams.')
