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
  newroot = inst.mirrorInstance()
  cmds.parent( children, s )
  cmds.delete(grp)
  print( newroot )
  cmds.setAttr( newroot+'.sx', -1 )
  newchildren = cmds.listRelatives( newroot, fullPath=True, children=True, type='transform' )
  target.append( cmds.listRelatives( s.replace('L','R'), fullPath=True, children=True, type='transform' ) )
  cmds.parent( newchildren, s.replace('L','R') )
  cmds.delete( newroot )

for t in target :
  cmds.delete( t )


from maya import cmds
import instantiate as inst
name = 'mainGunA%d_%s_FL'

geo = []
group = {}

def doRename( obj, type ) :
  counter = 0
  found = False
  while(not found):
    newname = name % (counter,type)
    match = cmds.ls(newname)
    if len(match) < 1 :
      found = True
      print( obj )
      cmds.rename(obj,newname)
      print('%s -> %s' % (obj,newname))
    counter += 1

selected = cmds.ls( sl=True, long=True )
for s in selected :
  cmds.select( cmds.listRelatives( children=True, fullPath=True, type='transform' ), hi=True )
  objs = cmds.ls( sl=True, type='transform', long=True )
  for o in objs :
    if inst.isDirectParent( o ) :
      if o not in geo :
        geo.append( o )
    else :
      depth = len(o.split('|'))
      if not group.has_key( depth ) :
        group[depth] = []
      if not o in group[depth] :
        group[depth].append( o )


print( 'start geo.' )
print( geo )
for g in geo :
  doRename( g, 'geo' )

keys = group.keys()
keys.sort(reverse=True)

print( 'start group.' )
print( group )


for k in keys :
  for g in group[k] :
    doRename( g, 'geoGp' )

cmds.select( selected )