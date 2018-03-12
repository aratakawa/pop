import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as om
import os, getpass, time, shutil

import harvester.lib.datatypes as hd
import harvester.lib.utils     as hu
import harvester.lib.functions as hf

def getProject() :
	return os.environ['VE_ENV_PROJ']

def getUser() :
    return getpass.getuser()

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
    cur_env_bases = os.environ.get('VE_ENV_BASES','maya2013')
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

def getDefaultTokens() :
	tokens = {}
	tokens['margin'] = 1.1
	tokens['resolution'] = 1024
	tokens['imagePrefix'] = 'frustum_txDnsMap'
	tokens['maxDist'] = 1000
	tokens['dmapResolution'] = 2048
	tokens['clipByResolution'] = True
	tokens['renderer'] = 'mentalray'
	tokens['ndotl'] = False
	return tokens

def getFrameRange() :
	return (cmds.playbackOptions(q=True, minTime=True), cmds.playbackOptions(q=True, maxTime=True))

def saveToTemp(outpath) :
	scene = cmds.file(q=True, sn=True)
	base = 	os.path.basename(scene)
	bext = os.path.splitext(base)
	timestamp = time.time()
	tmpscene = os.path.join(outpath, bext[0]+str(timestamp)+bext[-1]).replace('\\','/')
	cmds.file(rename=tmpscene)
	cmds.file(save=True)
	cmds.file(rename=scene)
	print(tmpscene)
	return tmpscene

def bakeFrustum(camera, targetobj, outpath, frameRange=None, tokens=None, dispatch=False) :
	if not tokens :
		tokens = getDefaultTokens()
	if dispatch :
		scenepath = os.path.join(outpath, 'scenes').replace('\\', '/')
		if not os.path.isdir(scenepath) :
			os.makedirs(scenepath)
		bkscene = cmds.file(q=True, sn=True)
		tmpscene = saveToTemp(scenepath)
		mproj = cmds.workspace(q=True, rd=True)
		if not frameRange :
			frameRange = getFrameRange()
		htokens = {}
		htokens['startFrame'] = frameRange[0]
		htokens['endFrame'] = frameRange[1]
		htokens['byFrame'] = 1
		htokens['perTask'] = 1
		htokens['sys_pr'] = 10
		htokens['prj_pr'] = 10
		htokens['job_type'] = 'default'
		htokens['title'] = 'Frustum Bake'
		fset = hu.frameSet('%d-%d/%d:%d' % (htokens['startFrame'], htokens['endFrame'], htokens['byFrame'], htokens['perTask']))
		hjob = hd.Job(system_priority = htokens['sys_pr'],
				project_priority = htokens['prj_pr'] ,
				job_type = htokens['job_type'] ,
				title = htokens['title'],
				frame_range_str = hu.frameStr(fset),
				total_frame = len(fset['frameList']),
				render_layer='layer',
				max_process=0,
				timeout=120,
				output='/tmp',
				message=''
				)
		cmd = envwrapCmd()
		#cmd += 'mayabatch -proj "%s" -file "%s" -command "python(\\\"import frustum;frustum.bakeFrustum(\'%s\', \'%s\', \'%s\', frameRange=%s, tokens=%s)\\")"' % (mproj, tmpscene, camera, targetobj, outpath, str(frameRange), str(tokens));
		cmd += 'mayabatch -proj "%s" -file "%s" -command "python(\\\"import frustum;frustum.bakeFrustum(\'%s\', \'%s\', \'%s\', frameRange=%s, tokens=%s)\\")"'
		#cmd += 'Render -r lightmap -rd "%s" -sel %s -override 1 -colorMode 0 -xResolution %d -yResolution %d -fileFormat tif -prefix %s %s'
		print(cmd)
		hfold = hd.Folder(threads = -2,
							title=htokens['title'],
							frame_range_str='1-1',
							total_frame=1,
							output=outpath,
							tags=['maya'],
							environ={}
							)
		for i in range(htokens['startFrame'], htokens['endFrame']+1) :
			htask = hd.Task(title=htokens['title'],
								command=cmd % (mproj, tmpscene, camera, targetobj, outpath, '(%d,%d)' % (i,i), str(tokens)),
								#frame_range_str='%d-%d' % (htokens['startFrame'], htokens['endFrame']),
								frame_range_str='%d-%d' % (i, i),
								total_frame=1,
								output=outpath,
								dependencies=None
							)
			hfold.append(htask)
		hjob.append(hfold)
		
		proj = getProject()
		user = getUser()
		seq = 'PROJ'
		shot = 'ALL'
		result = hf.save([hjob], user, proj, seq, shot, host='harvester4', port='80')
		cmds.confirmDialog( title='Done.', message='Harvester Job ID: '+str(result), button=['OK'])
							
	else :
		dren = 'defaultRenderGlobals'
		bkStart = cmds.getAttr(dren+'.startFrame')
		bkEnd = cmds.getAttr(dren+'.endFrame')
		cmds.setAttr(dren+'.startFrame', 1)
		cmds.setAttr(dren+'.endFrame', 1)
		createdNodes = []
		engine = cmds.listConnections(targetobj, type='shadingEngine')
		if not engine :
			om.displayError('shadingEngine missing failed.')
			if createdNodes :
				cmds.delete(createdNodes)
			return
		engine = engine[0]
		assigned = cmds.listConnections(engine+'.surfaceShader')[0]
		shader = assigned
		if not cmds.attributeQuery('isFrustumBakeShader', n=assigned, ex=True) :
			createdNodes.extend(createFrustumShader(camera, tokens))
			shader = cmds.ls(sl=True)
			if not shader :
				om.displayError('CreateFrustumShader failed.')
				if createdNodes :
					cmds.delete(createdNodes)
				return
			shader = shader[0]
			cmds.connectAttr(shader+'.outColor', engine+'.surfaceShader', f=True)
			bakeShader(targetobj, camera, outpath, frameRange=frameRange, tokens=tokens)
		print('Revert connection: %s -> %s' % (assigned, engine))
		if shader != assigned :
			cmds.connectAttr(assigned+'.outColor', engine+'.surfaceShader', f=True)
			cmds.delete(createdNodes)
		cmds.setAttr(dren+'.startFrame', bkStart)
		cmds.setAttr(dren+'.endFrame', bkEnd)
		print(createdNodes)

