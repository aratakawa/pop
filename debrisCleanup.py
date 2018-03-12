import maya.cmds as cmds
import maya.mel as mel
import os, shutil
import bakeUtils

def assignedShaders(mesh) :
	assigned = cmds.listConnections(mesh, type='shadingEngine')
	if assigned == None :
		cmds.error('[ERROR] no shader assgned to shape: %s' % mesh)
		cmds.hyperShade(assign='lambert1')
		return []
	return set(assigned)

def assignedShadersH() :
	initial = cmds.ls(sl=True)
	cmds.select(hi=True)
	mesh = cmds.ls(sl=True, type='mesh')
	engines = []
	for m in mesh :
		if cmds.getAttr(m+'.intermediateObject') :
			continue
		assigned = assignedShaders(m)
		for a in assigned :
			if a not in engines :
				engines.append(a)
	print('%d shaders' % len(engines))
	for e in engines :
		print(e)
	cmds.select(initial)

def getShaders() :
	engines = cmds.ls(type='shadingEngine')
	shaders = []
	omit = ['initialShadingEngine', 'initialParticleSE']
	for e in engines :
		if e in omit :
			continue
		shader = cmds.listConnections(e+'.surfaceShader')
		if shader == None or len(shader) == 0 :
			continue
		shaders.append(shader[0])
	return shaders
	
def cleanupShaderAssign() :
	initial = cmds.ls(sl=True)
	cmds.select(cl=True)
	shaders = getShaders()
	variations = {}
	for s in shaders :
		col = tuple(cmds.getAttr(s+'.color'))
		if col not in variations.keys() :
			variations[col] = s
	for v in variations :
		print('%s: %s' % (variations[v],str(v)))
	for s in shaders :
		if s not in variations.keys() :
			col = tuple(cmds.getAttr(s+'.color'))
			engine = cmds.listConnections(s, type='shadingEngine')[0]
			cmds.select(engine)
			cmds.hyperShade(assign=variations[col])
			print('%s -> %s' % (s,variations[col]))
	if len(initial) > 0 :
		cmds.select(initial)
		
def moveVisibilityKeys() :
	transforms = cmds.ls(type='transform')
	startFrame = cmds.playbackOptions(minTime=True, q=True)
	cmds.currentTime(startFrame)
	cmds.select(cl=True)
	print('%d transforms' % len(transforms))
	for t in transforms :
		vcurv = cmds.listConnections(t+'.visibility', type='animCurve')
		if vcurv == None or len(vcurv) == 0 :
			continue
		keys = cmds.keyframe(vcurv[0], q=True)
		found = -100
		for k in keys :
			if startFrame-0.99 < k < startFrame+0.99 :
				found = k
		if found < 0 :
			continue
		cmds.currentTime(found)
		if keys.index(found) > 0 and cmds.getAttr(t+'.visibility') > 0 :
			#cmds.select(t, add=True)
			print(t, found)
			cmds.cutKey(t, time=(0, found-0.001), attribute='visibility')

def deleteHidden() :
	print('[deleteHidden]')
	transforms = cmds.ls(type='transform')
	cmds.select(cl=True)
	hidden = []
	for t in transforms :
		vcurv = cmds.listConnections(t+'.visibility', type='animCurve')
		if vcurv == None or len(vcurv) == 0 :
			continue
		keys = cmds.keyframe(vcurv[0], q=True)
		if len(keys) == 1 :
			cmds.currentTime(keys[0])
			if cmds.getAttr(t+'.visibility') == 0 :
				hidden.append(t)
	print('deleting %d objects' % len(hidden))
	cmds.delete(hidden)
			
def createShaderSets() :
	print('[createShaderSets]')
	initial = cmds.ls(sl=True)
	cmds.select(hi=True)
	mesh = cmds.ls(sl=True, type='mesh')
	shadersets = {}
	for m in mesh :
		assigned = tuple(assignedShaders(m))
		if not shadersets.has_key(assigned) :
			shadersets[assigned] = []
		shadersets[assigned].append(m)
	print(shadersets.keys())
	outset = []
	for ss in shadersets :
		for s in ss :
			outset.append(cmds.sets(shadersets[ss], n=s))
	if len(initial) > 0 :
		cmds.select(initial)
	return outset

