from maya import cmds
from maya import mel
import random

ctrlAttrs = {'colorR':1, 'colorG':1, 'colorB':1, 'glowIntensity':0, 'maxSpread':0.5, 'thickness':0.1, 'lightIntensity':2}

root = 'lightningCtrl'
def createLightningOnCurve() :
	selected = cmds.ls(sl=True)
	if not cmds.objExists(root) :
		cmds.spaceLocator(n=root)
		for attr in ctrlAttrs :
			cmds.addAttr(root, at='double', ln=attr, defaultValue=ctrlAttrs[attr])
		cmds.addAttr(root, at='double', ln='length', defaultValue=1.0)
	for s in selected :
		children = cmds.listRelatives(s, shapes=True)
		shape = None
		# look for curve node
		for c in children :
			if cmds.objectType(c) == 'nurbsCurve' :
				shape = c
		if not shape :
			continue
		# create locators
		lsrc = cmds.spaceLocator()[0]
		ldst = cmds.spaceLocator()[0]
		# create group node
		grp = cmds.group(em=True, name='lightningObj#')
		cmds.addAttr(grp, ln='srcLocator', at='message')
		cmds.addAttr(grp, ln='dstLocator', at='message')
		cmds.connectAttr(lsrc+'.message', grp+'.srcLocator')
		cmds.connectAttr(ldst+'.message', grp+'.dstLocator')
		cmds.select([lsrc,ldst], r=True)
		# create lightning
		lightning = mel.eval('lightning "" 0 1 20 1 1 0 1 0.5;')[0]
		cmds.setAttr(lightning+'.colorR', 1)
		cmds.setAttr(lightning+'.glowIntensity', 0)
		print(lightning)
		cmds.addAttr(lightning, ln='curve', at='message')
		cmds.connectAttr(shape+'.message', lightning+'.curve')
		cmds.addAttr(lightning, ln='isLightning', at='bool', dv=1)
		cmds.addAttr(lightning, ln='lifespan', at='long', dv=1)
		cmds.addAttr(lightning, ln='age', at='long', dv=0)
        for attr in ctrlAttrs :
            cmds.connectAttr(root+'.'+attr, lightning+'.'+attr, f=True)
        # parent objects
        cmds.parent(lsrc, grp)
        cmds.parent(ldst, grp)
        cmds.parent(lightning, grp)
        cmds.parent(grp, root)

		
def expression() :
	grps = cmds.listRelatives(root, children=True, type='transform', fullPath=True)
	random.seed(cmds.currentTime(q=True))
	length = cmds.getAttr(root+'.length')
	for g in grps :
		#print(g)
		children = cmds.listRelatives(g, children=True, type='transform', fullPath=True)
		lightning = None
		for c in children :
			if cmds.attributeQuery('isLightning', n=c, ex=True) :
				lightning = c
		if not lightning :
			print('lightning not found for %s. something is wrong' % g)
			continue
		#print(lightning)
		lifespan = cmds.getAttr(lightning+'.lifespan')
		age = cmds.getAttr(lightning+'.age')
		lsrc = cmds.listConnections(g+'.srcLocator')
		ldst = cmds.listConnections(g+'.dstLocator')
		if age >= lifespan :
			lifespan = random.uniform(0,3)
			age = 0
			#print(lsrc,ldst)
			rpos = random.uniform(0.0, 1.0)
			curve = cmds.listConnections(lightning+'.curve')[0]
			maxVal = cmds.getAttr(curve+'.maxValue')
			spos = cmds.pointOnCurve(curve, pr=rpos*maxVal, p=True)
			rlen = random.uniform(0.0, length)
			drpos = rpos*maxVal+rlen
			if drpos > maxVal :
				drpos = maxVal
			dpos = cmds.pointOnCurve(curve, pr=drpos, p=True)
			cmds.xform(lsrc, translation=spos)
			cmds.xform(ldst, translation=dpos)
		else :
			age += 1
			cmds.xform(lsrc, r=True, translation=[0.001,0.001,0.001])
			cmds.xform(ldst, r=True, translation=[0.001,0.001,0.001])
		cmds.setAttr(lightning+'.age', age)
		cmds.setAttr(lightning+'.lifespan', lifespan)
			

selected = cmds.ls(sl=True)
for s in selected :
    cmds.select(s, r=True)
    createLightningOnCurve()
expression()