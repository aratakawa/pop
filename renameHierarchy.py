from maya import cmds
import instantiate as inst
name = 'bigAnchor%d_%s_R'

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