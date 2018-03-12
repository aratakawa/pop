from maya import cmds

f = 'fluidShape1'
res = cmds.getAttr(f+'.resolution')[0]
print(res)
x, y, z = res
voxels = x*y
print('%d voxels.' % voxels)

for xi in range(x) :
    for yi in range(y) :
    #for yi in range(1) :
        vel = cmds.getFluidAttr(f, at='velocity', xi=xi, yi=yi, zi=0)
        #print(vel)
        cmds.setFluidAttr(f, at='color', vv=vel, xi=xi, yi=yi, zi=0)

		
from maya import cmds

attrs = {'diffuseColorAmount':'diffuseWeight', 'roughnessAmount':'diffuseRoughness', 'reflectionColorAmount':'specularWeightP', 'refractionColorAmount':'refractionWeight'}
conns = {'reflectionColor':'specularColorP', 'color':'diffuseColor', 'refractionColor':'refractionColor'}

sources = cmds.ls(sl=True, type='VRayMtl')
for s in sources :
  std = cmds.shadingNode('mzStandardShader', asShader=True)
  for attr in attrs :
      cmds.setAttr(std+'.'+attrs[attr], cmds.getAttr(s+'.'+attr))
  if cmds.getAttr(s+'.useFresnel') :
      cmds.setAttr(std+'.specularFresnelTypeP', 0)
      cmds.setAttr(std+'.specularFresnelP', 1)
      if cmds.getAttr(s+'.lockFresnelIORToRefractionIOR') :
          cmds.setAttr(std+'.specularFresnelIorP', cmds.getAttr(s+'.refractionIOR'))
      else :
          cmds.setAttr(std+'.specularFresnelIorP', cmds.getAttr(s+'.fresnelIOR'))
  for c in conns :
      tgt = cmds.listConnections(s+'.'+c, s=True, plugs=True)
      if tgt or len(tgt) > 0 :
          cmds.connectAttr(tgt[0], std+'.'+conns[c], f=True)
  tgt = cmds.listConnections(s+'.bumpMap', s=True)
  if tgt or len(tgt) > 0 :
      tgt = tgt[0]
      bmp = cmds.shadingNode('bump2d', asUtility=True)
      cmds.setAttr(tgt+'.alphaIsLuminance', 1)
      cmds.connectAttr(tgt+'.outAlpha', bmp+'.bumpValue', f=True)
      cmds.connectAttr(bmp+'.outNormal', std+'.normalCamera')
      cmds.setAttr(bmp+'.bumpDepth', cmds.getAttr(s+'.bumpMult'))
      
      
files = cmds.ls(sl=True, type='file')
for f in files :
  path = cmds.getAttr(f+'.fileTextureName')
  cmds.setAttr(f+'.fileTextureName', path.replace('.tx','.tif'), type='string')