from maya import cmds

name = 'uvEdit'
scaleU = name + 'ScaleU'
scaleV = name + 'ScaleV'
offsetU = name + 'OffsetU'
offsetV = name + 'OffsetV'

def doScale( args ) :
    su = cmds.floatField( scaleU, q=True, v=True )
    sv = cmds.floatField( scaleV, q=True, v=True )
    cmds.polyEditUV( r=True, su=su, sv=sv )

def doOffset( args ) :
    u = cmds.floatField( offsetU, q=True, v=True )
    v = cmds.floatField( offsetV, q=True, v=True )
    cmds.polyEditUV( r=True, u=u, v=v )

def run() :
    if cmds.window( name, q=True, ex=True ) :
        cmds.deleteUI( name, window=True )
    cmds.window( name, title=name )
    cmds.columnLayout()
    # scale
    cmds.rowColumnLayout( nc=3 )
    cmds.floatField( scaleU, v=1 )
    cmds.floatField( scaleV, v=1 )
    cmds.button( label='Scale UV', c=doScale )
    cmds.setParent( '..' )
    # offset
    cmds.rowColumnLayout( nc=3 )
    cmds.floatField( offsetU, v=0 )
    cmds.floatField( offsetV, v=0 )
    cmds.button( label='Offset UV', c=doOffset )
    cmds.setParent( '..' )
    cmds.showWindow( name )

def cleanUvSets() :
	shapes = cmds.ls(type='mesh')
	for s in shapes :
	  indices = cmds.polyUVSet(s, q=True, allUVSetsIndices=True)
	  garbage = []
	  for i in indices :
		  setname = cmds.getAttr(s+'.uvSet[%d].uvSetName'%i)
		  if setname != 'map1' :
			  garbage.append(setname)
	  for g in garbage :
		  cmds.polyUVSet(s, delete=True, uvSet=g)
		  print('[%s] Deleting %s' % (s, g))

def cleanUvSets2() :
	shapes = cmds.ls(type='mesh')
	for s in shapes :
		indices = cmds.polyUVSet(s, q=True, allUVSetsIndices=True)
		garbage = []
		for i in indices :
			setname = cmds.getAttr(s+'.uvSet[%d].uvSetName'%i)
			print(setname, cmds.polyUVSet(s, q=True, currentUVSet=True)[0])
			if setname != cmds.polyUVSet(s, q=True, currentUVSet=True)[0] :
				garbage.append(setname)
		for g in garbage :
			print('[%s] Deleting %s' % (s, g))
			cmds.polyUVSet(s, delete=True, uvSet=g)
		  