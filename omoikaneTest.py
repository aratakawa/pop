import omoikane.client.functions as ocf
import os

assets = {}
assetPacks = {}
seqShots = {}
shotElms = {}


def getProject() :
	return os.environ['MZ_ENV_PROJ']

def getLatestPack(asset_group=None, name=None, context=None, datatype=None, variant=None) :
	tmpls = ocf.list_packages(project=getProject(), asset_group=asset_group, name=name, context=context, datatype=datatype)
	for tmpl in tmpls :
		print(tmpl.name, tmpl.variant)
		#print(dir(tmpl))
		#latest = tmpl.get_latest_version()
		
		print(latest)
		
def printAssetPacks() :
	print('--------- AssetPacks ----------')
	global assetPacks
	for group in assetPacks :
		print('[%s] %d assets' % (group, len(assetPacks[group].keys())))
	print('')

def updateAssetPacks() :
	global assetPacks
	assetPacks = {}
	tmpls = ocf.list_assets(project=getProject())
	for tmpl in tmpls :
		#print(tmpl.asset_group, tmpl.name, tmpl.datatype, tmpl.context, tmpl.variant)
		if not assetPacks.has_key(tmpl.asset_group) :
			assetPacks[tmpl.asset_group] = {}
		if not assetPacks[tmpl.asset_group].has_key(tmpl.name) :
			assetPacks[tmpl.asset_group][tmpl.name] = {}
		if not assetPacks[tmpl.asset_group][tmpl.name].has_key(tmpl.datatype) :
			assetPacks[tmpl.asset_group][tmpl.name][tmpl.datatype] = {}
		if not assetPacks[tmpl.asset_group][tmpl.name][tmpl.datatype].has_key(tmpl.context) :
			assetPacks[tmpl.asset_group][tmpl.name][tmpl.datatype][tmpl.context] = {}
		if not assetPacks[tmpl.asset_group][tmpl.name][tmpl.datatype][tmpl.context].has_key(tmpl.variant) :
			assetPacks[tmpl.asset_group][tmpl.name][tmpl.datatype][tmpl.context][tmpl.variant] = []
		assetPacks[tmpl.asset_group][tmpl.name][tmpl.datatype][tmpl.context][tmpl.variant].append(tmpl)
	printAssetPacks()

def printAssets() :
	print('--------- Assets ----------')
	global assets
	for group in assets :
		print('[%s] %d assets' % (group, len(assets[group].keys())))
	print('')
		
def updateAssets() :
	global assets
	assets = {}
	tmpls = ocf.list_assets(project=getProject())
	for tmpl in tmpls :
		#print(tmpl.asset_group, tmpl.name, tmpl.datatype, tmpl.context, tmpl.variant)
		if not assets.has_key(tmpl.asset_group) :
			assets[tmpl.asset_group] = {}
		if not assets[tmpl.asset_group].has_key(tmpl.name) :
			assets[tmpl.asset_group][tmpl.name] = {}
		if not assets[tmpl.asset_group][tmpl.name].has_key(tmpl.datatype) :
			assets[tmpl.asset_group][tmpl.name][tmpl.datatype] = {}
		if not assets[tmpl.asset_group][tmpl.name][tmpl.datatype].has_key(tmpl.context) :
			assets[tmpl.asset_group][tmpl.name][tmpl.datatype][tmpl.context] = {}
		if not assets[tmpl.asset_group][tmpl.name][tmpl.datatype][tmpl.context].has_key(tmpl.part) :
			assets[tmpl.asset_group][tmpl.name][tmpl.datatype][tmpl.context][tmpl.part] = {}
		if not assets[tmpl.asset_group][tmpl.name][tmpl.datatype][tmpl.context][tmpl.part].has_key(tmpl.variant) :
			assets[tmpl.asset_group][tmpl.name][tmpl.datatype][tmpl.context][tmpl.part][tmpl.variant] = []
		assets[tmpl.asset_group][tmpl.name][tmpl.datatype][tmpl.context][tmpl.part][tmpl.variant].append(tmpl)
	printAssets()

def printSeqShots() :
	print('--------- SeqShot ----------')
	global seqShots
	seqs = seqShots.keys()
	seqs.sort()
	for seq in seqs :
		print('[%s] %d shots.' % (seq, len(seqShots[seq]['shots'])))
		
def updateSeqShots() :
	global seqShots
	seqs = ocf.list_sequences(project=getProject())
	for seq in seqs :
		if not seqShots.has_key(seq.name) :
			seqShots[seq.name] = {}
			seqShots[seq.name]['object'] = seq
		seqShots[seq.name]['shots'] = ocf.list_shots(project=getProject(), sequence=seq.name)
	printSeqShots()	

def updateShotElms() :
	global shotElms
	shotElms = ocf.list_shot_elements(project=getProject())
	
def updateData() :
	#updateAssetPacks()
	#updateAssets()
	updateSeqShots()
	updateShotElms()
	#assets = ocf.list_assets(project=getProject())
	#shots = ocf.list_shots(project=getProject())

def updateSeqInfo(seq) :
	global seqShots
	shots = seqShots[seq]['shots']
	for shot in shots :
		print('[%s_%s]' % (seq, shot.name))
		subscribed = ocf.get_construct_list(getProject(), seq, shot.name)
		for ns in subscribed['Package'].keys() :
			print(ns)
	
def setup() :
	updateData()

if __name__ == '__main__' :
	"""
	assets = ocf.list_assets(project=getProject(), context='mid', datatype='gto')
	for asset in assets :
		print('%s: %s (%s, %s, %s, %s)' % (asset.asset_group, asset.name, asset.datatype, asset.context, asset.variant, asset.part	))
	"""
	"""
	asset_group = 'Character'
	name = 'Kody'
	context = 'mid'
	datatype = 'rig'
	variant = 'default'
	getLatestPack(asset_group=asset_group, name=name, context=context, datatype=datatype, variant=variant)
	"""
	setup()
	updateSeqInfo('040')
	
	