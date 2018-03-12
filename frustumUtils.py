import math
import maya.OpenMaya as om
import maya.cmds as cmds

x = om.MVector(1,0,0)
y = om.MVector(0,1,0)
z = om.MVector(0,0,-1)
nx = om.MVector(-1,0,0)
ny = om.MVector(0,-1,0)

kModeBbox = 0
kModePoint = 1
kModeFace = 2

def log(msg) :
	print('[CameraFrustum] %s' % msg)
	
def getDefaultTokens() :
	tokens = {}
	tokens['mode'] = 'bbox' # 'points', 'face', 'bbox'
	tokens['margin'] = 1.1
	tokens['invert'] = False
	tokens['clipByResolution'] = True
	return tokens

def inchToMm(inch) :
	return inch * 25.4

def angleOfView(focalLength, aperture) :
	return 2.0*math.atan((0.5*aperture)/focalLength)*180/math.pi

def lerp(a, b, v) :
	return a + v * (b-a)

class CameraFrustum(object) :
	def __init__(self, camera, tokens={}) :
		self.tokens = tokens
		self.camera = camera
		self.supported = ['mesh']
		self.focalLength = cmds.getAttr(self.camera+'.focalLength')
		self.hApertureInch = cmds.getAttr(self.camera+'.horizontalFilmAperture')
		self.vApertureInch = cmds.getAttr(self.camera+'.verticalFilmAperture')
		self.nearClip = cmds.getAttr(self.camera+'.nearClipPlane')
		self.farClip = cmds.getAttr(self.camera+'.farClipPlane')
		self.pos = om.MPoint()
		self.xvec = om.MVector()
		self.yvec = om.MVector()
		self.zvec = om.MVector()
		self.rvec = om.MVector()
		self.lvec = om.MVector()
		self.tvec = om.MVector()
		self.bvec = om.MVector()
		self.initData()
	def initData(self) :
		if not self.tokens :
			self.tokens = getDefaultTokens()
		# get camera node and worldMatrix attribute
		camobj = om.MObject()
		sellist = om.MSelectionList()
		sellist.add(self.camera)
		sellist.getDependNode(0, camobj)
		camfn = om.MFnDependencyNode(camobj)
		plug = camfn.findPlug('worldMatrix')
		plug = plug.elementByLogicalIndex(0)
		matrixobj = om.MObject()
		matrixobj = plug.asMObject()
		matrixfn = om.MFnMatrixData(matrixobj)
		worldMatrix = matrixfn.matrix()
		
		# angle of view
		self.nearClip = om.MPoint(0, 0, -cmds.getAttr(self.camera+'.nearClipPlane')) * worldMatrix
		self.farClip = om.MPoint(0, 0, -cmds.getAttr(self.camera+'.farClipPlane')) * worldMatrix
		self.focalLength = cmds.getAttr(self.camera+'.focalLength')
		self.hApertureInch = cmds.getAttr(self.camera+'.horizontalFilmAperture') * self.tokens['margin']
		self.vApertureInch = cmds.getAttr(self.camera+'.verticalFilmAperture') * self.tokens['margin']
		hApertureMm = inchToMm(self.hApertureInch)
		ratio = self.hApertureInch / self.vApertureInch
		if self.tokens['clipByResolution'] :
			ratio = cmds.getAttr('defaultResolution.width') / cmds.getAttr('defaultResolution.height')
		hw = angleOfView(self.focalLength, hApertureMm) / 180.0
		vw = hw / ratio

		# camera vectors
		self.pos = om.MPoint(worldMatrix(3,0), worldMatrix(3,1), worldMatrix(3,2))
		self.zvec = z * worldMatrix
		self.zvec.normalize()
		self.yvec = y * worldMatrix
		self.yvec.normalize()
		self.xvec = x * worldMatrix
		self.xvec.normalize()
		
		# frustum vectors
		print('hw', hw, angleOfView(self.focalLength, hApertureMm))
		print('rvec lerp', lerp(z.x,x.x,hw), lerp(z.y, x.y, hw), lerp(z.z, x.z, hw))
		print('rvecz', z.z, x.z)
		self.rvec = om.MVector(lerp(z.x,x.x,hw), lerp(z.y, x.y, hw), lerp(z.z, x.z, hw))
		self.rvec.normalize()
		self.rvec = self.rvec * worldMatrix
		self.lvec = om.MVector(lerp(z.x, nx.x, hw), lerp(z.y, nx.y, hw), lerp(z.z, nx.z, hw))
		self.lvec.normalize()
		self.lvec = self.lvec * worldMatrix
		self.tvec = om.MVector(lerp(z.x, y.x, vw), lerp(z.y, y.y, vw), lerp(z.z, y.z, vw))
		self.tvec.normalize()
		self.tvec = self.tvec * worldMatrix
		self.bvec = om.MVector(lerp(z.x, ny.x, vw), lerp(z.y, ny.y, vw), lerp(z.z, ny.z, vw))
		self.bvec.normalize()
		self.bvec = self.bvec * worldMatrix
		
		# inward vector
		self.rinward = self.yvec ^ self.rvec
		self.linward = self.lvec ^ self.yvec
		self.tinward = self.tvec ^ self.xvec
		self.binward = self.xvec ^ self.bvec
	def pointIsInside(self, point) :
		inside = True
		outside = False
		if self.tokens['invert'] :
			inside = False
			outside = True
		# right
		vec = point - self.pos+self.rvec
		vec.normalize()
		if vec*self.rinward <= 0 :
			return outside
		# left 
		vec = point - self.pos+self.lvec
		vec.normalize()
		if vec*self.linward <= 0 :
			return outside
		# top
		vec = point - self.pos+self.tvec
		vec.normalize()
		if vec*self.tinward <= 0 :
			return outside
		# buttom
		vec = point - self.pos+self.bvec
		vec.normalize()
		if vec*self.binward <= 0 :
			return outside
		# near
		vec = point - self.nearClip+self.zvec
		vec.normalize()
		if vec*self.zvec <= 0 :
			return outside
		# far
		vec = point - self.farClip+self.zvec
		vec.normalize()
		if vec*(-self.zvec) <= 0 :
			return outside
		#log('inside frustum.')
		return inside
	def bboxIsInside(self, obj) :
		if cmds.objectType(obj, isAType='shape') :
			obj = cmds.listRelatives(obj, p=True)[0]
		bbox = []
		nx, ny, nz, x, y, z = cmds.xform(obj, q=True, ws=True, bb=True)
		bbox.append(om.MPoint(x, y, nz))
		bbox.append(om.MPoint(x, y, z))
		bbox.append(om.MPoint(nx, y, nz))
		bbox.append(om.MPoint(nx, y, z))
		bbox.append(om.MPoint(x, ny, nz))
		bbox.append(om.MPoint(x, ny, z))
		bbox.append(om.MPoint(nx, ny, nz))
		bbox.append(om.MPoint(nx, ny, z))
		for p in bbox :
			if self.pointIsInside(p) :
				return True
		return False
	def pointsAreInside(self, obj) :
		if not cmds.objectType(obj, isAType='shape') :
			return False
		orgsellist = om.MSelectionList()
		om.MGlobal.getActiveSelectionList(orgsellist)
		sellist = om.MSelectionList()
		sellist.add(obj)
		dagpath = om.MDagPath()
		sellist.getDagPath(0, dagpath)
		sellist.clear()
		if cmds.objectType(obj) == 'mesh' :
			viter = om.MItMeshVertex(dagpath)
			while not viter.isDone() :
				if self.pointIsInside(viter.position(om.MSpace.kWorld)) :
					sellist.add(dagpath, viter.currentItem())
				viter.next()
			if not sellist.isEmpty() :
				orgsellist.merge(sellist)
				om.MGlobal.setActiveSelectionList(orgsellist)
				return True
		return False
	def facesAreInside(self, obj) :
		if not cmds.objectType(obj, isType='mesh') :
			return False
		orgsellist = om.MSelectionList()
		om.MGlobal.getActiveSelectionList(orgsellist)
		sellist = om.MSelectionList()
		sellist.add(obj)
		mobj = om.MObject()
		dagpath = om.MDagPath()
		sellist.getDagPath(0, dagpath)
		fiter = om.MItMeshPolygon(dagpath)
		sellist.clear()
		while not fiter.isDone() :
			points = om.MPointArray()
			fiter.getPoints(points, om.MSpace.kWorld)
			for i in range(points.length()) :
				if self.pointIsInside(points[i]) :
					sellist.add(dagpath, fiter.currentItem())
					break
			fiter.next()
		if not sellist.isEmpty() :
			orgsellist.merge(sellist)
			om.MGlobal.setActiveSelectionList(orgsellist)
			return True
		return False
	def objIsInside(self, obj) :
		if self.tokens['mode'] == kModeBbox :
			if self.bboxIsInside(obj) :
				cmds.select(obj, add=True)
				return True
		elif self.tokens['mode'] == kModePoint :
			return self.pointsAreInside(obj)
		elif self.tokens['mode'] == kModeFace :
			return self.facesAreInside(obj)
		return False
	def __repr__(self) :
		msg = ''
		msg += 'pos(%f, %f, %f)\n' % (self.pos.x, self.pos.y, self.pos.z)
		msg += 'x(%f, %f, %f)\n' % (self.xvec.x, self.xvec.y, self.xvec.z)
		msg += 'y(%f, %f, %f)\n' % (self.yvec.x, self.yvec.y, self.yvec.z)
		msg += 'z(%f, %f, %f)\n' % (self.zvec.x, self.zvec.y, self.zvec.z)
		msg += 'right(%f, %f, %f)\n' % (self.rvec.x, self.rvec.y, self.rvec.z)
		msg += 'left(%f, %f, %f)\n' % (self.lvec.x, self.lvec.y, self.lvec.z)
		msg += 'top(%f, %f, %f)\n' % (self.tvec.x, self.tvec.y, self.tvec.z)
		msg += 'bottom(%f, %f, %f)\n' % (self.bvec.x, self.bvec.y, self.bvec.z)
		msg += 'rinward(%f, %f, %f)\n' % (self.rinward.x, self.rinward.y, self.rinward.z)
		msg += 'linward(%f, %f, %f)\n' % (self.linward.x, self.linward.y, self.linward.z)
		msg += 'tinward(%f, %f, %f)\n' % (self.tinward.x, self.tinward.y, self.tinward.z)
		msg += 'binward(%f, %f, %f)\n' % (self.binward.x, self.binward.y, self.binward.z)
		return msg
	def __str__(self) :
		return self.__repr__()
	def createLocators(self) :
		cmds.spaceLocator(n='xvec', p=(self.xvec.x, self.xvec.y, self.xvec.z))
		cmds.spaceLocator(n='yvec', p=(self.yvec.x, self.yvec.y, self.yvec.z))
		cmds.spaceLocator(n='zvec', p=(self.zvec.x, self.zvec.y, self.zvec.z))
		cmds.spaceLocator(n='rvec', p=(self.rvec.x, self.rvec.y, self.rvec.z))
		cmds.spaceLocator(n='lvec', p=(self.lvec.x, self.lvec.y, self.lvec.z))
		cmds.spaceLocator(n='tvec', p=(self.tvec.x, self.tvec.y, self.tvec.z))
		cmds.spaceLocator(n='bvec', p=(self.bvec.x, self.bvec.y, self.bvec.z))
		cmds.spaceLocator(n='rinward', p=(self.rinward.x, self.rinward.y, self.rinward.z))
		cmds.spaceLocator(n='linward', p=(self.linward.x, self.linward.y, self.linward.z))
		cmds.spaceLocator(n='tinward', p=(self.tinward.x, self.tinward.y, self.tinward.z))
		cmds.spaceLocator(n='binward', p=(self.binward.x, self.binward.y, self.binward.z))
	def execute(self, nodes=[], frameRange=None) :
		if not nodes :
			cmds.select(hi=True)
			nodes = cmds.ls(sl=True, type=self.supported)
		cmds.select(cl=True)
		
		ct = int(cmds.currentTime(q=True))
		if not frameRange :
			frameRange = (ct,ct)
		
		out = []
		for i in range(frameRange[0], frameRange[1]+1) :
			cmds.currentTime(i)
			self.initData()
			for n in nodes :
				if self.objIsInside(n) :
					out.append(n)
		cmds.currentTime(ct)
		return out

def cameraFrustum(camera, tokens={}) :
	if not tokens :
		tokens = getDefaultTokens()
	tokens['mode'] = kModeFace
	tokens['invert'] = False
	cf = CameraFrustum(camera, tokens)
	#cf.execute(frameRange=(1, 24))
	objs = cf.execute()
	print(objs)

	
	
	
