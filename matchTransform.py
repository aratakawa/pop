from maya import cmds
import pymel.core as pm
import pymel.core.datatypes as dt

class MatchObj(object) :
	def __init__(self, transform) :
		self.transform = pm.PyNode(transform)
		self.shape = self.transform.getShape()
		pm.xform(self.transform, cp=True)
		self.basis = None
		self.originalPivots = None
		temp = cmds.xform(self.transform.name(), q=True, ws=True, m=True)
		self.matrix = dt.Matrix([temp[0:4], temp[4:8], temp[8:12], temp[12:]])
		self.resetTransform()
		self.setBasis()
		self.restoreTransform()
	def warning(self, message) :
		pm.system.warning('%s %s' %('MatchObj', message))
	def setBasis(self) :
		self.transform.centerPivots(val=True)	
		self.originalPivots = self.transform.getPivots()
		if self.originalPivots[0] != self.originalPivots[1] :
			self.warning('RotationPivot and scalePivot are different. RotationPivot is used.')
		v1 = dt.Vector(self.shape.vtx[0].getPosition() - self.shape.vtx[1].getPosition())
		vtemp = dt.Vector(self.shape.vtx[1].getPosition() - self.shape.vtx[2].getPosition())
		v2 = v1.cross(vtemp)
		v3 = v1.cross(v2)
		self.basis = [v1, v2, v3, self.originalPivots[0]]
	def centerPivots(self) :
		pass
	def getMatrixByBasis(self) :
		return dt.Matrix(self.basis)
	def resetTransform(self) :
		self.transform.setMatrix(self.matrix*self.matrix.inverse())
	def restoreTransform(self) :
		self.transform.setMatrix(self.matrix)
	def setMatrix(self, m) :
		self.transform.setMatrix(m)

def matchTransform(instance=False) :
	nodes = pm.selected()
	orig = nodes[-1]
	targets = nodes[:-1]
	oobj = MatchObj(orig.name())
	for t in targets :
		ocp = None
		if instance :
			ocp = pm.instance(orig)[0]
		else:
			ocp = pm.duplicate(orig)[0]
		if ocp != None :
			ttemp = pm.duplicate(t)[0]
			tobj = MatchObj(ttemp.name())
			ocp.rename(t.name()+'_matchcopy')
			m = tobj.getMatrixByBasis()
			#ocp.setMatrix(m)
			ocp.setMatrix(m*tobj.matrix)
			pm.delete(ttemp)
			if t.getParent() :
				print(ocp.name())
				#pm.parent(ocp, t.getParent(), a=True)
				pass
			pass



if True :
	matchTransform()