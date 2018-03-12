import maya.cmds as cmds
import os, re

root = 'Z:/marza/proj/kibble/team/lookdev/ShaderLibrary'
omit = '.meta'
exts = ['.tga', '.tif']
textures = {}

def getTextures(path) :
	tex = {}
	categories = os.listdir(root)
	for c in categories :
		if c in omit :
			continue
		files = os.listdir(os.path.join(root,c,'textures'))
		for f in files :
			if os.path.splitext(f)[-1] in exts :
				if not tex.has_key(c) :
					tex[c] = []
				tex[c].append(f)
	return tex
	
def printTextures() :
	global textures
	for c in textures :
		for t in textures[c] :
			print('[%s] %s' % (c, t))

def foundInLibrary(name) :
	global textures
	for c in textures :
		for t in textures[c] :
			if name == t :
				return (c, t)
	return None

def getLibraryPath(category, name) :
	return os.path.join(root, category, 'textures', name).replace('\\', '/')

def useTextureFromLibrary() :
	global root
	files = cmds.ls(type='file')
	for f in files :
		path = cmds.getAttr(f+'.fileTextureName')
		if path.startswith(root) :
			continue
		base = os.path.split(path)[-1]
		name, ext = os.path.splitext(base)
		m = re.search('_\d$', name)
		if m :
			baseB = name[0:-2] + ext
			match = foundInLibrary(baseB)
			if match is not None :
				print('Found: %s %s' % (match[0], match[1]))
				cmds.setAttr(f+'.fileTextureName', getLibraryPath(match[0], match[1]), type='string')
				continue
		match = foundInLibrary(base)
		if match is not None :
			print('Found: %s %s' % (match[0], match[1]))
			cmds.setAttr(f+'.fileTextureName', getLibraryPath(match[0], match[1]), type='string')
textures = getTextures(root)