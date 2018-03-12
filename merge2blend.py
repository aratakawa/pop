import maya.cmds as cmds

merges = cmds.ls(sl=True, type='mzStandardMerge')
for m in merges :
	bm = cmds.shadingNode('VRayBlendMtl', asShader=True)
	bm = cmds.rename(bm, m+'_VRay')
	for i in range(8) :
		conn = cmds.listConnections(m+'.node%d'%i, p=True)
		if conn != None and len(conn) > 0 :
			node = conn[0].split('.')[0]
			cmds.connectAttr(conn[0], bm+'.coat_material_%d'%i)
			conn2 = cmds.listConnections(node+'.opacity', p=True)
			# if something is connected to the leaf shader's opacity, use that connection
			if conn2 != None and len(conn2) > 0 :
				cmds.connectAttr(conn2[0], bm+'.blend_amount_%d'%i)
			# if nothing is connected but some value is set to the leaf shader's opacity, use that value
			elif cmds.getAttr(node+'.opacity') != [(1,1,1)] :
				opacity = cmds.getAttr(node+'.opacity')[0]
				cmds.setAttr(bm+'.blend_amount_%d'%i, opacity[0], opacity[1], opacity[2], type='double3')
			# mzStandardMerge's opacity value is used
			else :
				conn2 = cmds.listConnections(m+'.opacity%d'%i, p=True)
				if conn2 != None and len(conn2) > 0 :
					cmds.connectAttr(conn2[0], bm+'.blend_amount_%d'%i)
				else :
					opacity = cmds.getAttr(m+'.opacity%d'%i)[0]
					cmds.setAttr(bm+'.blend_amount_%d'%i, opacity[0], opacity[1], opacity[2], type='double3')