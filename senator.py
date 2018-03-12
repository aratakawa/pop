from maya import cmds

selected = cmds.ls(sl=True)
temp = cmds.ls(type='shadingEngine')
engines = []
for e in temp :
    if e.startswith('source:') :
        engines.append(e)

for e in engines :
    cmds.select(e)
    mesh = cmds.ls(sl=True, type='mesh')
    if len(mesh) >  0 :
        print(e, mesh)
        objs = []
        for m in mesh :
            obj = m.split(':')[-1]
            if cmds.objExists(obj) :
                objs.append(obj)
        if len(objs) != len(mesh) :
            print(e, 'not matched')
        if len(obj) > 0 :
            cmds.select(e, ne=True)
            cmds.hyperShade(duplicate=True)
            cmds.select(objs)
            print(objs)
            cmds.sets(e=True, forceElement=e.split(':')[-1])
			

import os
sbase = 'Senator'
srep = 'B'
tbase = 'attend'
rep = 'B'
missing = []
for f in cmds.ls(type='file') :
    path = cmds.getAttr(f+'.fileTextureName')
    npath = path
    if '%s%s' % (sbase.lower(), srep) in path :
        npath = npath.replace( '%s%s' % (sbase.lower(), srep),  '%s%s' % (tbase.lower(), rep))
    if '%s%s' % (sbase,srep) in path :
        npath = npath.replace( '%s%s' % (sbase, srep),  '%s%s' % (tbase, rep))
    if npath != path :
        if not os.path.isfile(npath) :
            print('[ERROR] missing', npath)
            missing.append(f)
        else :
            cmds.setAttr(f+'.fileTextureName', npath, type='string')
            print(f, npath)

if len(missing) > 0 :
    cmds.select(missing)

import os
missing = []
for f in cmds.ls(type='file') :
    path = cmds.getAttr(f+'.fileTextureName')
    if path.endswith('.tif') :
        npath = path.replace('.tif','.tx')
        if os.path.isfile(npath) :
            cmds.setAttr(f+'.fileTextureName', npath, type='string')
        else :
            missing.append(f)
            print('[ERROR] %s missing.' % npath)
if len(missing) > 0 :
    cmds.select(f)