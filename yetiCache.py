# -*- coding: utf-8 -*-
import yetiUtils.cache as yc
import os, re, datetime, re
#

import xml.etree.ElementTree as ET

import hutils
import yetiUtils._maya as yum
 
#import yetiUtils._maya as YUM
#YUM.cacheWithoutLicense('%s/%s.fur' % (path, prefix), nodes, startFrame=start, endFrame=end, sampleTimes=[0], verbose=True, perFrameCache=False)

def getDatetimeText(datetimeObj, mayaStyle = False):
	if datetimeObj is None:
		datetimeObj = datetime.datetime.now()
	dateText = ''
	if mayaStyle:
		dateText = '%04d/%02d/%2d' % (datetimeObj.year, datetimeObj.month, datetimeObj.day)
	else:
		dateText = '%4d-%02d-%02d' % (datetimeObj.year, datetimeObj.month, datetimeObj.day)
	return '%s %02d:%02d:%02d' % (dateText, datetimeObj.hour, datetimeObj.minute, datetimeObj.second)

def getTargetNodes() :
	from maya import cmds
	import maya.OpenMaya as om
	nodes = cmds.ls(type='pgYetiMaya')
	targets = {}
	if not nodes :
		return targets
	for n in nodes :
		if cmds.getAttr(n+'.fileMode') != 2 :
			om.MGlobal.displayError('[Error] Not Cache Mode : %s' % n)
			continue
		targets[n] = cmds.getAttr(n+'.cacheFileName')
	return targets
	
def createAnimContent(namespace, nodes) :
	nodeTemplate = """
select ":<NAMESPACE>:<YETI_SHAPE>";
setAttr -type "string" ".cacheFileName" "<CACHE_PATH>";
setAttr ".fileMode" 2; // cache
setAttr ".recache" 0;
"""

	if not nodes :
		return None

	from maya import cmds
	mayaVersion = cmds.about(file = 1)
	text = ''
	####
	text += '//Maya ASCII %s scene\n' % mayaVersion
	text += '//Last modified: %s\n' % getDatetimeText(None, mayaStyle = 1)
	text += 'requires maya "%s";\n' % mayaVersion
	text += 'currentUnit -l centimeter -a degree -t film;\n'
	####

	if nodes :
		for n in nodes :
			ntext = nodeTemplate
			ntext = ntext.replace('<NAMESPACE>', namespace)
			ntext = ntext.replace('<YETI_SHAPE>', n)
			ntext = ntext.replace('<CACHE_PATH>', nodes[n])
			text += ntext
	return text
 
def cacheYeti(scene, path, yetiShape, frameRange, useLicense=False) :
	if not yetiShape :
		print('[Error] No yeti node provided.')
		return
	startFrame, endFrame = frameRange
	basedir = os.path.split(scene)[0]
	projdir = os.path.split(basedir)[0]
	
	tokens = hutils.getDefaultTokens()
	tokens['threads'] = 0
	maincommand = 'import yetiUtils._maya as yum;'
	if useLicense :
		maincommand += 'yum.cache(\\\\\\"%s\\\\\\", yetiShapes=[\\\\\\"%s\\\\\\"], frameRange=(%d,%d), verbose=True, useLicense=%s);' % (path, yetiShape, startFrame, endFrame, str(useLicense))
	else :
		prefix = os.path.basename(path).split('.')[0]
		outname = '%s_%s.fur' % (prefix, yetiShape)
		outpath = os.path.join(os.path.dirname(path), outname).replace('\\','/')
		maincommand += 'yum.cacheWithoutLicense(\\\\\\"%s\\\\\\", [\\\\\\"%s\\\\\\"], startFrame=%d, endFrame=%d, sampleTimes=[0], verbose=True);' % (outpath, yetiShape, startFrame, endFrame)

	print(maincommand)

	command = hutils.envwrapCmd()
	command += 'mayabatch -proj "%s" -file "%s" ' % (projdir, scene)
	command += '-command "python(\\\"%s\\")"' % (maincommand)

	hutils.dispatchSingleCommand(tokens, command)

