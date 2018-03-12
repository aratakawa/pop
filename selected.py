from maya import cmds

name = 'popSeleced'
scrollList = name+'ScrollList'

def selectCB() :
    objs = cmds.textScrollList( scrollList, q=True, selectItem=True )
    cmds.select( objs )

def run() :
    if cmds.window( name, q=True, ex=True ) :
        cmds.deleteUI( name, window=True )
    selected = cmds.ls( sl=True, long=True )
    cmds.window( name, title=name, w=300, h=500 )
    cmds.columnLayout()
    cmds.text( '%d objects selected.' % len(selected) )
    cmds.textScrollList( scrollList, append=selected, allowMultiSelection=True, sc=selectCB )
    cmds.showWindow()