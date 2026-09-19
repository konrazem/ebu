"""Draw declared schematics and static formula curves; no scientific model code."""
from pathlib import Path
from math import atan2, cos, sin
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import reportlab
from reportlab.lib.colors import HexColor, white

ROOT = Path(__file__).resolve().parent
INK = HexColor('#173e48')
MUTED = HexColor('#56666a')
PALE = HexColor('#e8f1f1')
W = 364
FONTDIR = Path(reportlab.__file__).resolve().parent / 'fonts'
pdfmetrics.registerFont(TTFont('BookSans', str(FONTDIR / 'Vera.ttf')))
pdfmetrics.registerFont(TTFont('BookSansBold', str(FONTDIR / 'VeraBd.ttf')))

def start(name, h):
    (ROOT / 'figures').mkdir(exist_ok=True)
    c = canvas.Canvas(str(ROOT / 'figures' / (name + '.pdf')), pagesize=(W,h), invariant=1)
    c.setTitle(name.replace('_', ' ') + ' - labelled book illustration')
    c.setAuthor('EBU Book I introductory edition')
    return c

def txt(c,x,y,s,size=10,bold=False,align='left'):
    c.setFillColor(INK)
    c.setFont('BookSansBold' if bold else 'BookSans',size)
    getattr(c, {'left':'drawString','center':'drawCentredString','right':'drawRightString'}[align])(x,y,s)

def box(c,x,y,w,h,lines):
    c.setStrokeColor(INK); c.setFillColor(PALE); c.setLineWidth(.7)
    c.roundRect(x,y,w,h,5,fill=1,stroke=1)
    for k,s in enumerate(lines):
        label_size = 9 if s == 'Compare / decide' else 10
        txt(c,x+w/2,y+h-17-14*k,s,label_size,k==0,'center')

def arrow(c,x1,y1,x2,y2):
    c.setStrokeColor(INK); c.setLineWidth(1)
    c.line(x1,y1,x2,y2)
    angle=atan2(y2-y1,x2-x1)
    for offset in (-.45,.45): c.line(x2,y2,x2-6*cos(angle+offset),y2-6*sin(angle+offset))

def finish(c): c.showPage(); c.save()

c=start('two_records',197)
txt(c,0,183,'ONE EVENT, DISTINCT QUESTIONS',10,True)
box(c,99,113,166,48,['A pumping event','Water enters the clinic tank'])
arrow(c,130,113,87,83); arrow(c,234,113,277,83)
box(c,0,15,174,66,['Payment record','Who paid, and how much?','Which obligation was settled?'])
box(c,190,15,174,66,['Physical record','What moved or changed?','Was the service available?'])
finish(c)

c=start('regulation',212)
txt(c,0,197,'DECLARED ENGINEERING FEEDBACK',10,True)
box(c,3,116,96,46,['Measure level','Sensor'])
box(c,134,116,96,46,['Compare / decide','Control rule'])
box(c,266,116,94,46,['Change inflow','Pump'])
arrow(c,99,139,134,139); arrow(c,230,139,266,139)
box(c,133,26,100,49,['Stored water','Tank'])
arrow(c,313,116,313,50); arrow(c,313,50,233,50)
arrow(c,133,50,50,50); arrow(c,50,50,50,116)
txt(c,50,33,'level signal',9,False,'center')
arrow(c,182,26,182,4); txt(c,195,6,'outflow to use',9)
txt(c,282,77,'inflow',9)
finish(c)

c=start('transfer',210)
txt(c,0,194,'ONE DECLARED THREE-LITRE TRANSFER',10,True)
for row,stocks,label in [(108,(14,6),'Before'),(18,(11,9),'After')]:
    txt(c,0,row+42,label,10,True)
    for x,name,stock in [(86,'Ridge',stocks[0]),(252,'Vale',stocks[1])]:
        c.setFillColor(PALE); c.rect(x,row,64,60*stock/20,fill=1,stroke=0)
        c.setStrokeColor(INK); c.rect(x,row,64,60,fill=0,stroke=1)
        txt(c,x+32,row+64,name,10,True,'center');txt(c,x+32,row+22,f'{stock} L',12,True,'center')
    txt(c,187,row+3,'Total: 20 L',9,False,'center')
