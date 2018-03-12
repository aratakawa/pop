def doExec() :
	import maya.cmds as cmds
	cmds.file("Z:/marza/proj/onyx/work/TKValley/Sc058c07/model/ArakawaT/test/data/bakelist/AAA01SG2.mb", o=True)

if __name__  == '__main__' :
	import maya.standalone
	maya.standalone.initialize()
	doExec()