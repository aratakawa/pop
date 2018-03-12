from maya import cmds

def run() :
	attrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']
	src = cmds.ls(sl=True)[0]
	dst = cmds.ls(sl=True)[1]
	p = cmds.xform(src, q=True, rp=True, os=True)
	cmds.xform(dst, rp=p, os=True)
	p = cmds.xform(src, q=True, sp=True, os=True)
	cmds.xform(dst, sp=p, os=True)
	for a in attrs :
		cmds.setAttr(dst+'.'+a, cmds.getAttr(src+'.'+a))

def match() :
	src = cmds.ls(sl=True)[0]
	dst = cmds.ls(sl=True)[1]
	m = cmds.xform(src, q=True, matrix=True)
	cmds.xform(dst, matrix=m, ws=True)