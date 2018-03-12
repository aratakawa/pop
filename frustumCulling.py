attribs = {}
attribs['vector'] = ['campos', 'camx', 'camy', 'camz', 'rightvec', 'leftvec', 'topvec', 'bottomvec']
attribs['float'] = ['maxdist', 'mindist']

def addVectorAttr(shape, attr) :
	targets = ['X', 'Y', 'Z']
	attrname = 'yetiVariableV_%s' % attr
	if not cmds.attributeQuery(attrname, n=shape, ex=True) :
		cmds.addAttr(shape, ln=attrname, at='double3')
		for t in targets :
			cmds.addAttr(shape, ln=attrname+t, p=attrname, at='double')
		for t in targets :
			cmds.setAttr(shape+'.'+attrname+t, e=True, keyable=True)
		cmds.setAttr(shape+'.'+attrname, 0, 0, 0, type='double3')
		cmds.setAttr(shape+'.'+attrname, e=True, keyable=True)

def addFloatAttr(shape, attr) :
	attrname = 'yetiVariableF_%s' % attr
	if not cmds.attributeQuery(attrname, n=shape, ex=True) :
		cmds.addAttr(shape, ln=attrname, at='double')
		cmds.setAttr(shape+'.'+attrname, e=True, keyable=True)

def addAttributes(shape) :
	for t in attribs.keys() :
		if t == 'vector' :
			for a in attribs[t] :
				addVectorAttr(shape, a)
		elif t== 'float' :
			for a in attribs[t] :
				addFloatAttr(shape, a)