def createBakeListFromSets(ssets, space, animated=True) :
	print('[createBakeListFromSets]')
	print('sets: %s, space: %s' % (str(ssets),space))
	outpath = os.path.join(cmds.workspace(q=True,rd=True), 'data', 'bakelist')
	if not os.path.isdir(outpath) :
		os.makedirs(outpath)
	files = []
	for sset in ssets :
		cmds.select(sset)
		members = cmds.ls(sl=True)
		bl = bakeUtils.bakeList.BakeList()
		for m in members :
			bl.addShape(m, animated=animated, space=space)
		outfile = os.path.join(outpath, '%s.bakelist'%sset)
		bl.write(outfile)
		files.append(outfile)
		print('written to: %s' % os.path.join(outpath, '%s.bakelist'%sset))
	cmds.select(cl=True)
	return files

def removeAllNamespaces() :
	print('[removeAllNamespaces]')
	cmds.namespace(setNamespace=":")
	spaces = cmds.namespaceInfo(listOnlyNamespaces=True)
	omit = ['shared', 'UI']
	for s in spaces :
		if s in omit :
			continue
		print(s)
		objs = cmds
		cmds.namespace(moveNamespace=[s, ':'], force=True)
		cmds.namespace(removeNamespace=s)

def isolateShadingEngine(engine) :
	engines = cmds.ls(type='shadingEngine')
	for e in engines :
		if e == engine :
			continue
		cmds.select(e)
		cmds.delete()
	cmds.select(cl=True)
		
def setupBake(files) :
	print('[setupBake]')
	curfile = cmds.file(q=True, sn=True)
	targetdir = os.path.join(cmds.workspace(rd=True, q=True),'data','bakelist')
	targets = {}
	for f in files :
		basename = os.path.basename(os.path.splitext(f)[0])
		newscene = os.path.join(targetdir,'%s.mb' % basename)
		targets[basename] = newscene
		bl = bakeUtils.load(f)
		cmds.rename(bl, basename+'BL')
		cmds.file(rename=newscene)
		cmds.file(save=True, type='mayaBinary')
		print('Saving to file: %s' % newscene)
	return targets

def doBake(targets, gtopath) :
	print('[doBake]')
	startFrame = cmds.playbackOptions(q=True, minTime=True)
	endFrame = cmds.playbackOptions(q=True, maxTime=True)
	for t in targets :
		print('isolating %s...' % t)
		cmds.file(targets[t], o=True, f=True)
		print(os.path.join(gtopath, t+'.gto'))
		isolateShadingEngine(t)
		print('start baking...')
		bakeUtils.bake(os.path.join(gtopath, t+'.gto'), bakeListNode=('%sBL'%t), type=bakeUtils.REF, content=bakeUtils.GEOMETRY)
		bakeUtils.bake(os.path.join(gtopath, t+'.gto'), bakeListNode=('%sBL'%t), type=bakeUtils.ANIM, content=bakeUtils.GEOMETRY, refPath=os.path.join(gtopath, t+'.gto'), frameRange=(startFrame-1, endFrame+1), samplesPerFrame=1, samplesRange=1, samplingTiming=1)
	cmds.file(rename=curfile)
		
def deleteUnused() :
	print('[deleteUnused]')
	mel.eval('MLdeleteUnused;')
	
def doSetup(gtopath) :
	root = cmds.ls(sl=True)[0]
	deleteUnused()
	removeAllNamespaces()
	deleteHidden()
	cleanupShaderAssign()
	deleteUnused()
	moveVisibilityKeys()
	cmds.select('dynamic')
	ssets = createShaderSets()
	files = createBakeListFromSets(ssets, root, animated=True)
	targets = setupBake(files)
	doBake(targets, gtopath)

