import pymel.core as pm
import maya.cmds as cmds
import maya.OpenMaya as om

def createMeshFromUV(uvSet='map1') :
	# get mesh from selection
	selected = pm.selected()
	if len(selected) == 0 :
		om.MGlobal.displayError("Nothing is selected. Please select one object.")
		return
	original = selected[0]
	if original.type() != 'mesh' :
		original = original.getShape()
		if original.type() != 'mesh' :
			om.MGlobal.displayError('Selected object is not a polygon mesh.')
			return
	# get MObject from API
	sellist = om.MSelectionList()
	sellist.add(original.name())
	obj = om.MObject()
	objpath = om.MDagPath()
	sellist.getDagPath(0, objpath)
	sellist.getDependNode(0, obj)
	meshFn = om.MFnMesh(objpath)

	# variables to store data
	vnum = meshFn.numFaceVertices()
	polynum = meshFn.numPolygons()
	it = om.MItMeshFaceVertex(obj)
	parray = om.MFloatPointArray()
	connects = om.MIntArray()
	counts = om.MIntArray()
	fvrel = {}
	counter = 0
	pbake = []
	nbake = []

	# iterate all face vertices
	while not it.isDone() :
		# get uv data, store it as point position
		sutil = om.MScriptUtil()
		sutil.createFromList([0.0,0.0], 2)
		uvPoint = sutil.asFloat2Ptr()
		it.getUV(uvPoint, uvSet)
		u = om.MScriptUtil.getFloat2ArrayItem(uvPoint, 0, 0)
		v = om.MScriptUtil.getFloat2ArrayItem(uvPoint, 0, 1)
		point = om.MFloatPoint(-u, 0.0, v)
		parray.append(point)
		ppos = om.MPoint()
		meshFn.getPoint(it.vertId(), ppos, om.MSpace.kWorld)
		#ppos = it.position(space=om.MSpace.kWorld)
		pbake.append((ppos.x, ppos.y, ppos.z))
		nvec = om.MVector()
		it.getNormal(nvec)
		nbake.append((nvec.x, nvec.y, nvec.z))
		# store face index and vertex index of this faceVertex for later use
		fid = it.faceId()
		if not fvrel.has_key(fid) :
			fvrel[fid] = []
		fvrel[fid].append((it.faceVertId(), it.vertId(), counter))
		it.next()
		counter += 1
	it = om.MItMeshPolygon(obj)

	# iterate all polygons to get vertex per face and connection info
	while(not it.isDone()) :
		vlist = om.MIntArray()
		it.getVertices(vlist)
		counts.append(vlist.length())
		fid = it.index()
		for i in range(vlist.length()) :
			for relid, vid, fvid in fvrel[fid] :
				if vid == vlist[i] :
					connects.append(fvid)
					break
		it.next()

	# create uv unwrapped mesh
	newtransform = meshFn.create(vnum, polynum, parray, counts, connects)
	sl = om.MSelectionList()
	sl.add(newtransform)
	dagFn = om.MFnDagNode(newtransform)
	newpath = om.MDagPath()
	dagFn.getPath(newpath)
	newmesh = newpath.fullPathName()
	newmesh = pm.PyNode(newmesh).getShape().name()

	# add Pbake and Nbake attributes, which mzBake2d shader uses for rendering
	import userAttributesInfo
	pattr = 'mtoa_Pbake'
	nattr = 'mtoa_Nbake'
	print( len(pbake), len(nbake))
	cmds.addAttr(newmesh, ln=pattr, sn=pattr, nn=pattr, dt='vectorArray')
	cmds.addAttr(newmesh, ln=nattr, sn=nattr, nn=nattr, dt='vectorArray')
	cmds.setAttr(newmesh+'.'+pattr, len(pbake), type='vectorArray', *pbake)
	cmds.setAttr(newmesh+'.'+nattr, len(nbake), type='vectorArray', *nbake)
	userAttributesInfo.setClass(newmesh, pattr, userAttributesInfo.VARYING)
	userAttributesInfo.setClass(newmesh, nattr, userAttributesInfo.VARYING)

	return newmesh

def assignBakeShader(obj=None) :
	selected = cmds.ls(sl=True)
	if not obj :
		obj = selected
	shader = cmds.shadingNode('mzBake2d', asShader=True)
	engine = cmds.createNode('shadingEngine', n='%s_sg'%shader)
	cmds.connectAttr(shader+'.message', engine+'.surfaceShader')
	
	print(engine, shader)
	cmds.select(obj)
	cmds.sets(e=True,forceElement=engine)

	cmds.select(selected)
	return shader, engine

def createBakeCamera() :
	cam = cmds.camera(cameraScale=1, orthographic=True, orthographicWidth=1)
	cmds.setAttr(cam[0]+'.rotateX', -90)
	cmds.setAttr(cam[0]+'.rotateY', 180)
	cmds.setAttr(cam[0]+'.translateY', 10)
	cmds.setAttr(cam[0]+'.translateX', -0.5)
	cmds.setAttr(cam[0]+'.translateZ', 0.5)
	cmds.setAttr(cam[1]+'.displayResolution', 1)
	return cam

def getSceneBound(visualize=False) :
	large = 10000000
	objs = pm.ls(assemblies=True)
	max = [-large, -large, -large]
	min = [large, large, large]
	for o in objs :
		bmax = o.getBoundingBoxMax()
		bmin = o.getBoundingBoxMin()
		for i in range(len(bmax)) :
			if bmax[i] > max[i] :
				max[i] = bmax[i]
			if bmin[i] < min[i] :
				min[i] = bmin[i]
	if visualize :
		cube = pm.polyCube()
		cshape = cube[0].getShape()
		pm.move(cshape.name()+'.vtx[0]', min[0], min[1], max[2])
		pm.move(cshape.name()+'.vtx[1]', max[0], min[1], max[2])
		pm.move(cshape.name()+'.vtx[2]', min[0], max[1], max[2])
		pm.move(cshape.name()+'.vtx[3]', max[0], max[1], max[2])
		pm.move(cshape.name()+'.vtx[4]', min[0], max[1], min[2])
		pm.move(cshape.name()+'.vtx[5]', max[0], max[1], min[2])
		pm.move(cshape.name()+'.vtx[6]', min[0], min[1], min[2])
		pm.move(cshape.name()+'.vtx[7]', max[0], min[1], min[2])
	return min, max


def setupBakeScene(objs=None) :
	selected = cmds.ls(sl=True)
	if objs == None :
		objs = selected
	cmds.select(objs, hi=True)
	objs = cmds.ls(sl=True, type='mesh')

	# convert to uvMesh
	out = []
	for o in objs :
		cmds.select(o, r=True)
		out.append(createMeshFromUV())
	# assign shader
	cmds.select(out)	
	assignBakeShader()

	# create camera
	cam = createBakeCamera()

	g = pm.group(em=True, name='mzBake2dGroup')
	for o in out :
		pm.parent(o, g)
	pm.parent(cam, g)

	min, max = getSceneBound()
	print(min, max)
	offsetmin = max[0]
	if max[2] < offsetmin :
		offsetmin = max[2]
	pm.move(g, max[0]+1, 0, max[2]+1)