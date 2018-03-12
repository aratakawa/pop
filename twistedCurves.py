def twistedCurves() :
import pymel.core as pm
import sys
import random
import math

if not 'Z:/ve/home/ArakawaT/maya/python' in sys.path :
    sys.path.append('Z:/ve/home/ArakawaT/maya/python')

import mayawrap as mw

pm.select(hi=True)
obj = pm.selected(type='mesh')[0]

curvenum = 5.0
curvespan = 30.0
dumax = 5
circlemin = 0.02
circlemax = 0.1

extrude = True

print(obj.name())
print(obj.numFaces())

curves = []
for i in range(curvenum) :
    print('curve %d/%d' % (i+1,curvenum))
    dv = 1.0/curvespan
    u = random.uniform(0.0,1.0)
    cpoints = []
    for i in range(curvespan+1) :
        u = math.fmod(u+random.uniform(0, (dumax/curvespan)*2.0),1)
        #print(u,i*dv)
        faceiter = obj.faces
        for f in faceiter :
            try :
                p = f.getPointAtUV((u, i*dv), space='world')
                #print(p)
                cpoints.append(p)
                break
            except :
                pass
    curve = pm.curve(p=cpoints, d=3)
    curves.append(curve)
    if extrude :
        circle = pm.circle()[0]
        randscale = random.uniform(circlemin, circlemax)
        pm.xform(circle, scale=(randscale,randscale,randscale))
        pm.xform(circle, translation=cpoints[0])
        pm.extrude(circle, curve, ch=True, rn=False, po=0, et=2, ucp=0, fpt=True, upn=True, rotation=0, scale=1, rsp=True)
    print(cpoints)
pm.select(curves)