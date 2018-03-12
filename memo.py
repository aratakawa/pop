target = 'Z:/marza/proj/kibble/work/Character/Bobby/model/everyone/mid/textures/cloth'
import re, os
from maya import cmds

cmds.select(cl=True)
for f in cmds.ls(sl=True) :
	if cmds.objectType(f) != 'file' :
		continue
	path = cmds.getAttr(f+'.fileTextureName')
	file = os.path.basename(path)
	m = re.search('\\.v[0-9]*\\.', file)
	if m is not None :
		file = file.replace(m.group(), '.')
	newpath = os.path.join(target, file).replace('\\', '/')
	if os.path.isfile(newpath) :
		print(newpath)
		cmds.setAttr(f+'.fileTextureName', newpath)
	else :
		cmds.select(f, add=True)

		
for f in cmds.ls(type='file') :
	cmds.setAttr(f+'.aiMakeTxMode', 0)

prefix = 'FunlandMob04A'
for o in cmds.ls() :
	try :
		base = o.split(':')[-1]
		name = prefix+base
		cmds.rename(o, name)
		print(name)
	except:
		pass

for o in cmds.ls(sl=True) :
    try :
        cmds.keyframe(o, e=True, tc=-40, r=True)
    except:
        pass
		
def getObjectIds() :
	shapes = cmds.ls(type='shape', visible=True)
	attr = 'mtoa_objectid'
	objectids = {}
	for s in shapes :
		if cmds.attributeQuery(attr, n=s, ex=True) :
			val = cmds.getAttr(s+'.'+attr)
			if not objectids.has_key(val) :
				objectids[val] = []
			objectids[val].append(s)
	
	if objectids :
		for val in objectids :
			print('[%d]:' % val)
			for obj in objectids[val] :
				print('\t%s' % obj)
	return objectids