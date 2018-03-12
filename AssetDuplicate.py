import omoikane.client.functions as func
import omoikane.client.datatypes as dt
import mzAssetIO
import maya.cmds as cmds


class AssetDuplicate(object) :
	def __init__(self, assetgroup, name) :
		self.proj = 'onyx'
		self.name = name
		self.part = 'all'
		self.group = assetgroup
		self.context = 'mid'
		self.variant = 'default'
		self.master = None
		self.shots = {}
		self.doModel = True
		self.doShader = True
		self.doRig = True
		self.doBakeList = True
		self.user='NakaiT'
	def __getAssetTemplate( self, tokens ):
		templates = func.list_assets( project=tokens['project'], name=tokens['name'], part=tokens['part'], context=tokens['context'],
									  datatype=tokens['datatype'], variant=tokens['variant'], asset_group=tokens['asset_group'] )
		if ( templates == None or len( templates ) == 0 ): return None
		return templates[0]
	def capitalize(self, word) :
		return word[0].capitalize()+word[1:]
	def publishAssetToShots(self, tokens) :
		doit = eval('self.do%s' % self.capitalize(tokens['datatype']))
		if doit :
			print('-'*60)
			print('[AssetPublish]publishing %s...' % tokens['datatype'])
			for seq in self.shots :
				for shot in self.shots[seq] :
					tokens['sequence'] = seq
					tokens['shot'] = shot
					self.publishAsset(tokens)
	def publishAsset( self, tokens ) :
		print('publishing to (%s, %s)' % (tokens['sequence'], tokens['shot']))
		comment = 'copied from %s/%s' % (self.master[0], self.master[1])
		cmd = 'mzAssetIO.Publish%s(token=tokens, targetNodes=[], ExportSelection=True, user="%s", log="%s")' % (self.capitalize(tokens['datatype']), self.user, comment)
		print(cmd)
		inst = None
		inst = eval(cmd)
		if inst != None :
			print('published successfully.')
		else :
			print('SOMETHING IS WRONG!!!!')
	def importLatestAsset(self, tokens) :
		tmpl = self.__getAssetTemplate(tokens)
		tokens['version'] = tmpl.get_latest_version(self.master[0], self.master[1])
		mzAssetIO.Import(token=tokens, namespace='', targetNamespace='', additional_tokens={})
	def run(self) :
		if self.master[0] and self.master[1] :
			print(self.name, self.master)
		else :
			print('Invalid master.', self.master)
			return
		tokens = {}
		tokens['project'] = self.proj
		tokens['sequence'] = self.master[0]
		tokens['shot'] = self.master[1]
		tokens['asset_group'] = self.group
		tokens['name'] = self.name
		tokens['part'] = self.part
		tokens['context'] = self.context
		tokens['variant'] = self.variant

		if self.doModel or self.doShader :
			cmds.file(f=True, new=True)
			tokens['datatype'] = 'model'
			self.importLatestAsset(tokens)
			
			# publish model
			cmds.select('renderGeo_gp')
			tokens['datatype'] = 'model'
			self.publishAssetToShots(tokens)
			
			# publish shader
			cmds.select('renderGeo_gp')
			tokens['datatype'] = 'shader'
			self.publishAssetToShots(tokens)

		
		if self.doRig or self.doBakeList :
			cmds.file(f=True, new=True)
			tokens['datatype'] = 'rig'
			tokens['sequence'] = self.master[0]
			tokens['shot'] = self.master[1]
			self.importLatestAsset(tokens)

			# publish rig
			tokens['datatype'] = 'rig'
			cmds.select('root')
			tokens['sequence'] = self.master[0]
			tokens['shot'] = self.master[1]
			self.publishAssetToShots(tokens)
			
			cmds.file(f=True, new=True)
			tokens['sequence'] = self.master[0]
			tokens['shot'] = self.master[1]
			tokens['datatype'] = 'rig'
			self.importLatestAsset(tokens)
			tokens['datatype'] = 'bakeList'
			self.importLatestAsset(tokens)
			
			# publish bakeList
			tokens['datatype'] = 'bakeList'
			cmds.select(cmds.ls(type='bakeList')[0])
			self.publishAssetToShots(tokens)
	"""
	"""
	pass
		

if __name__ == '__main__' :
	ast = AssetDuplicate('okeInt', 'okBridge')
	ast.master = ('DFOkBridge', 'Sc070c01')
	ast.shots['ASOkBridge'] = ['ALL']
	sst.shots['JBOkBridge'] = ['ALL']
	ast.run()
	
	ast = AssetDuplicate('arcInt', 'arcBrgA')
	ast.master = ('GBArcInside', 'Sc015c16')
	ast.shots['IAArcBridge'] = ['ALL']
	ast.shots['TOArcBridge'] = ['ALL']
	ast.shots['TKArcBridge'] = ['ALL']
	ast.shots['ASArcInside'] = ['ALL']
	ast.shots['EAArcBridge'] = ['ALL']
	ast.shots['CWArcBridge'] = ['ALL']
	ast.shots['ARArcBridge'] = ['ALL']
	ast.shots['TEArcBridge'] = ['ALL']
	ast.shots['OBArcBridge'] = ['ALL']
	ast.run()