import maya.cmds as cmds
import maya.mel as mel
import os, shutil, time
import bakeUtils

import harvester.lib.datatypes as hd
import harvester.lib.wrapper as hw
import harvester.lib.utils as hu
import harvester.lib.functions as hf
import harvester.common.constants as hc

class debrisCleaner(object) :
	def __init__(self, root, outpath) :
		self.root = root
		self.outpath = outpath
		self.tempdir = os.path.join(self.outpath, 'temp')
		self.shaders = []
		self.shaderset = {}
		if not os.path.isdir(self.tempdir) :
			os.makedirs(self.tempdir)
	def deleteUnused(self) :
		print('[deleteUnused]')
		mel.eval('MLdeleteUnused;')
	def getShaders(self) :
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
	def assignedShaders(self, mesh) :
		assigned = cmds.listConnections(mesh, type='shadingEngine')
		if assigned == None :
			cmds.error('[ERROR] no shader assgned to shape: %s' % mesh)
			cmds.hyperShade(assign='lambert1')
			return []
		return set(assigned)
	def assignedShadersH(self) :
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
	def removeAllNamespaces(self) :
		print('[removeAllNamespaces]')
		cmds.namespace(setNamespace=":")
		spaces = cmds.namespaceInfo(listOnlyNamespaces=True)
		omit = ['shared', 'UI']
		while(len(spaces) > 2) :
			for s in spaces :
				if s in omit :
					continue
				print(s)
				objs = cmds
				cmds.namespace(moveNamespace=[s, ':'], force=True)
				cmds.namespace(removeNamespace=s)
			spaces = cmds.namespaceInfo(listOnlyNamespaces=True)
	def deleteHidden(self) :
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
		if len(hidden) > 0 :
			cmds.delete(hidden)
	def timestamp(self) :
		return int(time.time())
	def saveToTemp(self, baketype) :
		curfile = cmds.file(q=True, sn=True)
		newscene = os.path.join(self.tempdir, 'debrisCleaner_%s_%d.mb' % (baketype,self.timestamp()))
		cmds.file(rename=newscene)
		cmds.file(save=True, type='mayaBinary')
		cmds.file(rename=curfile)
		print('[saveToTemp] %s' % newscene)
		return newscene
	def cleanupShaderAssign(self) :
		initial = cmds.ls(sl=True)
		cmds.select(cl=True)
		shaders = self.getShaders()
		variations = {}
		supported = ['lambert', 'phong', 'blinn']
		for s in shaders :
			if not cmds.objectType(s) in supported :
				continue
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
	def moveVisibilityKeys(self) :
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
	def createShaderSets(self, baketype) :
		print('[createShaderSets]')
		initial = cmds.ls(sl=True)
		cmds.select(baketype)
		cmds.select(hi=True)
		mesh = cmds.ls(sl=True, type='mesh')
		shadersets = {}
		for m in mesh :
			assigned = tuple(self.assignedShaders(m))
			for a in assigned :
				if not shadersets.has_key(a) :
					shadersets[a] = []
				shadersets[a].append(m)
		print(shadersets.keys())
		outset = []
		for ss in shadersets :
			outset.append(cmds.sets(shadersets[ss], n='%s_%s'%(baketype,ss)))
		if len(initial) > 0 :
			cmds.select(initial)
		return outset
	def createBakeListFromSets(self, baketype) :
		ssets = self.shaderset[baketype]
		animated = False
		if baketype == 'dynamic' :
			animated = True
		print('[createBakeListFromSets]')
		print('sets: %s, space: %s' % (str(ssets),self.root))
		files = []
		for sset in ssets :
			cmds.select(sset)
			members = cmds.ls(sl=True)
			bl = bakeUtils.bakeList.BakeList()
			for m in members :
				bl.addShape(m, animated=animated, space=self.root)
			outfile = os.path.join(self.tempdir, '%s.bakelist'%sset)
			bl.write(outfile)
			files.append(outfile)
			print('written to: %s' % outfile)
		cmds.select(cl=True)
		return files
	def cleanup(self) :
		self.deleteUnused()
		self.removeAllNamespaces()
		self.deleteHidden()
		#self.cleanupShaderAssign()
		self.deleteUnused()
		self.moveVisibilityKeys()
	def getUsername(self):
		import getpass
		user = getpass.getuser()
		if 'USER' in os.environ:
			user = os.environ['USER']
		elif 'USERNAME' in os.environ:
			user = os.environ['USERNAME']
		return user
	def venvwrapCmd(self, root=None, proj=None, seq=None, shot=None, dep=None, arch=None, env_file=None, env_base=None):
		if not root:
			root = os.environ.get('VE_ENV_ROOT','z:/marza/proj')
		if not proj:
			proj = os.environ.get('VE_ENV_PROJ','onyx')
		if not seq:
			seq  = os.environ.get('VE_ENV_SEQ','PROJ')
		if not shot:
			shot = os.environ.get('VE_ENV_SHOT','ALL')
		if not dep:
			dep  = os.environ.get('VE_ENV_DEPT','ALL')

		env_parm = ''
		cur_env_bases = os.environ.get('VE_ENV_BASES','houdini11_1_22_nw')
		cur_env_file = os.environ.get('VE_ENV_FILE','')
		if env_base:
			env_parm = ' -n '+env_base
			if cur_env_bases==env_base and cur_env_file!='':
				env_parm = ' -f '+cur_env_file
		else:
			if env_file:
				env_parm = ' -f '+env_file
			else:
				if cur_env_file:
					env_parm = ' -f '+cur_env_file
				else:
					env_parm = ' -n '+cur_env_bases
		if not arch:
			arch = os.environ.get('VE_ARCH','x64')
		cmdStr = 'z:/ve/team/rnd/mzLauncher/venvwrap.exe -r %s -p %s -s %s -t %s -d %s %s -a %s -- ' % (root, proj, seq, shot, dep, env_parm, arch)
		return cmdStr
	def bake(self, baketype):
		#cmds.select(type)
		self.shaderset[baketype] = self.createShaderSets(baketype)
		self.createBakeListFromSets(baketype)
		scene = self.saveToTemp(baketype)
		scenename = os.path.split(scene)[-1]
		cmd = self.venvwrapCmd() + r'mayabatch -command "python(\"import debrisCleaner as dc;baker = dc.debrisBaker(\\\"%s\\\", \\\"%s\\\", \\\"%s\\\", \\\"%s\\\");baker.doBake()\")"'
		#cmd = self.venvwrapCmd() + r'mayapy -c "import maya.standalone as ms;ms.initialize();import debrisCleaner as dc;baker = dc.debrisBaker(\"%s\", \"%s\", \"%s\", \"%s\");baker.doBake()"'
		fset = hu.frameSet('%d-%d/%d:%d' % (1, 1, 1, 1))
		# submit harvester
		job = hd.Job(system_priority=10,
					project_priority=10,
					priority=10,
					title='gto',
					job_type='default',
					frame_range_str=hu.frameStr(fset),
					total_frame=len(fset['frameList']),
					render_layer='layer?',
					max_process=0,
					timeout=120,
					output=self.outpath,
					message='')
		tags = ['maya']		
		env = {}
		for s in self.shaderset[baketype] :
			title = 'bake %s' % s
			command = cmd % (s, self.outpath, scenename, baketype)
			print(command)
			folder = hd.Folder(threads=hc.threads.HALF,
								title=title,
								frame_range_str=job.frame_range_str,
								total_frame=job.total_frame,
								output=self.outpath,
								tags=tags,
								environ=env
								)
			task = hd.Task(title=title,
							command=command,
							frame_range=hu.frameStr('1-1\1'),
							total_frame = 1,
							output = self.outpath,
							dependencies=None
							)
			folder.append(task)
			job.append(folder)
		user = self.getUsername()
		proj = os.environ.get('VE_ENV_PROJ','onyx')
		seq  = os.environ.get('VE_ENV_SEQ','PROJ')
		shot = os.environ.get('VE_ENV_SHOT','ALL')
		result = hf.save([job], user, proj, seq, shot, host='harvester4', port='80')
		print(result)
			
			
