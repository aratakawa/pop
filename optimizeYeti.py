for y in cmds.ls(type='pgYetiMaya') :
	conn = cmds.listConnections(y, type='time')
	if not conn :
		cmds.connectAttr('time1.outTime', y+'.currentTime')
		print(y)



		
import ld_frustrum
reload(ld_frustrum)
camera = 's280_340:camShape'
targetobj = 'hillAB_geoShape'
outpath = 'Z:/marza/proj/kibble/work/280/340/light/ArakawaT/optimize/textures/grass_hillAB'
tokens = ld_frustrum.getDefaultTokens()
tokens['margin'] = 2.5
tokens['resolution'] = 4096
tokens['clipByResolution'] = False
ld_frustrum.bakeFrustrum(camera, targetobj, outpath, frameRange=None, tokens=tokens, dispatch=True)

import mzAssetIO
seq = '280'
shot = '130'
name = 'BayParkingLot_grass_s130'
part = 'all'
user = 'ArakawaT'
comment = 'density map'
tokens = {'project':'kibble', 'sequence':seq, 'shot':shot,
		  'name':name, 'part':part, 'datatype':'animation', 'context':'', 'variant':''}
mzAssetIO.PublishAnimation(tokens, targetNodes = [masterfile], ExportSelection=False, log=comment, user=user)

# 050

import yetiCache
reload(yetiCache)
scene = 'z:/marza/proj/kibble/work/280/050/light/ArakawaT/dummy/scenes/280_050_dummy_default_v001.ma'
cpath = 'z:/marza/proj/kibble/work/280/050/light/ArakawaT/grassc/data'
prefix = 'grassc'
path = '%s/%s.fur' % (cpath, prefix)
frameRange = (1040, 1602)
yetiShape = 'lotVariationGrassANew_geoShape'
useLicense=True
yetiCache.cacheYeti(scene, path, yetiShape, frameRange, useLicense=useLicense)

# 130

import yetiCache
reload(yetiCache)
scene = 'z:/marza/proj/kibble/work/280/130/light/ArakawaT/dummy/scenes/280_130_dummy_default_v001.ma'
cpath = 'z:/marza/proj/kibble/work/280/130/light/ArakawaT/grass/data'
prefix = 'grass'
path = '%s/%s.fur' % (cpath, prefix)
frameRange = (2173, 2264)
yetiShape = 'lotVariationGrassANew_geoShape'
useLicense=True
yetiCache.cacheYeti(scene, path, yetiShape, frameRange, useLicense=useLicense)

# 340

import yetiCache
reload(yetiCache)
scene = 'z:/marza/proj/kibble/work/280/340/light/ArakawaT/dummy/scenes/280_340_dummy_default_v003.ma'
cpath = 'z:/marza/proj/kibble/work/280/340/light/ArakawaT/grass/data'
prefix = 'grass'
path = '%s/%s.fur' % (cpath, prefix)
frameRange = (4149, 4289)
yetiShape = 'lotVariationGrassB_geoShape'
useLicense=True
yetiCache.cacheYeti(scene, path, yetiShape, frameRange, useLicense=useLicense)


import yetiCache
reload(yetiCache)
import os
scene = None
#scene = 'z:/marza/proj/kibble/work/276/640/lookdev/ArakawaT/optimize/scenes/276_640_optimize_default_v003.mb'
if not scene :
    scene = cmds.file(q=True,sn=True)
    print(scene)
proj = os.path.split(os.path.dirname(scene))[0]
cpath = os.path.join(proj, 'data').replace('\\', '/')
print(cpath)
prefix = 'grass'
path = '%s/%s.fur' % (cpath, prefix)
frameRange = (cmds.playbackOptions(q=True, minTime=True), cmds.playbackOptions(q=True, maxTime=True))
useLicense=False
for n in cmds.ls(sl=True, type='pgYetiMaya') :
    print(n)
    yetiShape = n
    yetiCache.cacheYeti(scene, path, yetiShape, frameRange, useLicense=useLicense)


# create anim file
import yetiCache
reload(yetiCache)
nodes = yetiCache.getTargetNodes()
print(nodes)
namespace = 'BayParkingLot_grass_s130'
text = yetiCache.createAnimContent(namespace, nodes)
print(text)
wd = cmds.workspace(q=True, rd=True)
path = os.path.join(wd, namespace+'.ma').replace('\\', '/')
print(path)
open(path, 'w').write(text)

# publish anim file
import mzAssetIO
seq = '280'
shot = '130'
name = namespace
part = 'all'
user = 'ArakawaT'
comment = 'density map'
tokens = {'project':'kibble', 'sequence':seq, 'shot':shot,
		  'name':name, 'part':part, 'datatype':'animation', 'context':'', 'variant':''}
mzAssetIO.PublishAnimation(tokens, targetNodes = [masterfile], ExportSelection=False, log=comment, user=user)

# frustum

import ld_frustrum
reload(ld_frustrum)
seq = '280'
shot = '085'
camera = 's%s_%s:camShape' % (seq, shot)
obj = 'hillAC'
targetobj = '%s_geoShape' % obj
outpath = 'Z:/marza/proj/kibble/work/%s/%s/lookdev/ArakawaT/optimize/textures/%s' % (seq, shot, obj)
tokens = ld_frustrum.getDefaultTokens()
tokens['margin'] = 1.5
tokens['resolution'] = 4096
tokens['clipByResolution'] = False
ld_frustrum.bakeFrustrum(camera, targetobj, outpath, frameRange=None, tokens=tokens, dispatch=True)

# frustum multi

import ld_frustrum
reload(ld_frustrum)
seq = '280'
shot = '085'
camera = 's%s_%s:camShape' % (seq, shot)
objs = cmds.ls(sl=True, type='mesh')
for o in objs :
	obj = o.split('_')[0]
	targetobj = o
	outpath = 'Z:/marza/proj/kibble/work/%s/%s/lookdev/ArakawaT/optimize/textures/%s' % (seq, shot, obj)
	tokens = ld_frustrum.getDefaultTokens()
	tokens['margin'] = 1.5
	tokens['resolution'] = 4096
	tokens['clipByResolution'] = False
	ld_frustrum.bakeFrustrum(camera, targetobj, outpath, frameRange=None, tokens=tokens, dispatch=True)

# textureFrame

nodes = cmds.ls(type='pgYetiMaya')
attr = 'yetiVariableF_textureFrame'
for n in nodes :
	if not cmds.attributeQuery(attr, n=n, ex=True) :
		cmds.addAttr(n, ln=attr, at='double')
		cmds.setAttr(n+'.'+attr, e=True, keyable=True)
	if not cmds.listConnections(n+'.'+attr) :
		cmds.connectAttr('time1.outTime', n+'.'+attr)

# time

nodes = cmds.ls(type='pgYetiMaya')
for n in nodes :
	try :
		cmds.connectAttr('time1.outTime', n+'.currentTime', f=True)
	except :
		pass