arrow(c,155,146,245,146); txt(c,200,157,'3 L',10,True,'center')
finish(c)

def axes(c, xmin,xmax,ymin,ymax,xticks,yticks,xlabel,ylabel):
    l,b,r,t=43,38,354,179
    X=lambda x:l+(x-xmin)/(xmax-xmin)*(r-l)
    Y=lambda y:b+(y-ymin)/(ymax-ymin)*(t-b)
    c.setStrokeColor(HexColor('#ced8da'));c.setLineWidth(.4)
    for v in yticks:c.line(l,Y(v),r,Y(v));txt(c,l-7,Y(v)-3,str(v),9,False,'right')
    c.setStrokeColor(INK);c.setLineWidth(.7);c.line(l,b,l,t);c.line(l,Y(0),r,Y(0))
    for v in xticks:
        c.line(X(v),b,X(v),b-4);txt(c,X(v),b-16,str(v),9,False,'center')
    txt(c,(l+r)/2,6,xlabel,10,False,'center');txt(c,0,201,ylabel,10,True)
    return X,Y

def curve(c,X,Y,fn,xmin,xmax,dashed=False):
    c.setStrokeColor(INK); c.setLineWidth(1.7);c.setDash(5,3) if dashed else c.setDash()
    p=c.beginPath()
    for k in range(301):
        x=xmin+(xmax-xmin)*k/300
        if k==0:p.moveTo(X(x),Y(fn(x)))
        else:p.lineTo(X(x),Y(fn(x)))
    c.drawPath(p);c.setDash()

c=start('quadratic',226)
X,Y=axes(c,2,18,0,8,[2,6,10,14,18],[0,2,4,6,8],'Stock x (L)','Local potential V_i (dimensionless)')
curve(c,X,Y,lambda x:(x-10)**2/8,2,18)
curve(c,X,Y,lambda x:(x-10)**2/32,2,18,True)
txt(c,107,159,'Solid: scale 2 L',9);txt(c,107,145,'Dashed: scale 4 L',9)
txt(c,107,131,'Reference: 10 L',9)
finish(c)

c=start('finite_value',228)
X,Y=axes(c,0,10,-6,21,[0,2,4,6,8,10],[-5,0,5,10,15,20],'Alternative quantity q (L), not time','Finite action value (dimensionless)')
curve(c,X,Y,lambda q:2*q-q*q/4,0,10)
curve(c,X,Y,lambda q:2*q,0,10,True)
txt(c,65,157,'Dashed: initial slope prediction 2q',9)
txt(c,65,143,'Solid: exact value 2q - q^2/4',9)
c.setFillColor(INK);c.circle(X(4),Y(4),2.5,stroke=0,fill=1)
txt(c,X(4)+8,Y(4)+7,'(4 L, 4)',9)
finish(c)

c=start('group',239)
txt(c,0,223,'COMMON BASELINE: (14, 12, 4) L; V = 7',10,True)
box(c,2,132,110,63,['Action a alone','(12, 12, 6) L','V = 3; value = 4'])
box(c,252,132,110,63,['Action b alone','(14, 10, 6) L','V = 4; value = 3'])
txt(c,182,174,'Alternative',9,False,'center');txt(c,182,160,'singleton quotes',9,False,'center')
box(c,78,34,208,66,['Both actions: joint endpoint','(12, 10, 8) L; V = 1','Group field value = 7 - 1 = 6'])
txt(c,182,114,'a: 2 L from first tank; b: 2 L from second',9,False,'center')
txt(c,182,16,'Common-path attribution: 3.5 + 2.5 = 6',10,True,'center')
finish(c)
print('Created six schematic/static-formula figures; no model execution.')
