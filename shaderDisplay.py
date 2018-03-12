import maya.cmds as cmds

win = 'ShaderDisplay'

def setDisplayFlag(cls, show) :
	nodes = cmds.allNodeTypes()
	types = []
	for n in nodes :
		c = cmds.getClassification(n)[0]
		do = True
		for cl in cls :
			if cl not in c :
				do = False
				break
		if do :
			types.append(n)
	for t in types :
		print(t)
		tag = cmds.objectType(tagFromType=t)
		cmds.setNodeTypeFlag(tag, display=show)

def setShaderDisplay(show) :
	setDisplayFlag(['shader', 'texture'], show)
	setDisplayFlag(['shader', 'utility'], show)
	setDisplayFlag(['placement'], show) 
	#setDisplayFlag(['shader', 'surface'], 0)

def setShaderDisplayCB(args) :
	global win
	sl = cmds.radioButtonGrp(win+'Btn', q=True, select=True)
	print(sl)
	setShaderDisplay(sl-1)

def ui() :
	global win
	if cmds.window(win, q=True, ex=True) :
		cmds.deleteUI(win, window=True)
		cmds.windowPref(win, remove=True)
	cmds.window(win, widthHeight=(400, 60))
	cmds.columnLayout(adj=True)
	cmds.radioButtonGrp( win+'Btn', label='Mode', labelArray2=['Simplify', 'All Nodes'], numberOfRadioButtons=2 )
	cmds.radioButtonGrp( win+'Btn', e=True, select=0 )
	offButton = cmds.button(label='Set Display', c=setShaderDisplayCB)
	cmds.showWindow(win)