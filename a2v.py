import sys

scriptpath = 'Z:/marza/proj/onyx/team/lookdev/scripts/a2v/python'

if not cmds.pluginInfo('vrayformaya',  q=True,loaded=True) :
	cmds.loadPlugin('vrayformaya')

scripts = ['a2v_funcs', 'a2v_preProcess']
#scripts = ['a2v_step1', 'a2v_step2', 'a2v_step3']
for s in scripts :
    sf = os.path.join(scriptpath, s+'.py')
    exec(open(sf).read())

exec(open(os.path.join(scriptpath, 'a2v_step1.py')).read())

exec(open(os.path.join(scriptpath, 'a2v_step2.py')).read())

exec(open(os.path.join(scriptpath, 'a2v_step3.py')).read())


import os
for f in cmds.ls(type='file') :
	path = cmds.getAttr(f+'.fileTextureName')
	if path.endswith('.tx') :
		exts = ['.tga', '.tif']
		for e in exts :
			npath = os.path.splitext(path)[0]+e
			if os.path.isfile(npath) :
				print(f, npath)
				cmds.setAttr(f+'.fileTextureName', npath, type='string')