import debrisCleaner as dc
import maya.cmds as cmds

# root transform of debris(used as space for gto bake)
root = 'Debris_G'
# output directory for gto files
# should be set somewhere under work/seq/shot/effect/user/
outpath = 'Z:/marza/proj/onyx/work/TKValley/Sc058c07/effect/ArakawaT/etc/out'

reload(dc)
cleaner = dc.debrisCleaner(root, outpath)

# first, manually delete unnecessary objects by hand
# then execute the following to further cleanup the scene
cleaner.cleanup()

# create object sets called "dynamic" and "static", to differentiate objects with and without animation
# bake is executed based on these sets.
cleaner.bake('dynamic')
cleaner.bake('static')

# create a new scene, load gto files into the scene with namespaces
dc.mergeDebris(outpath)

# import a maya scene only with shaders needed
# this could be a good starting point: Z:/marza/proj/onyx/team/lookdev/outpbox/fx/tokargaDebris/shaders.ma
cmds.file('Z:/marza/proj/onyx/team/lookdev/outpbox/fx/tokargaDebris/shaders.ma', i=True)
dc.assignShadersByName()

# set necessary geometry attributes, such as output_Pref, visibleInReflections, visibleInRefractions, etc.
dc.setGeomAttrs()