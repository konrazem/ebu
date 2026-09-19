"""Exact fixed-state textbook arithmetic only; no model modules or transitions."""
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
import json

checks=[]
def check(label,actual,expected):
 assert actual==expected,(label,actual,expected)
 checks.append({'label':label,'exact_value':str(actual)})
def potential(x,ref,scale):
 return sum(((Q(a)-b)/c)**2 for a,b,c in zip(x,ref,scale))/2
def value(x,d,ref,scale):
 return potential(x,ref,scale)-potential(tuple(Q(a)+b for a,b in zip(x,d)),ref,scale)
def attribution(x,child,total,ref,scale):
 return -sum((Q(a)-r+Q(g)/2)*d/Q(s)**2
             for a,r,g,d,s in zip(x,ref,total,child,scale))

check('weighted chain endpoint',potential((15,11,4),(10,)*3,(2,)*3),Q(31,4))
check('weighted chain finite value',value((18,10,2),(-3,1,2),(10,)*3,(2,)*3),Q(33,4))
for label,d in [('hub A',(-4,4,0)),('hub B',(0,-4,4))]:
 check(label+' singleton',value((18,10,2),d,(10,)*3,(2,)*3),4)
 check(label+' common path',attribution((18,10,2),d,(-4,0,4),(10,)*3,(2,)*3),6)
check('hub group',value((18,10,2),(-4,0,4),(10,)*3,(2,)*3),12)
x=(18,6,6,10);ref=(10,)*4;scale=(2,)*4
children=[(-2,2,0,0),(-2,0,2,0),(-2,0,0,2)]
expected={():0,(0,):5,(1,):5,(2,):3,(0,1):9,(0,2):7,(1,2):7,(0,1,2):10}
values={}
for subset,wanted in expected.items():
 d=tuple(sum(children[j][i] for j in subset) for i in range(4))
 values[subset]=value(x,d,ref,scale)
 check('three-child subset '+str(subset),values[subset],wanted)
for (a,b) in combinations(range(3),2):
 check('pair coefficient '+str((a,b)),values[(a,b)]-values[(a,)]-values[(b,)],-1)
check('third coefficient',sum((-1)**(3-len(k))*v for k,v in values.items()),0)
for n,wanted in enumerate((4,4,2)):
 check('three-child attribution '+str(n),attribution(x,children[n],(-6,2,2,2),ref,scale),wanted)
check('disjoint group',value((14,6,14,6),(-2,2,-2,2),ref,scale),6)
for label,d,wanted in [('A',(-2,2,0),Q(7,2)),('B',(0,-2,2),Q(-5,2))]:
 check('positive group signed child '+label,attribution((14,6,10),d,(-2,0,2),(10,)*3,(2,)*3),wanted)
check('positive group endpoint',value((14,6,10),(-2,0,2),(10,)*3,(2,)*3),1)
check('scale change only',potential((18,2),(10,10),(2,2))-potential((18,2),(10,10),(4,4)),12)
check('repair rail factor',Q(99,100)**2,Q(9801,10000))
check('repair air factor',Q(99,100)*Q(98,100),Q(9702,10000))
check('repair signed lines',1+1-2+59,59)
check('repair endpoint less burdens',80-5-(3+1+8+4),59)
# Verify the continuous example symbolically by coefficient identities,
# not by integrating an ODE or evaluating a time series.
check('continuous force coefficient',Q(1,4)+Q(1,4),Q(1,2))
check('continuous response coefficient',Q(1,2)*Q(1,2),Q(1,4))
check('continuous initial potential',Q(8)**2/4,16)
check('continuous potential exponent coefficient',2*Q(1,4),Q(1,2))
check('threshold limiting potential coefficient',Q(2)**2/4,1)
record={'checks':len(checks),'all_passed':True,'execution_class':'fixed-state exact rational arithmetic',
        'model_imports':0,'model_transitions':0,'scientific_runs':0,'details':checks}
out=Path(__file__).resolve().parent/'review'
out.mkdir(exist_ok=True)
(out/'arithmetic_checks.json').write_text(json.dumps(record,indent=2)+'\n')
print(f'{len(checks)} exact arithmetic checks passed; no model imported or advanced.')
