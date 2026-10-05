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
box(c,7,230,346,57,'COMPLETE COALITION TABLE', ['One baseline, field and comparison protocol', 'Every required subset is defined and physically scoped'])
arrow(c,115,307,115,289)
box(c,7,153,346,57,'INTERACTION AND EXACT DISCRETE TAYLOR', ['Alternating differences = Mobius coefficients', 'Recursion; unique multilinear reconstruction without remainder'])
arrow(c,180,230,180,212)
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
box(c,5,36,350,68,'WHAT THE ENDPOINT TABLE IDENTIFIES', ['The total coefficient: m_E(T) = - Delta_T G(0)', 'A unique multilinear representation on the Boolean cube', 'No unique split into causal or physical origins without more evidence'])
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
print('Created 3 deterministic vector diagrams.')
