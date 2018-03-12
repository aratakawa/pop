from maya import cmds

targetAttrs = {'mtoa_matteout':['Matte Out','bool'], 'primaryVisibility':['Primary Visibility','bool']}

def doSetAttr(obj, attr, val) :
    if not cmds.attributeQuery(attr, node=obj, ex=True) :
        cmds.addAttr(obj, longName=attr, niceName=targetAttrs[attr][0], at=targetAttrs[attr][1])
    cmds.setAttr(obj+'.'+attr, val)

def setGeomAttr(attr, val):
    selected = cmds.ls(sl=True)
    targetTypes = ['mesh', 'particle']

    types = set(cmds.allNodeTypes())
    if "gtoLocator" in types:
        targetTypes.append("gtoLocator")
    if "veFurNode" in types:
        targetTypes.append("veFurNode")

    if len(selected) > 0 :
        # apply to objects below selection
        cmds.select(selected,hi=True)
    else :
        # apply to all objects of target types
        cmds.select(all=True,hi=True)

    for t in targetTypes :
        objs = cmds.ls(sl=True,type=t,long=True)
        for o in objs :
            doSetAttr(o, attr, val)

    if len(selected) > 0 :
        cmds.select(selected)
        cmds.confirmDialog( title='Done', message='%s attribute set to selected objecs.\n(%d object(s) and below)' % (targetAttrs[attr][0], len(selected)), button=['Ok'], defaultButton='Ok', cancelButton='Ok', dismissString='Ok' )
    else :
        cmds.select(cl=True)
        cmds.confirmDialog( title='Done', message='%s attribute set to ALL objecs.' % targetAttrs[attr][0], button=['Ok'], defaultButton='Ok', cancelButton='Ok', dismissString='Ok' )