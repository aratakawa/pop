import os

class PackageTemplate(object) :
	def __init__(self, name='Kody', context='mid', datatype='rig', variant='default') :
		self.name = name
		self.context = context
		self.datatype = datatype
		self.variant = variant
		self.packages = []

class Package(object) :
	def __init__(self) :
		pass

def getDirs(path) :
	out = []
	files = os.listdir(path)
	for f in files :
		if not os.path.isdir(os.path.join(path, f)) :
			continue
		out.append(f)
	out.sort()
	return out

def getProject() :
	return os.environ['MZ_ENV_PROJ']

def getRoot() :
	return os.environ['MZ_ENV_ROOT']
	
def getAssetPath() :
	return os.path.join(getRoot(), getProject(), 'asset').replace('\\','/')

def getAssetGroupPath(assetGroup) :
	return os.path.join(getAssetPath(), assetGroup).replace('\\', '/')

def getAssetPackPath(assetGroup, asset) :
	return os.path.join(getAssetPath(), assetGroup, asset, 'assetPack').replace('\\','/')
	
def getAssetPackFilePath(assetGroup, asset, seq, shot, datatype, context, variant) :
	return os.path.join(getAssetPackPath(assetGroup, asset), seq, shot, datatype, context, variant).replace('\\', '/') 
	
def getAssetPackSeq(assetGroup, asset) :
	path = getAssetPackPath(assetGroup, asset)
	return getDirs(path)
	
def getAssetPackShot(assetGroup, asset, seq) :
	path = os.path.join(getAssetPackPath(assetGroup, asset), seq).replace('\\','/')
	return getDirs(path)

def getAssetPackDatatype(assetGroup, asset, seq, shot) :
	path = os.path.join(getAssetPackPath(assetGroup, asset), seq, shot).replace('\\', '/')
	return getDirs(path)
	
def getAssetPackContext(assetGroup, asset, seq, shot, datatype) :
	path = os.path.join(getAssetPackPath(assetGroup, asset), seq, shot, datatype).replace('\\', '/')

def getAssetGroups() :
	path = getAssetPath()
	return getDirs(path)

def getAssets(assetGroup) :
	path = getAssetGroupPath(assetGroup)
	return getDirs(path)
	
def getAssetPacks(assetGroup, asset, context, datatype) :
	pshots = {}
	for seq in getAssetPackSeq(assetGroup, asset) :
		pshots[seq] = {}
		shots = getAssetPackShot(assetGroup, asset, seq)
		for shot in shots :
			pshots[seq][shot] = []
			datatypes = getAssetPackDatatype(assetGroup, asset, seq, shot)
			for d in datatypes :
				pshots[seq][shot].append(datatypes)
	

def list_packages(project='kibble', asset_group='Character', name='Kody', context='mid', datatype='rig') :
	pass

def getUpdatedAssetPacks() :
	assetGroups = getAssetGroups()
	for assetGroup in assetGroups :
		for asset in getAssets(assetGroup) :
			#print('[%s: %s]' % (g, a))
			for seq in getAssetPackSeq(assetGroup, asset) :
				for shot in getAssetPackShot(assetGroup, asset, seq) :
					for d in getAssetPackDatatype(assetGroup, asset, seq, shot) :
						for c in getAssetPackContext(assetGroup, asset, seq, shot, d) :
							for v in getAssetPackVariant(assetGroup, asset, seq, shot, d, c) :
								for f in os.listdir(getAssetPackFilePath(assetGroup, asset, seq, shot, d, c, v)) :
									print(f)
									
	