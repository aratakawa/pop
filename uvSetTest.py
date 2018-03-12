import maya.OpenMaya as om

selection = om.MSelectionList()
selection.add( "arcadiaA_all_defaultShader:uvChooser1" )

chooser = om.MObject()
selection.getDependNode(0, chooser)
fnNode = om.MFnDependencyNode()
fnNode.setObject(chooser)

uvplug = fnNode.findPlug("uvSets")
print( uvplug.name() )
#print( uvplug.numElements() )

for i in range(uvplug.numElements() ) :
  uv = uvplug[i]
  parray = om.MPlugArray()
  uv.connectedTo( parray, True, False )
  print( parray.length() )

cmds.listConnections("arcadiaA_all_defaultShader:uvChooser1.uvSets", s=True, d=False, p=True )
cmds.getAttr( "arcadiaA_all_default:center9_geoShape.uvSet[1].uvSetName" )
