import maya.OpenMaya as om

space = om.MSpace.kWorld

def getDagPath(obj) :
	sellist = om.MSelectionList()
	sellist.add(obj)
	dagpath = om.MDagPath()
	sellist.getDagPath(0, dagpath)
	return dagpath

def printVertexNormals(obj) :
	dagpath = getDagPath(obj)
	meshfn = om.MFnMesh(dagpath)
	viter = om.MItMeshVertex(dagpath)
	while not viter.isDone() :
		normal = om.MVector()
		viter.getNormal(normal, space)
		print(viter.index(), normal[0], normal[1], normal[2])
		viter.next()

def calculateVertexNormalsByNormalize(obj) :
	print('[calculateVertexNormalsByNormalize]')
	dagpath = getDagPath(obj)
	meshfn = om.MFnMesh(dagpath)
	viter = om.MItMeshVertex(dagpath)
	while not viter.isDone() :
		varray = om.MVectorArray()
		viter.getNormals(varray, space)
		vec = om.MVector()
		for i in range(varray.length()) :
			vec += varray[i]
		vec.normalize()
		print(viter.index(), vec[0], vec[1], vec[2])
		viter.next()
	pass

def calculateVertexNormalsByAngle(obj) :
	dagpath = getDagPath(obj)
	pass

def calculateVertexNormalsByArea(obj) :
	print('[calculateVertexNormalsByArea]')
	dagpath = getDagPath(obj)
	meshfn = om.MFnMesh(dagpath)
	viter = om.MItMeshVertex(dagpath)
	while not viter.isDone() :
		farray = om.MIntArray()
		viter.getConnectedFaces(farray)
		vec = om.MVector()
		for i in range(farray.length()) :
			fiter = om.MItMeshPolygon(dagpath)
			while not fiter.isDone() :
				if farray[i] == fiter.index() :
					su = om.MScriptUtil(0.0)
					dptr = su.asDoublePtr()
					fiter.getArea(dptr, space)
					area = su.getDouble(dptr)
					normal = om.MVector()
					fiter.getNormal(normal, space)
					vec += normal * area
					break
				fiter.next()
		vec.normalize()
		print(viter.index(), vec[0], vec[1], vec[2])	
		viter.next()
	pass

def calculateVertexNormals(obj, mode='normalize') :
	eval('calculateVertexNormalsBy'+mode.capitalize()+'(obj)')