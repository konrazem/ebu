"""Deterministic vector illustrations of declared equations and diagrams.

No simulation, randomness, model imports or recorded scientific outcomes.
"""
from pathlib import Path
from math import exp
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, white

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'figures'
OUT.mkdir(exist_ok=True)
NAVY=HexColor('#123F56'); TEAL=HexColor('#008C8C'); GREY=HexColor('#627786')
PALE=HexColor('#EDF5F5')

def start(name,h=200):
 c=canvas.Canvas(str(OUT/f'{name}.pdf'),pagesize=(360,h),invariant=1)
 c.setTitle('Illustrative mathematics: '+name.replace('_',' '))
 c.setAuthor('Energy Balance Project')
 return c

def text(c,x,y,t,size=9,color=NAVY):
 c.setFillColor(color);c.setFont('Helvetica',size);c.drawString(x,y,t)

def box(c,x,y,w,h,title,lines):
 c.setStrokeColor(TEAL);c.setFillColor(PALE);c.roundRect(x,y,w,h,4,fill=1,stroke=1)
 text(c,x+8,y+h-17,title,10)
 for i,t in enumerate(lines):text(c,x+8,y+h-34-13*i,t,8)

def arrow(c,x1,y1,x2,y2):
 c.setStrokeColor(NAVY);c.setLineWidth(1.2);c.line(x1,y1,x2,y2)
 from math import atan2,cos,sin
 a=atan2(y2-y1,x2-x1)
 for s in [-1,1]:c.line(x2,y2,x2-6*cos(a)+s*3*sin(a),y2-6*sin(a)-s*3*cos(a))

def plot(name,f,xmin,xmax,ymin,ymax,xticks,yticks,xlabel,ylabel,caption,second=None):
 c=start(name,225);left,bottom,w,h=42,45,302,146
 px=lambda x:left+(x-xmin)/(xmax-xmin)*w
 py=lambda y:bottom+(y-ymin)/(ymax-ymin)*h
 c.setStrokeColor(GREY);c.setLineWidth(.5)
 c.line(left,bottom,left,bottom+h);c.line(left,bottom,left+w,bottom)
 for x in xticks:
  c.line(px(x),bottom,px(x),bottom-3);text(c,px(x)-5,bottom-15,str(x),8)
 for y in yticks:
  c.line(left-3,py(y),left,py(y));text(c,8,py(y)-3,str(y),8)
 if ymin<0<ymax:
  c.setDash(2,3);c.line(left,py(0),left+w,py(0));c.setDash()
 for fun,col,dash in [(f,TEAL,False)]+([(second,GREY,True)] if second else []):
  p=c.beginPath()
  for k in range(401):
   x=xmin+(xmax-xmin)*k/400;y=fun(x)
   if k==0:p.moveTo(px(x),py(y))
   else:p.lineTo(px(x),py(y))
  c.setStrokeColor(col);c.setLineWidth(1.6);c.setDash(4,3) if dash else c.setDash();c.drawPath(p)
 c.setDash();text(c,left,207,ylabel,10);text(c,130,18,xlabel,9);text(c,42,2,caption,7)
 c.save()

plot('potential',lambda x:(x-10)**2/8,0,20,0,13,[0,5,10,15,20],[0,4,8,12], 'Local stock x (stock units)','Local potential V_i','Declared reference 10; scale 2. Mathematical illustration.')
plot('finite',lambda q:4*q-q*q/4,0,18,-10,18,[0,4,8,12,16,18],[-8,0,8,16], 'Transfer quantity q (stock units)','Exact finite field value E(q)','Frozen state (18,2); references (10,10); scales (2,2).')
plot('marginal',lambda q:4-q/2,0,18,-6,5,[0,4,8,12,16,18],[-4,0,4], 'Transfer quantity q (stock units)','Slope of E(q)','The slope crosses zero at q=8; it does not select an action.')
plot('gaussian',lambda x:exp(-(x-10)**2/8),2,18,0,1.1,[2,6,10,14,18],[0,.5,1], 'Local stock x (stock units)','Relative Gaussian shape exp(-V_i)','Relative shape with peak 1; not an observed probability distribution.')

c=start('two_records',208)
box(c,5,95,165,94,'Monetary record',['Payment and obligation','Contract and authorization','Claims under institutions'])
box(c,190,95,165,94,'Physical record',['Quantity and transformation','State, boundary and evidence','Declared finite field change'])
box(c,90,7,180,59,'One linked event',['A shared identity connects records.','Their meanings remain distinct.'])
arrow(c,87,93,149,68);arrow(c,272,93,212,68);c.save()

c=start('transfer',174)
box(c,5,70,103,70,'Ridge',['Before: 18','After: 14'])
box(c,252,70,103,70,'Vale',['Before: 2','After: 6'])
arrow(c,115,104,245,104);text(c,150,116,'q = 4',11)
text(c,23,40,'Total stock: 20 before and after',10)
text(c,23,22,'Potential: 16 before, 4 after; field value: +12',10);c.save()

c=start('locality',206)
for x,t,lines in [(6,'Cell 1',['8 -> 2']),(126,'Cell 2',['8 -> 2']),(246,'Other cells',['1 -> 1'])]:box(c,x,115,108,63,t,lines)
arrow(c,60,108,60,61);arrow(c,180,108,180,61);arrow(c,300,108,300,61)
text(c,35,45,'reduction 6',9);text(c,155,45,'reduction 6',9);text(c,275,45,'cancels',9)
text(c,30,12,'Local difference 12 = global difference 17 - 5',10);c.save()

c=start('sequence',165)
for x,t,lines in [(2,'Start',['V = 16']),(96,'After A',['V = 9']),(190,'After B',['V = 2.25']),(284,'End',['V = 1'])]:box(c,x,79,74,57,t,lines)
for x,label in [(76,'7'),(170,'6.75'),(264,'1.25')]:arrow(c,x,105,x+18,105);text(c,x-2,66,label,9)
text(c,37,35,'Action values: 7 + 6.75 + 1.25 = 15',10)
text(c,37,17,'Endpoint difference: 16 - 1 = 15',10);c.save()

c=start('group',205)
box(c,5,115,160,72,'Separate counterfactuals',['A alone: E = 7','B alone: E = 7','Sum: 14'])
box(c,195,115,160,72,'One joint transition',['Accepted quantities: 2 + 2','Joint field value: 12','Cross-term correction: -2'])
box(c,68,15,225,65,'Declared common-path attribution',['R_A = 6; R_B = 6; sum = 12','Closure does not establish ownership.'])
arrow(c,277,110,241,83);c.save()

c=start('route',170)
for x,t,lines in [(5,'Ridge',['18 -> 14']),(128,'Hub',['10 -> 14 -> 10']),(252,'Vale',['2 -> 6'])]:box(c,x,86,102,63,t,lines)
arrow(c,110,117,123,117);arrow(c,233,117,247,117)
text(c,25,56,'First edge: field value 4',9);text(c,192,56,'Second edge: value 8',9)
text(c,28,25,'Route total 12; intermediate potential cancels.',10);c.save()

c=start('account_layers',245)
rows=[('Physical state','Stocks, carriers and boundaries'),('Potential difference','The declared finite field account'),('Service outcome','What function was delivered, and when'),('Institutional response','Permission, access and compensation')]
for i,(title,desc) in enumerate(rows):
 y=185-55*i;box(c,30,y,300,44,title,[desc])
 if i<3:arrow(c,180,y-1,180,y-9)
c.save()
print('Created 11 vector figures; all are schematics or equation illustrations.')
