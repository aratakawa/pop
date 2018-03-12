import maya.cmds as cmds
from functools import partial

class mzColorSetEditor(object) :
	def __init__(self) :
		self.objects = []
		self.lightSet = 'mzColorSetLights'
		self.window = 'mzColorSetEditor'
		self.objectSet = 'mzColorSetObjects'
		self.initScene()
		self.selected = []
	def initScene(self) :
		self.saveSelection()
		cmds.select(cl=True)
		if not cmds.objExists(self.lightSet) :
			cmds.sets(name=self.lightSet)
		if not cmds.objExists(self.objectSet) :
			cmds.sets(name=self.objectSet)
		self.revertSelection()
	def saveSelection(self) :
		self.selected = cmds.ls(sl=True)
	def revertSelection(self) :
		if len(self.selected) == 0 :
			cmds.select(cl=True)
		else :
			cmds.select(self.selected)
	def createLight(self, ltype) :
		#self.saveSelection()
		light = cmds.shadingNode(ltype+'Light', asLight=True)
		shape = cmds.listRelatives(light, children=True)[0]
		cmds.sets(shape, e=True, addElement=self.lightSet)
		#self.revertSelection()
		cmds.setAttr(shape+'.decayRate', 2)
		cmds.setAttr(shape+'.aiDiffuse', 0)
		cmds.setAttr(shape+'.aiSpecular', 0)
		cmds.setAttr(shape+'.aiSss', 0)
		cmds.setAttr(shape+'.aiIndirect', 0)
		cmds.setAttr(shape+'.aiAffectVolumetrics', 0)
		cmds.setAttr(shape+'.aiCastShadows')
		cmds.select(light)
	def showLights(self) :
		self.saveSelection()
		cmds.select(self.lightSet)
		if len(cmds.ls(sl=True)) > 0 :
			cmds.showHidden(cmds.ls(sl=True))
		self.revertSelection()
	def hideLights(self) :
		self.saveSelection()
		cmds.select(self.lightSet)
		if len(cmds.ls(sl=True)) > 0 :
			cmds.hide(cmds.ls(sl=True))
		self.revertSelection()
	def addObject(self, args) :
		self.saveSelection()
		if len(self.selected) == 0 :
			return
		cmds.select(hi=True)
		mesh = cmds.ls(sl=True, type='mesh')
		if len(mesh) > 0 :
			cmds.sets(mesh, e=True, addElement=self.objectSet)
		self.refreshObjectList()
		state = cmds.checkBox(self.window+'DisplayCheck', q=True, v=True)
		cmds.polyOptions(mesh, colorShadedDisplay=bool(state))
		self.revertSelection()
	def removeObject(self, args) :
		objects = cmds.textScrollList(self.window+'ObjectList', q=True, selectItem=True)
		if not objects :
			return
		print('Removing %s from list.' % object)
		cmds.sets(objects, e=True, remove=self.objectSet)
		self.refreshObjectList()
	def refreshObjectList(self) :
		self.saveSelection()
		self.initScene()
		cmds.select(self.objectSet)
		cmds.textScrollList(self.window+'ObjectList', e=True, removeAll=True)
		cmds.textScrollList(self.window+'ObjectList', e=True, append=cmds.ls(sl=True))
		self.refreshColorSets()
		self.revertSelection()
	def refreshColorSets(self) :
		cmds.select(self.objectSet)
		mesh = cmds.ls(sl=True)
		cmds.textScrollList(self.window+'SetList', e=True, removeAll=True)
		if len(mesh) == 0 :
			return
		csets = cmds.polyColorSet(q=True, allColorSets=True)
		if not csets :
			return
		csets = set(csets)
		csetstr =' '.join(csets)
		import mtoa
		ver = mtoa.Version
		from distutils.version import StrictVersion
		for m in mesh :
			cmds.setAttr(m+'.aiExportColors', 1)
			if StrictVersion(ver) > StrictVersion('1.22.4') :
				cmds.setAttr(m+'.aiExportColorsAsVectors', csetstr, type='string')
			cursets = cmds.polyColorSet(m, q=True, allColorSets=True)
			for c in csets :
				if c not in cursets :
					cmds.polyColorSet(m, c=True, clamped=True, colorSet=c)
		cmds.textScrollList(self.window+'SetList', e=True, removeAll=True)
		csetlist = list(csets)
		csetlist.sort()
		cmds.textScrollList(self.window+'SetList', e=True, append=csetlist)
	def setSelectionCB(self) :
		self.saveSelection()
		selectedset = cmds.textScrollList(self.window+'SetList', q=True, selectItem=True)
		if not selectedset:
			return
		self.setCurrentColorSet(selectedset[0])
		self.revertSelection()
	def addSetCB(self, args) :
		result = cmds.promptDialog(title='Add Color Set', message='Enter Set Name:', button=['OK', 'Cancel'], defaultButton='OK', cancelButton='Cancel', dismissString='Cancel')
		if result == 'OK' :
			sname = cmds.promptDialog(q=True, text=True)
			cmds.select(self.objectSet)
			cmds.polyColorSet(cr=True, cs=sname)
			self.refreshColorSets()
	def removeSetCB(self, args) :
		self.saveSelection()
		selected = cmds.textScrollList(self.window+'SetList', q=True, selectItem=True)
		if not selected :
			return
		cmds.select(self.objectSet)
		cmds.polyColorSet(e=True, delete=True, cs=selected[0])
		self.refreshColorSets()
		self.revertSelection()
	def setCurrentColorSet(self, setname) :
		print('Setting current color set: %s' % setname)
		cmds.select(self.objectSet)
		cmds.polyColorSet(e=True, currentColorSet=True, colorSet=setname)
	def selectObjects(self, args) :
		cmds.select(self.objectSet)
	def getVisibility(self, node) :
		if not cmds.getAttr(node+'.visibility') :
			return False
		else :
			parents = cmds.listRelatives(node, parent=True)
			if parents :
				return self.getVisibility(parents[0])
		return True
	def bake(self, args) :
		self.saveSelection()
		mode = cmds.optionMenuGrp(self.window+'ColorBlendMenu', q=True, v=True)
		selmode = cmds.checkBox(self.window+'BakeSelectionCheck', q=True, v=True)
		if selmode :
			cmds.select(hi=True)
		selobj = cmds.ls(sl=True, type='mesh')
		print(selmode, selobj)
		cmds.select(self.objectSet)
		objects = cmds.sets(self.objectSet, q=True)
		if selmode :
			temp = []
			for o in objects :
				#print(o, o in selobj)
				if o in selobj :
					temp.append(o)
			objects = temp
		print(objects)
		nobjects = len(objects)
		if nobjects == 0 :
			self.revertSelection()
			return
		cmds.select(self.lightSet)
		lights = cmds.ls(sl=True)
		# get visible lights
		vlights = []
		for l in lights :
			if self.getVisibility(l) :
				vlights.append(l)
			else :
				print('%s not visible. skipped' % l)
		# multiply intensity by number of lights
		nlights = len(vlights)
		for l in vlights :
			cmds.setAttr(l+'.intensity', cmds.getAttr(l+'.intensity')* nlights)
		# hide unrelated lights
		allLights = cmds.ls(type='light')
		state = {}
		for l in allLights :
			if l not in lights :
				state[l] = cmds.getAttr(l+'.visibility')
				cmds.setAttr(l+'.visibility', 0)
		print('Bake color blend mode: %s' % mode)
		# do bake
		import maya.mel
		gMainProgressBar = maya.mel.eval('$tmp = $gMainProgressBar')
		cmds.progressBar( gMainProgressBar, e=True, beginProgress=True, isInterruptable=True, status='Baking Objects...', maxValue=nobjects )
		for i in range(nobjects) :
			if cmds.progressBar(gMainProgressBar, query=True, isCancelled=True ) :
				break
			cmds.select(objects[i])
			cmds.polyGeoSampler(ids=True, lightingOnly=True, clampRGBMin=(0,0,0), clampRGBMax=(1,1,1), clampAlphaMin=0, clampAlphaMax=1, shareUV=True, colorBlend=mode.lower(), alphaBlend='overwrite')
			cmds.progressBar(gMainProgressBar, edit=True, step=1)
		cmds.progressBar(gMainProgressBar, edit=True, endProgress=True)
		#cmds.polyGeoSampler(ids=True, lightingOnly=True, clampRGBMin=(0,0,0), clampRGBMax=(1,1,1), clampAlphaMin=0, clampAlphaMax=1, shareUV=True, colorBlend=mode.lower(), alphaBlend='overwrite')
		for l in state.keys() :
			cmds.setAttr(l+'.visibility', state[l])
		self.revertSelection()
		# revert intensity value
		for l in vlights :
			cmds.setAttr(l+'.intensity', cmds.getAttr(l+'.intensity') / nlights)
	def displayCB(self, args) :
		state = cmds.checkBox(self.window+'DisplayCheck', q=True, v=True)
		mesh = cmds.sets(self.objectSet, q=True)
		for m in mesh :
			if cmds.objectType(m) != 'mesh' :
				continue
			cmds.polyOptions(m, colorShadedDisplay=bool(state))
	def refreshDisplay(self) :
		mesh = cmds.sets(self.objectSet, q=True)
		state = False
		if mesh and len(mesh) > 0 :
			state = cmds.polyOptions(mesh[0], q=True, colorShadedDisplay=True)
			cmds.checkBox(self.window+'DisplayCheck', e=True, v=True)
	def refreshUI(self, args) :
		if cmds.layout(self.window+'BodyLayout', ex=True) :
			cmds.deleteUI(self.window+'BodyLayout')
		self.createBody()
		self.refreshObjectList()
		self.refreshDisplay()
	def createBody(self) :
		cmds.setParent(self.window+'RootLayout')
		cmds.columnLayout(self.window+'BodyLayout', adj=True)
		cmds.button(self.window+'RefreshButton', label='Refresh UI', c=self.refreshUI)
		cmds.checkBox(self.window+'DisplayCheck', label='Display Vertex Color', cc=self.displayCB)
		# Lights
		cmds.frameLayout(self.window+'LightFrame', label='Lights', borderStyle='etchedIn', collapsable=True, collapse=False)
		cmds.rowColumnLayout(self.window+'LightLayout', nc=5)
		cmds.iconTextButton( style='iconOnly', image1='pointlight.png', label='pointlight', c=partial(self.createLight, 'point') )
		cmds.iconTextButton( style='iconOnly', image1='spotlight.png', label='spotlight', c=partial(self.createLight, 'spot') )
		cmds.iconTextButton( style='iconOnly', image1='arealight.png', label='arealight', c=partial(self.createLight, 'area') )
		cmds.iconTextButton( image1='pointlight.png', iol='Show', c=self.showLights )
		cmds.iconTextButton( image1='pointlight.png', iol='Hide', c=self.hideLights )
		cmds.setParent('..') # out rowColumnLayout
		cmds.setParent('..') # out frameLayout
		# Objects
		cmds.frameLayout(self.window+'ObjectFrame', label='Objects', borderStyle='etchedIn', collapsable=True, collapse=False)
		cmds.columnLayout(self.window+'ObjectLayout', adj=True)
		cmds.textScrollList(self.window+'ObjectList', allowMultiSelection=True)
		cmds.rowColumnLayout(self.window+'AddRemoveObjLayout', nc=2)
		cmds.button(self.window+'AddObjButton', label='Add Selected', c=self.addObject)
		cmds.button(self.window+'RemoveObjButton', label='Remove Selected', c=self.removeObject)
		cmds.setParent('..') # out rowColumnLayout
		cmds.button(self.window+'SelectObjButton', label='Select Objects', c=self.selectObjects)
		cmds.setParent('..') # out columnLayout
		cmds.setParent('..') # out frameLayout
		# Color Sets
		cmds.frameLayout(self.window+'SetFrame', label='Color Sets', borderStyle='etchedIn', collapsable=True, collapse=False)
		cmds.columnLayout(self.window+'SetLayout')
		cmds.textScrollList(self.window+'SetList', allowMultiSelection=False, selectCommand=self.setSelectionCB)
		cmds.rowColumnLayout(self.window+'AddRemoveSetLayout', nc=2)
		cmds.button(self.window+'AddSetButton', label='Add Color Set', c=self.addSetCB)
		cmds.button(self.window+'RemoveSetButton', label='Remove Color Set', c=self.removeSetCB)
		cmds.setParent('..') # out rowColumnLayout
		cmds.setParent('..') # out columnLayout
		cmds.setParent('..') # out frameLayout
		# Bake Options
		cmds.frameLayout(self.window+'BakeFrame', label='Bake Options', borderStyle='etchedIn', collapsable=True, collapse=False)
		cmds.columnLayout(self.window+'BakeLayout', adj=True)
		cmds.optionMenuGrp(self.window+'ColorBlendMenu', label='Color Blending')
		cmds.checkBox(self.window+'BakeSelectionCheck', label='Bake Selected Objects Only')
		menus = ['Overwrite', 'Add', 'Subtract', 'Multiply', 'Divide', 'Average']
		for m in menus :
			cmds.menuItem(label=m)
		cmds.button(self.window+'BakeButton', label='Bake', c=self.bake)
		cmds.setParent('..') # out columnLayout
		cmds.setParent('..') # out frameLayout
	def ui(self) :
		if cmds.window(self.window, q=True, ex=True) :
			cmds.deleteUI(self.window)
		"""
		if cmds.windowPref(self.window, q=True, ex=True) :
			cmds.windowPref(self.window, remove=True)
		"""
		cmds.window(self.window)
		cmds.columnLayout(self.window+'RootLayout', adj=True)
		self.refreshUI('dummy')
		cmds.showWindow(self.window)