from maya import cmds
from maya import mel

def run() :
	selected = cmds.ls(sl=True)
	fattrs = {'squareVoxels':0, 'dimensionsW':30, 'dimensionsH':6, 'dimensionsD':30, 'densityMethod':0, 'velocitySwirl':5, 'highDetailSolve':3, 'boundaryDraw':4}
	fc = mel.eval('create3DFluid 10 10 10 10 10 10')
	scale = 20
	
	print(fc)
	cmds.setAttr(fc+'.resolution', 100, 20, 100)
	for attr in fattrs :
		cmds.setAttr(fc+'.'+attr, fattrs[attr])
	cmds.select(selected[0])
	fm = cmds.fluidEmitter(type='surface', densityEmissionRate=1, heatEmissionRate=0, fuelEmissionRate=0, fluidDropoff=2, rate=100, cycleInterval=1, maxDistance=1, minDistance=0)[1]
	cmds.connectDynamic(fc, em=fm)
	cmds.setAttr(fm+'.emitterType', 2)
	pt = cmds.particle()
	cmds.setAttr(pt[1]+'.conserve', 0)
	cmds.select(selected[0])
	pm = cmds.emitter(type='surface', rate=100000, scaleRateByObjectSize=0, needParentUV=0, cycleInterval=1, speed=0, speedRandom=0, normalSpeed=1, tangentSpeed=0)
	cmds.connectDynamic(pt[1], em=pm)
	va = cmds.volumeAxis(pos=(0,0,0), magnitude=5, attenuation=0, invertAttenuation=0, awayFromCenter=0, awayFromAxis=0, aroundAxis=1, alongAxis=0, drs=0, turbulence=0.1, turbulenceSpeed=0.2, detailTurbulence=1)[0]
	cmds.setAttr('.sx',scale)
	cmds.setAttr('.sy',scale)
	cmds.setAttr('.sz',scale)
	cmds.connectDynamic(fc, f=va)
	cmds.connectDynamic(pt, f=fc)
	cmds.connectAttr('time1.outTime', va+'.time')
	cmds.setAttr(selected[0]+'.overrideEnabled',1)
	cmds.setAttr(selected[0]+'.overrideDisplayType',1)
	# parent under a group
	grp = cmds.group(n='vortex', em=True)
	cmds.parent(va, grp)
	cmds.parent(fc, grp)
	cmds.parent(pt, grp)
	#cmds.parent(selected[0], grp)
	pass