def createFrustumShader(camera, tokens=None) :
	if not tokens :
		tokens = getDefaultTokens()
	if cmds.objectType(camera) != "camera" :
		print('Parameter must be a camera shape.')
		return
	camTrans = cmds.listRelatives(camera, f=True, p=True)[0]
	createdNodes = []
	ss = cmds.shadingNode('surfaceShader', asShader=True)
	ss = cmds.rename(ss, 'FrustumBakeShader')
	createdNodes.append(ss)
	cmds.addAttr(ss, ln='isFrustumShader', at='bool')
	cmds.setAttr(ss+'.isFrustumShader', e=True, keyable=True)
	cmds.setAttr(ss+'.isFrustumShader', 1)
	md = cmds.shadingNode('multiplyDivide', asUtility=True)
	createdNodes.append(md)
	cmds.connectAttr(md+'.output', ss+'.outColor')
	md2 = cmds.shadingNode('multiplyDivide', asUtility=True)
	createdNodes.append(md2)
	cmds.connectAttr(md2+'.output', md+'.input1')
	# camera frustum projection
	pj = cmds.shadingNode('projection', asUtility=True)
	createdNodes.append(pj)
	cmds.setAttr(pj+'.projType', 8) # perspective
	cmds.setAttr(pj+'.fitFill', 1) # horizontal
	cmds.setAttr(pj+'.fitType', 1) # film gate
	cmds.setAttr(pj+'.defaultColor', 0, 0, 0)
	wramp = cmds.shadingNode('ramp', asTexture=True)
	createdNodes.append(wramp)
	cmds.removeMultiInstance(wramp+'.colorEntryList[1]', b=True)
	cmds.removeMultiInstance(wramp+'.colorEntryList[2]', b=True)
	cmds.setAttr(wramp+'.defaultColor', 0, 0, 0)
	p2d = cmds.shadingNode('place2dTexture', asUtility=True)
	createdNodes.append(p2d)
	cmds.connectAttr(p2d+'.outUV', wramp+'.uv')
	cmds.connectAttr(p2d+'.outUvFilterSize', wramp+'.uvFilterSize')
	cmds.connectAttr(wramp+'.outColor', pj+'.image')
	cmds.setAttr(p2d+'.wrapU', 0)
	cmds.setAttr(p2d+'.wrapV', 0)
	# camera distance falloff
	dramp = cmds.shadingNode('ramp', asTexture=True)
	createdNodes.append(dramp)
	cmds.setAttr(wramp+'.colorEntryList[0].color', 1, 1, 1)
	cmds.removeMultiInstance(dramp+'.colorEntryList[1]', b=True)
	cmds.setAttr(dramp+'.colorEntryList[0].color', 1, 1, 1)
	cmds.setAttr(dramp+'.colorEntryList[2].color', 0, 0, 0)
	cmds.setAttr(dramp+'.colorEntryList[2].position', 1)
	cmds.setAttr(dramp+'.interpolation', 3)
	cmds.setAttr(dramp+'.defaultColor', 0, 0, 0)
	flipz = cmds.shadingNode('multiplyDivide', asUtility=True)
	createdNodes.append(flipz)
	sinfo = cmds.shadingNode('samplerInfo', asUtility=True)
	createdNodes.append(sinfo)
	srange = cmds.shadingNode('setRange', asUtility=True)
	createdNodes.append(srange)
	cmds.connectAttr(sinfo+'.pointCamera', flipz+'.input1')
	cmds.setAttr(flipz+'.input2Z', -1)
	cmds.connectAttr(flipz+'.output', srange+'.value')
	cmds.setAttr(srange+'.maxX', 1)
	cmds.setAttr(srange+'.maxY', 1)
	cmds.setAttr(srange+'.maxZ', 1)
	cmds.setAttr(srange+'.oldMaxZ', tokens['maxDist'])
	cmds.connectAttr(srange+'.outValueZ', dramp+'.vCoord')
	# light projection
	light = cmds.shadingNode('spotLight', asLight=True)
	createdNodes.append(light)
	cmds.setAttr(light+'.coneAngle', 100)
	cmds.setAttr(light+'.useDepthMapShadows', 1)
	cmds.setAttr(light+'.dmapResolution', tokens['dmapResolution'])
	cmds.pointConstraint(camTrans, light, weight=1)
	cmds.orientConstraint(camTrans, light, weight=1)
	lambert = cmds.shadingNode('lambert', asShader=True)
	createdNodes.append(light)
	cmds.setAttr(lambert+'.color', 1 ,1 ,1)
	cmds.setAttr(lambert+'.diffuse', 1)
	lramp = cmds.shadingNode('ramp', asTexture=True)
	createdNodes.append(lramp)
	cmds.removeMultiInstance(lramp+'.colorEntryList[1]', b=True)
	cmds.setAttr(lramp+'.colorEntryList[0].color', 0, 0, 0)
	cmds.setAttr(lramp+'.colorEntryList[2].color', 1, 1, 1)
	if tokens['ndotl'] :
		cmds.setAttr(lramp+'.colorEntryList[2].position', 0.3)
	else :
		cmds.setAttr(lramp+'.colorEntryList[2].position', 0.01)
	cmds.setAttr(lramp+'.interpolation', 3)
	cmds.setAttr(lramp+'.defaultColor', 0, 0, 0)
	cmds.connectAttr(lambert+'.outColorR', lramp+'.vCoord')
	# merge three
	cmds.connectAttr(pj+'.outColor', md2+'.input1')
	cmds.connectAttr(dramp+'.outColor', md2+'.input2')
	cmds.connectAttr(lramp+'.outColor', md+'.input2')
	
	# connect camera
	cmds.connectAttr(camera+'.message', pj+'.linkedCamera')
	cmds.select(ss)
	return createdNodes

