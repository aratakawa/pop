import maya.cmds as cmds
import maya.OpenMaya as om
import os

import harvester.lib.datatypes as hd
import harvester.lib.utils     as hu
import harvester.lib.functions as hf

libraryDir = os.path.join(os.environ['VE_ENV_ROOT'], os.environ['VE_ENV_PROJ'], 'team/lookdev/ShaderLibrary')
win = 'ShaderLibraryPublish'
supportedTypes = ['mzStandardShader', 'mzStandardMerge', 'mzStandardAOV', 'mzHair']

glbl = {}
glbl['startFrame'] = 1
glbl['endFrame'] = 144
glbl['byFrame'] = 1
glbl['perTask'] = 1
glbl['sys_pr'] = 10
glbl['prj_pr'] = 10
glbl['job_type'] = 'default'
glbl['title'] = 'Thumbnail Render'

glbl['cam'] = 'cam'
glbl['xres'] = 1024
glbl['yres'] = 1024
glbl['scene'] = 'thumnail.mb'

glbl['meta'] = '.meta'

def getProject() :
	return os.environ['VE_ENV_PROJ']
	
def getUser() :
	return os.environ['USERNAME']

def getGlobalMetaPath() :
	return os.path.join(libraryDir, glbl['meta']).replace('\\', '/')

def getCategoryMetaPath(category) :
	return os.path.join(libraryDir, category, glbl['meta']).replace('\\', '/')

def getAssDir(category) :
	return os.path.join(getImageDir(category), 'ass').replace('\\', '/')
def getAssPath(category, name) :
	return os.path.join(getAssDir(category), name).replace('\\', '/')
def getAssName(category, name) :
	return os.path.join(getAssPath(category, name), name+'.%04d.ass').replace('\\', '/')

def getImageDir(category) :
	return os.path.join(getCategoryPath(category), 'images').replace('\\', '/')
def getImagePath(category, name) :
	return os.path.join(getImageDir(category), name).replace('\\', '/')
def getImageName(category, name) :
	return os.path.join(getImagePath(category, name), name+'.0001.exr').replace('\\','/')
	
def getTemplatePath( category, name ) :
	if name.endswith('_ss') :
		name = name.replace('_ss', '')
	return os.path.join(libraryDir, category, name+'.ma').replace('\\', '/')

def getCategoryPath( category ) :
	return os.path.join(libraryDir, category).replace('\\', '/')

def envwrapCmd(root=None, proj=None, seq=None, shot=None, dep=None, arch=None, env_file=None, env_base=None):
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

    cmdStr = 'z:/ve/team/rnd/mzLauncher/mzenvwrap -r %s -p %s -s %s -t %s -d %s %s -a %s -- ' % (root, proj, seq, shot, dep, env_parm, arch)
    return cmdStr

def thumbAndClean(category, name) :
	import ImageLibrary
	exr = getImageName(category, name)
	png = os.path.join(getCategoryMetaPath(category), name+'.png').replace('\\','/')
	thumb = os.path.join(getCategoryMetaPath(category), name+'_thumb.png').replace('\\','/')
	print('[%s] converting exr to png %s->%s' % (win, exr, png))
	ImageLibrary.format(exr, png, gamma='2.2')
	print('[%s] resizing png to thumb %s->%s' % (win, png, thumb))
	ImageLibrary.resize(png, thumb, size='256x256')
	# cleanup
	import shutil
	imgdir = getImagePath(category, name)
	assdir = getAssPath(category, name)
	#print('[%s] removing images files. %s' % (win, imgdir)
	#shutil.rmtree(imgdir)
	print('[%s] removing ass files. %s' % (win, assdir))
	shutil.rmtree(assdir)
	pass

