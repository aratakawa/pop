from maya import cmds

import instantiate as inst
reload( inst )

target = []
selected = cmds.ls( sl=True, long=True )
for s in selected :
  print( '%s' % s.replace('L','R') )
  children = cmds.listRelatives( s, fullPath=True, children=True, type='transform' )
  cmds.select( children )
  grp = cmds.group()
  children = cmds.listRelatives( grp, fullPath=True, children=True, type='transform' )
  grp = cmds.ls( sl=True, long=True )[0]
  cmds.select( grp )
  newroot = inst.mirrorInstance('noMove_geoGp')
  cmds.parent( children, s )
  cmds.delete(grp)
  print( newroot )
  cmds.setAttr( newroot+'.sx', -1 )
  newchildren = cmds.listRelatives( newroot, fullPath=True, children=True, type='transform' )
  #target.append( cmds.listRelatives( s.replace('_L','_R'), fullPath=True, children=True, type='transform' ) )
  #cmds.parent( newchildren, s.replace('_L','_R') )
  #cmds.delete( newroot )
  cmds.select( newroot )

for t in target :
  cmds.delete( t )