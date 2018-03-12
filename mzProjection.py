import maya.cmds as cmds

def assignProjection(ps) :
	engines = cmds.ls(type='shadingEngine')
	
	for e in engines :
		ss = cmds.listConnections(e+'.surfaceShader')
		if ss :
			ss = ss[0]
			switch = cmds.shadingNode('aiRaySwitch', asShader=True)
			cmds.connectAttr(switch+'.outColor', e+'.surfaceShader', f=True)
			cmds.connectAttr(ss+'.outColor', switch+'.camera')
			cmds.connectAttr(ss+'.outColor', switch+'.shadow')
			cmds.connectAttr(ss+'.outColor', switch+'.reflection')
			cmds.connectAttr(ss+'.outColor', switch+'.refraction')
			cmds.connectAttr(ps+'.outColor', switch+'.diffuse')
			cmds.connectAttr(ps+'.outColor', switch+'.glossy')

def glossyOn() :
	standards = cmds.ls(type='mzStandardShader')
	for s in standards :
		cmds.setAttr(s+'.specularIndirectP', 1)
		cmds.setAttr(s+'.specularIndirectS', 1)