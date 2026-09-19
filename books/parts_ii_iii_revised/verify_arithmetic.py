"""Exact checks of fixed teaching expressions, not transitions or a simulation."""
from fractions import Fraction as F

count=0
def check(label,actual,expected):
 global count
 assert actual == expected,(label,actual,expected)
 count+=1

def value(x,ref,scales):
 return sum((F(a)-b)**2/F(s)**2 for a,b,s in zip(x,ref,scales))/2

ref=(10,10);scale=(2,2)
for q,after,e in [(0,16,0),(1,F(49,4),F(15,4)),(2,9,7),(4,4,12),
                  (8,0,16),(12,4,12),(16,16,0),(17,F(81,4),F(-17,4)),(18,25,-9)]:
 check('endpoint potential',value((18-q,2+q),ref,scale),after)
 check('finite expansion',4*q-F(q*q,4),e)
 check('endpoint difference',16-after,e)
 check('physical total',(18-q)+(2+q),20)
check('remote baseline',value((18,2,12),(10,10,10),(2,2,2)),F(33,2))
check('remote endpoint',value((14,6,12),(10,10,10),(2,2,2)),F(9,2))
check('unequal baseline',value((18,2),ref,(2,4)),10)
check('unequal endpoint',value((14,6),ref,(2,4)),F(5,2))
check('source scale changed',value((18,2),ref,(1,2)),40)
check('live sum',7+F(27,4)+F(5,4),15)
check('one then three',F(15,4)+F(33,4),12)
check('three then one',F(39,4)+F(9,4),12)
check('group cross',12-7-7,-2)
check('unequal child sum',3+9,12)
check('opposing singleton',0-7-(-9),2)
check('opposing path',8-8,0)
for duration,delta in [(F(1,2),F(-15,4)),(2,-12),(4,-16),(8,0),(9,9)]:
 check('Euler analytic expression',-8*duration+duration**2,delta)
check('rate conversion quarter',6*F(1,4),F(3,2))
check('rate conversion two',6*2,12)
for point,expected in [((18,10,2),16),((14,14,2),12),((14,10,6),4)]:
 check('three-cell route',value(point,(10,10,10),(2,2,2)),expected)
for point,expected in [((10,10,2),12),((6,14,2),16),((6,6,10),0)]:
 check('negative-first route',value(point,(6,6,10),(2,2,2)),expected)
check('negative-first net',-4+16,12)
check('forcing account',1+3-4,0)
check('reverse account',4+0-4,0)
check('Part III singleton',4-value((13,7),ref,scale),F(7,4))
check('Part III group',4-value((12,8),ref,scale),3)
check('Part III path child',2-F(1,2),F(3,2))
check('Part III cross',3-2*F(7,4),F(-1,2))
check('mobility illustration',2*(F(14,10)-F(5,10)),F(18,10))
print(f'{count} exact rational checks passed. Fixed illustrative arithmetic only; no model imports or advancement.')