def getFrameByName(name) :
	frame = None
	m = re.search('\.\d\d\d\d\.', name)
	if not m :
		print('Frame number not found in filename.')
	else :
		frame = int(m.group()[1:-1])
		print('Frame number from filename: %04d' % frame)
	return frame

def freezeTextureFrame(cache, frame=None) :
	import h5py
	ca = h5py.File(cache, 'r+')
	xmlpath = os.path.splitext(cache)[0]+'.xml'
	if frame is None :
		frame = getFrameByName(cache)
		if frame is None :
			return
	if yc.extractXMLFromCache(ca, xmlpath) :
		tree = ET.parse(xmlpath)
		for r in tree.getroot().findall("./*"):
			#print(r.tag)
			nt = r.attrib.get('type', '')
			if nt == 'texture' :
				fn = r.find('./file_name')
				if fn is None :
					continue
				texpath = fn.attrib.get('value', '')
				if '%04d' in texpath :
					print(r.tag)
					rpath = texpath % frame
					print('%s -> %s' % (texpath,rpath))
					fn.attrib['value'] = rpath
		tree.write(xmlpath)
		yc.updateCache(ca, xmlpath, '')
		os.remove(xmlpath)
					
def setGlobalDensityPath(cache, texpath, frame=None) :
	ca = h5py.File(cache, 'r+')
	xmlpath = os.path.splitext(cache)[0]+'.xml'
	if frame is None :
		frame = getFrameByName(cache)
		if frame is None :
			return
	if yc.extractXMLFromCache(ca, xmlpath) :
		tree = ET.parse(xmlpath)
		for r in tree.getroot().findall("./*"):
			#print(r.tag)
			nt = r.attrib.get('type', '')
			if nt == 'texture' and r.tag == 'globalDensityCulling' :
				fn = r.find('./file_name')
				if fn is None :
					continue
				fn.attrib['value'] = texpath
		tree.write(xmlpath)
		yc.updateCache(ca, xmlpath, '')
		os.remove(xmlpath)	
					
if __name__ == '__main__' :
	import yetiCache
	reload(yetiCache)

	texpath = 'Z:/marza/proj/kibble/work/PROJ/ALL/model/ArakawaT/frustum/textures/DnsMap/frustum_txDnsMap.%04d.tif'
	#cache = 'Z:/marza/proj/kibble/work/PROJ/ALL/model/ArakawaT/frustum/data/cache_pgYetiMayaShape_1378801158.0002.fur'
	
	"""
	cpath = 'Z:/marza/proj/kibble/work/PROJ/ALL/model/ArakawaT/frustum/data/cache_pgYetiMayaShape.%04d.fur'
	for i in range(1, 145) :
		print(cpath % i)
		yetiCache.freezeTextureFrame(cpath % i)
	"""
	
	cpath = 'Z:/marza/proj/kibble/work/PROJ/ALL/model/ArakawaT/frustum/data/noDensityMap/cache_pgYetiMayaShape.%04d.fur'
	for i in range(1, 145) :
		print(cpath % i)
		yetiCache.setGlobalDensityPath(cpath%i, texpath%i)
	
	import yetiCache
	reload(yetiCache)
	scene = 'z:/marza/proj/kibble/work/280/340/light/ArakawaT/grassb/scenes/280_340_grassb_default_v005.ma'
	cpath = 'z:/marza/proj/kibble/work/280/340/light/ArakawaT/grassb/data'
	prefix = 'grassb'
	path = '%s/%s.fur' % (cpath, prefix)
	frameRange = (4149, 4289)
	yetiShape = 'longFarGrass_geoShape'
	useLicense=True
	yetiCache.cacheYeti(scene, path, yetiShape, frameRange, useLicense=useLicense)