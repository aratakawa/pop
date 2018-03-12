from maya import cmds

def reconnectNode(node) :
	#node = cmds.ls(sl=True)[0]
	newn = cmds.duplicate(node, ic=True)[0]
	print(newn)
	val = cmds.getAttr(node+'.secondTerm')
	cmds.setAttr(node+'.secondTerm', val-0.1)
	cmds.setAttr(node+'.operation', 2)
	cmds.setAttr(newn+'.secondTerm', val+0.1)
	cmds.setAttr(newn+'.operation', 4)
	for n in (node, newn) :
		cmds.setAttr(n+'.colorIfTrue', 1,1,1, type='double3')
		cmds.setAttr(n+'.colorIfFalse', 0,0,0, type='double3')
	targets = cmds.listConnections(node+'.outColor', p=True)
	mult = cmds.shadingNode('multiplyDivide', asUtility=True)
	rev = cmds.shadingNode('reverse', asUtility=True)
	cmds.connectAttr(node+'.outColor', mult+'.input1')
	cmds.connectAttr(newn+'.outColor', mult+'.input2')
	cmds.connectAttr(mult+'.output', rev+'.input')
	for t in targets :
		print(t)
		cmds.connectAttr(rev+'.output', t, f=True)

def reconnect() :
	nodes = cmds.ls(sl=True, type='condition')
	for n in nodes :
		reconnectNode(n)