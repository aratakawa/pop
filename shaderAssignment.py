from maya import cmds

def selectAssignedObjects() :
    selected = cmds.ls( sl=True )
    root = selected[0]
    engine = selected[1]
    cmds.select( root, hi=True )
    objs = cmds.ls( sl=True, type='mesh', long=True )
    cmds.select( engine )
    assigned = cmds.ls( sl=True, type='mesh', long=True )

    targets = []
    for o in objs :
      if o in assigned :
        targets.append( o )

    if len(targets) > 0 :
      cmds.select( targets )

"""
from maya import cmds
import shaderAssignment as sa

engine = cmds.ls(sl=True)[-1]
groups = cmds.ls(sl=True,long=True)[0:-1]

targets = []
print(groups, engine)
for g in groups :
    cmds.select(g, r=True)
    cmds.select(engine, ne=True, add=True)
    print(cmds.ls(sl=True))
    sa.selectAssignedObjects()
    targets.extend(cmds.ls(sl=True, long=True))
cmds.select(targets)
cmds.pickWalk(d='up')
"""
pass