def postProcess(category, name, originalName=None) :
	fset = hu.frameSet('%d-%d/%d:%d' % (glbl['startFrame'], glbl['endFrame'], glbl['byFrame'], glbl['perTask']))
	hjob = hd.Job(system_priority = glbl['sys_pr'],
					project_priority = glbl['prj_pr'] ,
					job_type = glbl['job_type'] ,
					title = glbl['title'],
					frame_range_str = hu.frameStr(fset),
					total_frame = len(fset['frameList']),
					render_layer='layer',
					max_process=0,
					timeout=120,
					output='/tmp',
					message=''
					)
	# clean up task
	ccmd = envwrapCmd()
	ccmd += 'mayabatch -command "python(\\\"import ShaderLibraryPublish as slp; slp.cleanupSceneTask(\'%s\', \'%s\');\\\")"' % (category, name)
	print(ccmd)
	cfold = hd.Folder(threads = -2,
						title='cleanup',
						frame_range_str='1-1',
						total_frame=1,
						output=getCategoryPath(category),
						tags=['maya'],
						environ={}
						)
	ctask = hd.Task(title='cleanup',
						command=ccmd,
						frame_range_str='1-1',
						total_frame=1,
						output=getCategoryPath(category),
						dependencies=None
					)
	cfold.append(ctask)
	hjob.append(cfold)
						
	# ass gen task
	afold = hd.Folder(threads = -2,
						title='.ass generator',
						frame_range_str=hu.frameStr(fset),
						total_frame=hjob.total_frame,
						output=getCategoryPath(category),
						tags=['maya', 'arnold'],
						environ={}
						)
						
	rd = getImagePath(category, name)
	if not os.path.isdir(rd) :
		os.makedirs(rd)
	assDir = getAssPath(category, name)
	if not os.path.isdir(assDir) :
		os.makedirs(assDir)
	for sf, ef, bf, cf in fset['parTask'] :
		for f in range(sf, ef+1, bf) :
			acmd = envwrapCmd()
			acmd += 'Render -r arnoldExport'
			acmd += ' -execPy "import ShaderLibraryPublish as slp;slp.setupRender(\\\"%s\\\", \\\"%s\\\")"' % (category, name)
			acmd += ' -s %d -e %d -b 1 -pad 4' % (f,f)
			acmd += ' -x %d -y %d' % (glbl['xres'], glbl['yres'])
			acmd += ' -cam "%s"' % glbl['cam']
			#acmd += ' -proj '
			acmd += ' -rd "%s"' % rd
			acmd += ' -im "%s"' % (name)
			acmd += ' -assDir "%s"' % assDir
			acmd += ' -assPrefix "%s"' % (name)
			acmd += ' "%s"' % os.path.join(getGlobalMetaPath(), 'thumbnail.mb').replace('\\','/')
			print(acmd)
			atask = hd.Task(title='.ass generator',
								command=acmd,
								frame_range_str='%d-%d' % (f,f),
								total_frame=1,
								output=getCategoryPath(category),
								dependencies=[ctask]
							)
			afold.append(atask)
	hjob.append(afold)
	
	# render task
	rfold = hd.Folder(threads = -2,
						title='rendering with arnold',
						frame_range_str=hu.frameStr(fset),
						total_frame=hjob.total_frame,
						output=getCategoryPath(category),
						tags=['ren', 'arnold'],
						environ={}
						)
	id = 0
	for sf, ef, bf, cf in fset['parTask'] :
		for f in range(sf, ef+1, bf) :
			rcmd = envwrapCmd()
			rcmd += 'mzkick -dp -dw -t $HARVESTER_THREADS -v 5'
			rcmd += ' -mc "%s"' % glbl['cam']
			rcmd += ' -sf %d -ef %d -fs 1' % (f,f)
			rcmd += ' -set options.abort_on_license_fail true'
			rcmd += ' -i "%s"' % getAssName(category, name)
			rcmd += ' -assf mzRenderForMaya_makeTxMode.py reuse @'
			print(rcmd)
			rtask = hd.Task(title='rendering with arnold',
								command=rcmd,
								frame_range_str='%d-%d' % (f,f),
								total_frame=1,
								output=getCategoryPath(category),
								dependencies=[afold.tasks[id]]
							)
			rfold.append(rtask)
		id += 1
	hjob.append(rfold)
	
	# movie encoding
	mfold = hd.Folder(threads = -2,
						title='exr to qt',
						frame_range_str=hu.frameStr(fset),
						total_frame=hjob.total_frame,
						output=getCategoryPath(category),
						tags=['ren'],
						environ={}
						)
	mcmd = envwrapCmd()
	mcmd += 'mzTranscoder %s %s' % (getImageName(category, name), os.path.join(getImageDir(category), name+'.mov').replace('\\','/'))
	print(mcmd)
	mtask = hd.Task(title='exr to qt',
					command=mcmd,
					frame_range_str=hu.frameStr(fset),
					total_frame=hjob.total_frame,
					output=getCategoryPath(category),
					)
	#mtask.dependencies = []
	for rt in rfold.tasks :
		mtask.dependencies.append(rt)

	mfold.append(mtask)
	hjob.append(mfold)
	
	# thumbnail & cleanup
	tfold = hd.Folder(threads=-2,
						title='thumbnail and cleanup',
						frame_range_str='1-1',
						total_frame=1,
						output=getCategoryPath(category),
						tags=['ren'],
						environ={}
						)
	tcmd = envwrapCmd()
	tcmd += 'python -c "import ShaderLibraryPublish as slp; slp.thumbAndClean(\'%s\', \'%s\')"' % (category, name)
	print(tcmd)
	ttask = hd.Task(title='thumbnail and cleanup',
					command=tcmd,
					frame_range_str='1-1',
					total_frame=1,
					output=getCategoryPath(category),
					dependencies=[mtask]
					)
	tfold.append(ttask)
	hjob.append(tfold)
	
	# submit
	proj = getProject()
	seq = 'PROJ'
	shot = 'ALL'
	user = getUser()
	hf.save([hjob], user, proj, seq, shot, host='harvester4', port='80')
	pass
	