class debrisBaker(object):
	def __init__(self, target, outpath, scene, baketype) :
		self.outpath = outpath
		self.tempdir = os.path.join(outpath, 'temp')
		self.scene = os.path.join(self.tempdir, scene)
		self.target = target
		self.baketype = baketype
	def isolateShadingEngine(self, engine) :
		engine = engine.replace('%s_'%self.baketype, '')
		engines = cmds.ls(type='shadingEngine')
		counter = 1
		for e in engines :
			print('Processing %s(%d/%d)' % (e,counter,len(engines)))
			counter += 1
			if e == engine :
				continue
			cmds.select(e)
			cmds.delete()
		cmds.select(cl=True)
	def saveToTemp(self) :
		curfile = cmds.file(q=True, sn=True)
		newscene = os.path.splitext(curfile)
		newscene = '%s_%s.mb' % (newscene, self.target)
		cmds.file(rename=newscene)
		cmds.file(save=True, type='mayaBinary')
	def doBake(self) :
		print('[doBake]')
		# open scene, load bakelist
		cmds.file(self.scene, o=True, f=True)
		bakelist = os.path.join(self.tempdir, self.target+'.bakelist')
		bl = bakeUtils.load(bakelist)
		bnode = self.target+'BL'
		cmds.rename(bl, bnode)
		startFrame = cmds.playbackOptions(q=True, minTime=True)
		endFrame = cmds.playbackOptions(q=True, maxTime=True)
		# delete everything except target
		print('isolating %s...' % self.target)
		self.isolateShadingEngine(self.target)
		# bake to gto
		print('start baking %s... '%self.baketype)
		refgto = os.path.join(self.outpath, self.target+'.gto')
		print(refgto)
		cmds.currentTime(startFrame)
		bakeUtils.bake(refgto, bakeListNode=(bnode), type=bakeUtils.REF, content=bakeUtils.GEOMETRY)
		if(self.baketype=='dynamic') :
			bakeUtils.bake(refgto, bakeListNode=(bnode), type=bakeUtils.ANIM, content=bakeUtils.GEOMETRY, refPath=refgto, frameRange=(startFrame-1, endFrame+1), samplesPerFrame=1, samplesRange=1, samplingTiming=1)
		print('[done baking]')
		self.saveToTemp()

def mergeDebris(path) :
	files = os.listdir(path)
	ma = []
	for f in files :
		if f.endswith('.ma') :
			ma.append(f)
	cmds.file(new=True,f=True)
	for m in ma :
		print('Loading %s...' % m)
		cmds.file(os.path.join(path,m), i=True, ns=os.path.splitext(m)[0])

def assignShadersByName() :
	print('[assignShadersByName]')
	import gtoUtils.materialEditor as me
	engines = cmds.ls(type='shadingEngine')
	locators = cmds.ls(type='gtoLocator')
	for e in engines :
		print('Assigning %s' % e)
		for l in locators :
			if e in l :
				shader = cmds.listConnections(e+'.surfaceShader')[0]
				me.setGtoLocatorShader(l, shader)
def setGeomAttrs() :
	print('[setGeomAttrs]')
	import fx_tokargaDebris as td
	locators = cmds.ls(type='gtoLocator')
	for l in locators :
		td.setAttrs(l)