import maya.cmds as cmds

def replace(instance=True) :
	selected = cmds.ls(sl=True, l=True)
	targets = selected[:-1]
	src = selected[-1]
	delete = []
	for tobj in targets :
		r = cmds.getAttr(tobj+'.rotate')[0]
		t = cmds.getAttr(tobj+'.translate')[0]
		s = cmds.getAttr(tobj+'.scale')[0]
		p = cmds.listRelatives(tobj, f=True, p=True)
		if p and len(p) > 0 :
			p = p[0]
		
		newobj = None
		if instance :
			newobj = cmds.instance(src, n='MarzaReplaceObj')[0]
		else :
			newobj = cmds.duplicate(src, n='MarzaReplaceObj')[0]
		delete.append(tobj)
		cmds.setAttr(newobj+'.translate', t[0], t[1], t[2])
		cmds.setAttr(newobj+'.rotate', r[0], r[1], r[2])
		cmds.setAttr(newobj+'.scale', s[0], s[1], s[2])
		cmds.delete(tobj)
		if p :
			cmds.parent(newobj, p)
		print(newobj, tobj.split('|')[-1])
		cmds.rename(newobj, tobj.split('|')[-1])
		
	