def setupRender(category, name) :
	cmds.select('target_sg')
	objs = cmds.ls(sl=True)
	cmds.file(getTemplatePath(category, name), r=True, ns='%s_%s' % (category, name))
	cmds.select(objs)
	cmds.sets(e=True, forceElement='%s_%s:%s' % (category, name, name+'_sg'))
	
def cleanShaderNames(engine, name) :
	ss = cmds.listConnections(engine+'.surfaceShader')
	if not ss :
		om.MGlobal.displayError('[%s] ######## No surface shader found. ########' % win)
		return False
	ds = cmds.listConnections(engine+'.displacementShader')
	ss = ss[0]
	cmds.rename(ss, name+'_ss')
	cmds.rename(engine, name+'_sg')
	if ds :
		cmds.rename(ds, name+'_ds')
	return True

def cleanTextureNames() :
	for f in cmds.ls(type='file') :
		path = cmds.getAttr(f+'.fileTextureName')
		name = os.path.split(path)[-1].split('.')[0]
		cmds.rename(f, name)
	return True

def cleanupScene(name) :
	omit = ['initialParticleSE', 'initialShadingGroup']
	engines = cmds.ls(type='shadingEngine')
	target = None
	for e in engines :
		if e not in omit :
			target = e
	if not target :
		om.MGlobal.displayError('[%s] ######## No Target Found. ########' % win)
		return
	if not cleanShaderNames(target, name) :
		return
	if not cleanTextureNames() :
		return
	print('[%s] Cleanup done.' % win)

def copyTextures(category) :
	import veTexShaderManager as tsm
	tsm.copyTexturesAndSetPath(os.path.join(getCategoryPath(category), 'textures').replace('\\', '/'), relative=False)

def cleanupSceneTask(category, name) :
	cmds.file(getTemplatePath(category, name), o=True, f=True)
	cleanupScene(name)
	copyTextures(category)
	cmds.file(f=True, s=True)
	pass

def createCategory(args) :
	res = cmds.promptDialog(title='Create Category', message='New Category:', button=['Create', 'Cancel'], defaultButton='Create', cancelButton='Cancel', dismissString='Cancel')
	if res == 'Create' :
		name = cmds.promptDialog(q=True, text=True)
		if name == '' :
			om.MGlobal.displayError('Invlid category name.')
		else :
			name = name.lower()
			if os.path.isdir(os.path.join(libraryDir, name)) :
				om.MGlobal.displayError('Category already exists: %s' % name)
			else :
				os.makedirs(os.path.join(libraryDir, name, 'textures'))
				os.makedirs(os.path.join(libraryDir, name, glbl['meta']))

