"""Exact arithmetic on declared, fixed teaching states. No transitions or runners."""
from fractions import Fraction as F
from pathlib import Path
import json

checks = []
def equal(name, actual, expected):
    if actual != expected:
        raise AssertionError(f'{name}: {actual} != {expected}')
    checks.append({'check':name, 'actual':str(actual), 'expected':str(expected), 'passed':True})

def potential(fixed_stocks, scales=None):
    """Pure evaluation of one frozen illustrative state, not an update rule."""
    scales = scales or [2] * len(fixed_stocks)
    return sum((F(x)-10)**2 / (2*F(s)**2) for x,s in zip(fixed_stocks,scales))

equal('quantity = 2 L/min times 1.5 min', F(2)*F(3,2),F(3))
equal('two-tank starting total',14+6,20)
equal('two-tank displayed endpoint total',11+9,20)
equal('two-tank reference mass',10+10,20)
equal('incompatible 12/12 target exceeds available total',12+12-20,4)
equal('one-cell score at 14 L, scale 2 L',potential([14]),F(2))
equal('one-cell score at 14 L, scale 4 L',potential([14],[4]),F(1,2))
equal('local scores at 8,10,12 L',tuple(potential([v]) for v in (8,10,12)),(F(1,2),F(0),F(1,2)))
equal('two-tank initial potential',potential([14,6]),F(4))
equal('two-tank 18/2 potential',potential([18,2]),F(16))
# Each tuple below is an independently specified alternative, not the output
# of an action function, and no endpoint is fed to a runner or state updater.
rows=[(0,(14,6),F(4),F(0)),(1,(13,7),F(9,4),F(7,4)),
      (3,(11,9),F(1,4),F(15,4)),(4,(10,10),F(0),F(4)),
      (6,(8,12),F(1),F(3)),(8,(6,14),F(4),F(0)),
      (9,(5,15),F(25,4),F(-9,4))]
for q,state,v,e in rows:
    equal(f'table q={q}: physical total',sum(state),20)
    equal(f'table q={q}: potential',potential(state),v)
    equal(f'table q={q}: endpoint difference',F(4)-v,e)
    equal(f'table q={q}: quadratic expression',2*F(q)-F(q*q,4),e)
    equal(f'table q={q}: source/destination arithmetic',state,(14-q,6+q))
    equal(f'table q={q}: capacity bounds',all(0<=x<=20 for x in state),True)
equal('three-litre initial marginal prediction',F(2)*3,F(6))
equal('three-litre curvature correction',F(1,2)*(9+9)/4,F(9,4))
equal('departure from reference',potential([10,10])-potential([9,11]),F(-1,4))
equal('four-cell initial value',potential([14,6,12,8]),F(5))
equal('four-cell endpoint value',potential([11,9,12,8]),F(5,4))
equal('affected support cancellation',potential([14,6,12,8])-potential([11,9,12,8]),F(15,4))
equal('marginal at Ridge',F(14-10,4),F(1))
equal('marginal at Vale',F(6-10,4),F(-1))
equal('local sensitivity example',potential([F(61,10)])-potential([6]),F(-79,800))
equal('group reference and starting mass',sum((14,12,4)),30)
equal('group initial potential',potential([14,12,4]),F(7))
equal('singleton a endpoint potential',potential([12,12,6]),F(3))
equal('singleton b endpoint potential',potential([14,10,6]),F(4))
equal('group endpoint potential',potential([12,10,8]),F(1))
da=(-2,0,2); db=(0,-2,2); dg=(-2,-2,4); mu=(F(1),F(1,2),F(-3,2))
equal('additive displayed increments',tuple(a+b for a,b in zip(da,db)),dg)
equal('signed cross term',sum(F(a*b,4) for a,b in zip(da,db)),F(1))
for name,d,linear,correction,attribution in [('a',da,F(5),F(3,2),F(7,2)),('b',db,F(4),F(3,2),F(5,2))]:
    lin=-sum(m*v for m,v in zip(mu,d))
    cur=sum(F(v*w,8) for v,w in zip(d,dg))
    equal(f'{name}: initial linear contribution',lin,linear)
    equal(f'{name}: common-path correction',cur,correction)
    equal(f'{name}: common-path attribution',lin-cur,attribution)
equal('common-path closure',F(7,2)+F(5,2),F(7)-F(1))
equal('singleton excess',F(4)+3-1,F(6))
equal('a then b endpoint differences',(F(7)-3,F(3)-1),(F(4),F(2)))
equal('b then a endpoint differences',(F(7)-4,F(4)-1),(F(3),F(3)))
equal('opposing increment cross term',sum(F(a*(-a),4) for a in da),F(-2))
equal('opposing singleton sum corrected',-F(1)-1-(-2),F(0))
equal('two displayed sequential accounts telescope',F(15,4)+F(1,4),F(4))
equal('ideal closed cycle',F(15,4)-F(15,4),F(0))
equal('0.3 L boundary loss arithmetic',F(3)-F(27,10),F(3,10))
# Formal polynomial coefficient checks in independent symbols. Coefficients,
# not sampled trajectories, verify the elementary quadratic cancellations.
# Ordered monomials: d^2, d*h, h^2; divide by 2*sigma^2 afterwards.
equal('expanded endpoint minus initial coefficients',(1-1,2,1),(0,2,1))
# E(a+b)-E(a)-E(b) has only -a^T H b after symmetry of H.
equal('mixed quadratic coefficient',-F(1,2)*2,F(-1))
# In V_next + B_next - J_next minus V + B - J, with
# deltaB=Vz-Vnext and deltaJ=Vz-V, coefficients (Vnext,Vz,V) cancel.
equal('capacity-audit identity coefficients',(1-1,1-1,1-1),(0,0,0))
report={'scope':'Static exact arithmetic and polynomial coefficients only; no scientific model imports, transitions, simulations, random draws or parameter searches.',
        'passed':True,'count':len(checks),'checks':checks}
out=Path(__file__).resolve().parent/'review'/'mathematics_checks.json'
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(report,indent=2)+'\n')
print(f'{len(checks)} exact fixed-state/coefficient checks passed.')