def bakeShader(targetobj, camera, outpath, frameRange=None, tokens=None) :
	if not tokens :
		tokens = getDefaultTokens()
	if not targetobj :
		om.displayError('Please select a shader to bake.')
		return
	sg = cmds.listConnections(targetobj, type='shadingEngine')
	if not sg :
		om.displayError('No shadingEngine found to bake.')
		return
	ss = cmds.listConnections(sg[0]+'.surfaceShader')
	if not ss :
		om.displayError('No surfaceShader found to bake.')
		return
	plug = cmds.listConnections(ss[0]+'.outColor', p=True)
	if not plug :
		om.displayError('No plug found to bake.')
		return 
	print(plug[0])
	if not frameRange :
		frameRange = getFrameRange()
		print(frameRange)
	# modify film back
	dres = 'defaultResolution'
	bkResX = cmds.getAttr(dres+'.width')
	bkResY = cmds.getAttr(dres+'.height')
	bkApertureH = cmds.getAttr(camera+'.horizontalFilmAperture')
	bkApertureV = cmds.getAttr(camera+'.verticalFilmAperture')
	apertureH = bkApertureH * tokens['margin']
	apertureV = bkApertureV * tokens['margin']
	if tokens['clipByResolution'] :
		pratio = bkResX / bkResY
		apertureV = apertureH / pratio
	conn = cmds.listConnections(camera+'.horizontalFilmAperture', p=True, s=True)
	if conn != None and len(conn) > 0 :
		cmds.disconnectAttr(conn[0], camera+'.horizontalFilmAperture')
	conn = cmds.listConnections(camera+'.verticalFilmAperture', p=True, s=True)
	if conn != None and len(conn) > 0 :
		cmds.disconnectAttr(conn[0], camera+'.verticalFilmAperture')
	cmds.setAttr(camera+'.horizontalFilmAperture', apertureH)
	cmds.setAttr(camera+'.verticalFilmAperture', apertureV)
	for i in range(frameRange[0], frameRange[1]+1) :
		#cmds.dgdirty(a=True)
		projections = cmds.ls(type='projection')
		file = '%s.%04d.tif' % (tokens['imagePrefix'], i)
		file = os.path.join(outpath, file).replace('\\', '/')
		print(file)
		cmds.currentTime(i, update=True, e=True)
		if cmds.about(batch=True) or tokens['renderer'] == 'mentalray' :
			if not cmds.pluginInfo('Mayatomr', q=True, loaded=True) :
				cmds.loadPlugin('Mayatomr')
			ibs = 'initialTextureBakeSet'
			if not cmds.objExists(ibs) :
				cmds.createNode('textureBakeSet', n=ibs)
				cmds.sets(targetobj, e=True, forceElement=ibs)
				#bset = mel.eval('createAndAssignBakeSet textureBakeSet %s' % targetobj)
			ldir = cmds.workspace(q=True, rd=True)
			ldir = os.path.join(ldir, 'renderData/mentalray/lightMap').replace('\\', '/')
			cmds.setAttr(ibs+'.xResolution', tokens['resolution'])
			cmds.setAttr(ibs+'.yResolution', tokens['resolution'])
			targetp = cmds.listRelatives(targetobj, p=True)[0]
			tempobj = cmds.rename(targetp, targetp+'%04d'%i)
			print('Start Rendering Frame: ', tempobj, sg[0], camera)
			res = cmds.convertLightmap(sg[0], tempobj, camera=camera, sh=True)
			res = os.path.join(ldir, res[0]+'.tif').replace('\\', '/')
			shutil.copyfile(res, file)
			cmds.rename(tempobj, targetp)
			print(res, file)
		else :
			cmds.convertSolidTx(sg[0], targetobj, camera=camera, antiAlias=True, shadows=True, rx=tokens['resolution'], ry=tokens['resolution'], fileFormat='tif', fileImageName=file)

	# revert film back
	cmds.setAttr(camera+'.horizontalFilmAperture', bkApertureH)
	cmds.setAttr(camera+'.verticalFilmAperture', bkApertureV)

if __name__ == '__main__' :
	import frustum
	camera = 'Lookdev_LunaHouse06:camShape'
	targetobj = 'grassEmitterA_bk1Shape'
	outpath = 'Z:/marza/proj/kibble/work/Stage/LunaHouseExt/lookdev/ArakawaT/grass/textures/txDnsMap2'
	tokens = frustum.getDefaultTokens()
	tokens['margin'] = 1.3
	tokens['resolution'] = 2048
	frustum.bakeFrustum(camera, targetobj, outpath, frameRange=None, tokens=tokens, dispatch=True)