def shaderNameIsValid(name) :
	names = name.split('_')
	print(names)
	if len(names) == 2 and names[-1] == 'ss' :
		return True
	return False

def checkValidity(args) :
	selected = cmds.ls(sl=True)
	isValid = True

	name = ''
	if not len(selected) > 0 :
		om.MGlobal.displayError("Nothing selected. Please select a shadeingEngine to publish.")
		isValid = False
	else :
		ss = cmds.listConnections(selected[0]+'.surfaceShader')
		if not ss :
			om.MGlobal.displayError('No shader is connected to this shadingEngine.')
			isValid = False
		else :
			name = ss[0]
	pubname = cmds.textFieldGrp(win+'Shader', q=True, text=True)
	if pubname != '' :
		name = pubname
	cmds.textFieldGrp(win+'Shader', e=True, text=name)
	if not shaderNameIsValid(name) :
		om.MGlobal.displayError("Shader name is not valid.")
		isValid = False
	
	if not isValid :
		cmds.button(win+'Publish', e=True, enable=False)
	else :
		cmds.button(win+'Publish', e=True, enable=True)

def doPublish(args) :
	global win
	attr = 'shaderLibrary'
	print('[%s] publish' % win)
	category = cmds.optionMenuGrp(win+'Category', q=True, value=True)
	name = cmds.textFieldGrp(win+'Shader', q=True, text=True)
	message = '[%s]\n\n[Category]\t%s\n[Name]\t%s\n' % (win, category, name)
	res = cmds.confirmDialog( title='Confirm', message=message, button=['Yes','Cancel'], defaultButton='Yes', cancelButton='Cancel', dismissString='Cancel' )
	if res == 'Yes' :
		selected = cmds.ls(sl=True)[0]
		if not cmds.attributeQuery(attr, node=selected, ex=True) :
			cmds.addAttr(selected, ln=attr, sn=attr, dt='string')
		message = str({'category':category, 'name':name})
		print(message)
		cmds.setAttr(selected+'.'+attr, message, type='string')
		cmds.file(os.path.join(libraryDir, category, name.replace('_ss', '')+'.ma'), type='mayaAscii', force=True, es=True)
		postProcess(category, name.replace('_ss', ''))

def getCategories() :
	dirs = os.listdir(libraryDir)
	categories = []
	for d in dirs :
		if not d.startswith('.') :
			categories.append(d)
	categories.sort()
	return categories

def refreshUI(args) :
	if cmds.layout(win+'RootLayout', q=True, ex=True) :
		cmds.deleteUI(win+'RootLayout')
	createBodyUI()
	
def createBodyUI() :
	global win, supportedTypes
	cmds.setParent(win)
	cmds.columnLayout(win+'RootLayout', adj=True)
	cmds.button(win+'Refresh', label='Refresh', c=refreshUI)
	cmds.separator()
	cmds.text(label='')
	cmds.optionMenuGrp(win+'Category', label='Category')
	categories = getCategories()
	for c in categories :
		cmds.menuItem(label=c)
	cmds.textFieldGrp(win+'Shader', label='Publish Name', text='', cc=checkValidity)
	cmds.text(label='')
	cmds.separator()
	cmds.button(win+'Publish', label='Publish', c=doPublish)
	checkValidity('dummy')
	

def ui() :
	global win
	if cmds.window(win, q=True, ex=True) :
		cmds.deleteUI(win, window=True)
	if cmds.windowPref(win, ex=True) :
		cmds.windowPref(win, remove=True)
	cmds.window(win, menuBar=True, widthHeight=(500,200))
	cmds.menu(label='Advanced')
	cmds.menuItem('CreateNewCategory', c=createCategory)
	createBodyUI()
	cmds.showWindow(win)
	