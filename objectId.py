from maya import cmds

attr = 'mtoa_constant_objectid'
types = ['gtoLocator', 'mesh', 'veFurNode', 'particle', 'mzAbcShape']

def setId() :
    result = cmds.promptDialog(title='RenameGeo',message='Enter Name',button=['OK','Cancel'],defaultButton='OK',cancelButton='Cancel',dismissString='Cancel')
    if result == 'OK':
        id = int(cmds.promptDialog(q=True,text=True))
        selected = cmds.ls( sl=True )
        cmds.select(hi=True)
        for t in types :
            if t not in cmds.allNodeTypes() :
                continue
            objs = cmds.ls(sl=True,type=t,long=True)
            for o in objs :
                if not cmds.attributeQuery(attr, ex=True, node=o) :
                    cmds.addAttr(o, ln=attr, nn="Object ID", at='long', dv=0)
                    cmds.setAttr(o+'.'+attr, e=True, keyable=True)
                cmds.setAttr(o+'.'+attr, id)

def getObjectsById() :
    result = cmds.promptDialog(title='RenameGeo',message='Enter Name',button=['OK','Cancel'],defaultButton='OK',cancelButton='Cancel',dismissString='Cancel')
    out = []
    if result == 'OK':
        id = int(cmds.promptDialog(q=True,text=True))
        for t in types :
            if t not in cmds.allNodeTypes() :
                continue
            objs = cmds.ls( type=t, long=True )
            for o in objs :
                if cmds.attributeQuery( attr, ex=True, node=o ) :
                    if id == cmds.getAttr( o+'.'+attr ) :
                        out.append( o )

    cmds.select(cl=True)
    if len( out ) > 0 :
        cmds.select( out )