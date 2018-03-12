from maya import cmds
from maya import mel

unsupported =  {'reflInterpolation':False,
                #'reflMapMinRate',
                #'reflMapMaxRate',
                #'reflMapColorThreshold',
                #'reflMapNormalThreshold',
                #'reflMapSamples',
                'reflectOnBackSide':False,
                'softenEdge':0.0,
                'fixDarkEdges':False,
                'reflectionDimDistanceOn':False,
                #'reflectionDimDistance',
                #'reflectionDimFallOff'
                'refrDispersionOn':False,
                #'refrDispersionAbbe',
                'refrInterpolation':False,
                #'refrMapMinRate',
                #'refrMapMaxRate',
                #'refrMapColorThreshold',
                #'refrMapNormalThreshold',
                #'refrMapSamples'
                'traceRefractions':True,
                'affectShadows':False,
                'affectAlpha':0,
                'fogMult':1.0,
                'fogBias':0.0,
                'sssOn':False,
                #'translucencyColor',
                #'thickness',
                #'scatterCoeff',
                #'scatterDir',
                #'scatterLevels',
                #'sssEnvironment',
                }

warnattr = {
            'hilightGlossinessLock':True,
            'anisotropy':0,
            'fogColor':[(1,1,1)],
            'bumpMapType':0
            }
                
attrmap = {
            # basic
            'color':'diffuseColor',
            'diffuseColorAmount':'diffuseWeight',
            'transparency':'opacity',
            'roughnessAmount':'diffuseRoughness',
            'illumColor':'emissionColor',
            
            # reflection
            'reflectionColor':'specularColorP',
            'reflectionColorAmount':'specularWeightP',
            'reflectionExitColor':'reflectionExitColor',
            'useFresnel':'specularFresnelP',
            'fresnelIOR':'specularFresnelIorP',
            
            # refraction
            'refractionColor':'refractionColor',
            'refractionColorAmount':'refractionWeight',
            'refractionGlossiness':'refractionRoughness',
            'refractionIOR':'refractionIor',
            'fogColor':'refractionTransmittance'
            }
 
class v2aConverter(object) :
    def __init__(self, vrmtl) :
        std = vrmtl.replace('_ss','')+'Arnold_ss'
        print('-'*50)
        print('[%s] --> [%s]' % (vrmtl,std))
        std = cmds.shadingNode('mzStandardShader', asShader=True, n=std)
        self.src = vrmtl
        self.dst = std
    def checkUnsupported(self) :
        global unsupported
        for u in unsupported :
            if not cmds.getAttr(self.src+'.'+u) == unsupported[u] :
                print('--[ERROR %s] unsupported attr used.' % u)
    def checkWarnings(self) :
        global warnattr
        for w in warnattr :
            if not cmds.getAttr(self.src+'.'+w) == warnattr[w] :
                print('--[WARNING %s] might not be converted well.' % w)
    def matchAttribute(self, srcattr, dstattr) :
        sattr = self.src+'.'+srcattr
        dattr = self.dst+'.'+dstattr
        conn = cmds.listConnections(sattr, p=True, s=True)
        if conn == None or len(conn) == 0 :
            if cmds.getAttr(sattr, type=True) == 'float3' :
                val = cmds.getAttr(sattr)[0]
                vals = str(val)[1:-1]
                cmd = 'cmds.setAttr("%s", %s, type="float3")'% (dattr, vals)
                eval(cmd)
            else :
                cmds.setAttr(dattr, cmds.getAttr(sattr))
        else :
            cmds.connectAttr(conn[0], dattr)
    def doConvert(self) :
        global attrmap
        # simple one-to-one matching
        for a in attrmap :
            self.matchAttribute(a, attrmap[a])
            
        # overall overrides
        cmds.setAttr(self.dst+'.specularFresnelTypeP', 0)
        cmds.setAttr(self.dst+'.reflectionFresnelType', 0)
        
        # basic parater overrides
        if cmds.getAttr(self.src+'.illumColor')[0] != (0,0,0) or cmds.listConnections(self.src+'.illumColor') != None :
            cmds.setAttr(self.dst+'.emissionWeight', 1.0)
            
        # reflection overrides
        # anisotropy
        aniso = cmds.getAttr(self.src+'.anisotropy')
        if aniso != 0.0 :
            aniso = aniso*0.5 + 0.5
            cmds.setAttr(self.dst+'.specularAnisotropyP', aniso)
            conn = cmds.listConnections(self.src+'.anisotropyUVWGen')
            if conn == None or len(conn) == 0 :
                pass
            else :
                self.matchAttribute('anisotropyRotation', 'specularRotationP')
        # specular roughness
        rmin = 0.1
        roffset = -0.1
        anisogain = 4.0
        rattr = 'reflectionGlossiness'
        if not cmds.getAttr(self.src+'.hilightGlossinessLock') :
            rattr = 'hilightGlossiness'
        rval = cmds.getAttr(self.src+'.'+rattr)
        conn = cmds.listConnections(self.src+'.'+rattr)
        if conn == None or len(conn) == 0 :
            # when uniform value is used for specular roughness
            rgh = 1.0-rval+roffset
            if cmds.getAttr(self.src+'.anisotropy') != 0.0 :
                rgh *= anisogain
            rgh = min(1.0, max(0.1, rgh))
            print('SpecularRoughness original: %f after: %f' % (rval, rgh))
            cmds.setAttr(self.dst+'.specularRoughnessP', rgh)
        else:
            # when node is connected to specular roughness
            gnode = cmds.shadingNode('gammaCorrect', asUtility=True)
            cmds.connectAttr(conn[0]+'.outColor', gnode+'.value')
            cmds.setAttr(gnode+'.gamma', 2.2, 2.2, 2.2, type='float3')
            rnode = cmds.shadingNode('reverse', asUtility=True)
            cmds.connectAttr(gnode+'.outValue', rnode+'.input')
            pnode = cmds.shadingNode('plusMinusAverage', asUtility=True)
            cmds.connectAttr(rnode+'.output', pnode+'.input3D[0]')
            cmds.setAttr(pnode+'.input3D[1]', roffset, roffset, roffset, type='float3')
            mnode = cmds.shadingNode('multiplyDivide', asUtility=True)
            cmds.connectAttr(pnode+'.output3D', mnode+'.input1')
            rgh = 1.0
            if cmds.getAttr(self.src+'.anisotropy') != 0.0 :
                rgh = anisogain
            cmds.setAttr(mnode+'.input2', rgh, rgh, rgh, type='float3')
            cnode = cmds.shadingNode('clamp', asUtility=True)
            cmds.connectAttr(mnode+'.output', cnode+'.input')
            cmds.setAttr(cnode+'.min', rmin, rmin, rmin, type='float3')
            cmds.setAttr(cnode+'.max', 1, 1, 1, type='float3')
            cmds.connectAttr(cnode+'.outputR', self.dst+'.specularRoughnessP')
        # match reflection ior with refraction ior
        if cmds.getAttr(self.src+'.lockFresnelIORToRefractionIOR') :
            self.matchAttribute('refractionIOR', 'specularFresnelIorP')
        # trace reflection
        if cmds.getAttr(self.src+'.traceReflections') :
            self.matchAttribute('reflectionColor', 'reflectionColor')
            #self.matchAttribute('reflectionColorAmount', 'reflectionWeight')
            self.matchAttribute('useFresnel', 'reflectionFresnel')
            self.matchAttribute('fresnelIOR', 'reflectionFresnelIor')
            
        # refraction overrides
        if cmds.getAttr(self.src+'.refractionExitColorOn') :
            self.matchAttribute('refractionExitColor', 'refractionExitColor')
            
        # bump map overrides
        conn = cmds.listConnections(self.src+'.bumpMap')
        if conn == None or len(conn) == 0 :
            pass
        else :
            gnode = cmds.shadingNode('gammaCorrect', asUtility=True)
            cmds.connectAttr(conn[0]+'.outColor', gnode+'.value')
            cmds.setAttr(gnode+'.gamma', 2.2, 2.2, 2.2, type='float3')
            b2d = cmds.shadingNode('bump2d', asUtility=True)
            cmds.connectAttr(gnode+'.outValueX', b2d+'.bumpValue')
            cmds.setAttr(b2d+'.bumpDepth', cmds.getAttr(self.src+'.bumpMult'))
            cmds.connectAttr(b2d+'.outNormal', self.dst+'.normalCamera')

    def switchAssignment(self) :
        conn = cmds.listConnections(self.src+'.outColor', type='shadingEngine')
        if conn == None or len(conn) == 0 :
            return
        else :
            cmds.disconnectAttr(self.src+'.outColor', conn[0]+'.surfaceShader')
            cmds.connectAttr(self.dst+'.outColor', conn[0]+'.surfaceShader')
        
class vl2alConverter(object) :
    def __init__(self, vl) :
        self.src = vl
        tra = cmds.listRelatives(vl, p=True)[0]
        self.src = tra
        self.dst = cmds.shadingNode('areaLight', asLight=True)
        self.dst = cmds.rename(self.dst, tra+'Arnold')
        print('-'*50)
        print('[%s] --> [%s]' % (self.src,self.dst))
    def doConvert(self) :
        lc = cmds.getAttr(self.src+'.lightColor')[0]
        if cmds.getAttr(self.src+'.useRectTex') :
            bl = cmds.shadingNode('blendColors', asUtility=True)
            cmds.setAttr(bl+'.blender', 1.0)
            cmds.setAttr(bl+'.color1', lc[0], lc[1], lc[2], type='float3')
            mul = cmds.shadingNode('multiplyDivide', asUtility=True)
            cmds.connectAttr(bl+'.output', mul+'.input1')
            rectex = cmds.listConnections(self.src+'.rectTex')[0]
            cmds.connectAttr(rectex+'.outColor', mul+'.input2')
            cmds.connectAttr(mul+'.output', self.dst+'.color')
        else :
            cmds.setAttr(self.dst+'.color', lc[0], lc[1], lc[2], type='float3')
        cmds.setAttr(self.dst+'.intensity', cmds.getAttr(self.src+'.intensityMult'))
        tr = cmds.getAttr(self.src+'.translate')[0]
        rot = cmds.getAttr(self.src+'.rotate')[0]
        sc = cmds.getAttr(self.src+'.scale')[0]
        cmds.setAttr(self.dst+'.translate', tr[0], tr[1], tr[2], type='float3')
        cmds.setAttr(self.dst+'.rotate', rot[0], rot[1], rot[2], type='float3')
        cmds.setAttr(self.dst+'.scale', sc[0], sc[1], sc[2], type='float3')

def v2a() :
    selected = cmds.ls(sl=True, type='VRayMtl')
    targets = []
    if selected == None or len(selected) == 0 :
        print('Converting ALL VRayMtls to mzStandardShader')
        targets = cmds.ls(type='VRayMtl')
        print(targets)
    else :
        targets = selected
    for t in targets :
        print('%d/%d' % (targets.index(t)+1, len(targets)))
        converter = v2aConverter(t)
        converter.checkUnsupported()
        converter.checkWarnings()
        converter.doConvert()
        converter.switchAssignment()
        pass
    print('-'*50)
    print('Conversion Done.')

def vl2al() :
    selected = cmds.ls(sl=True, type='VRayLightRectShape')
    targets = []
    if selected == None or len(selected) == 0 :
        print('Converting All VRayLightRectShape')
        targets = cmds.ls(type='VRayLightRectShape')
    else :
        targets = selected
    for t in targets :
        converter = vl2alConverter(t)
        converter.doConvert()


def exrFileGamma(f) :
    path = cmds.getAttr(f+'.fileTextureName')
    if path.endswith('.exr') :
        if cmds.attributeQuery('vrayFileGammaEnable', n=f, ex=True) and cmds.getAttr(f+'.vrayFileGammaEnable') :
            if (cmds.getAttr(f+'.vrayFileColorSpace') == 1 and int(cmds.getAttr(f+'.vrayFileGammaValue')*10) == 22) or cmds.getAttr(f+'.vrayFileColorSpace') == 2:
                print( '[%s] %s: reverse gamma applied' % (f, path))
                return True
    return False

def convertToLDR(f) :
    import os
    path = cmds.getAttr(f+'.fileTextureName')
    if not os.path.isfile(path) :
        print('[ERROR] missing: %s' % path    )
        return False
    os.system('"Z:/ve/team/rnd/tools/modeling/houdini/11.1.118/windows/x64/bin/iconvert.exe" %s %s' % (path,path.replace('.exr','.tga')))

def checkExrFileGamma() :
    files = cmds.ls(type='file')
    out = []
    for f in files :
        if exrFileGamma(f) :
            res = convertToLDR(f)
            if not res :
                out.append(f)

def traverseTree(node) :
    avoid = ['mesh','locator','place2dTexture', 'place3dTexture', 'defaultShaderList', 'lightLinker', 'materialInfo', 'shadingEngine']
    attrs = cmds.listAttr(node, r=True, c=True)
    for a in attrs :
        try :
            conn = cmds.listConnections(node+'.'+a, s=True, d=False)
        except :
            continue
        if conn != None :
            for c in conn :
                if not cmds.objectType(c) in avoid and c != node:
                    #print(c)
                    traverseTree(c)
        else :
            if 'VRay' in cmds.objectType(node) :
                print('skipping... %s' % node)
                continue
            if cmds.attributeQuery(a, n=node, usedAsColor=True) :
                orig = cmds.getAttr(node+'.'+a)[0]
                if 0<orig[0]<1.0 or 0<orig[1]<1.0 or 0<orig[2]<1.0 :
                    blendcol = cmds.shadingNode('blendColors', asUtility=True)
                    cmds.setAttr(blendcol+'.blender', 1.0)
                    cmds.setAttr(blendcol+'.color2', 0, 0, 0, type='float3')
                    cmds.setAttr(blendcol+'.color1', orig[0], orig[1], orig[2], type='float3')
                    gamma = cmds.shadingNode('gammaCorrect', asUtility=True)
                    cmds.setAttr(gamma+'.gamma', 2.2, 2.2, 2.2, type='float3')
                    cmds.connectAttr(blendcol+'.output', gamma+'.value')
                    cmds.connectAttr(gamma+'.outValue', node+'.'+a)

def fixUniformColors() :
    omit = ['initialShadingEngine', 'initialParticleSE']
    selected = cmds.ls(sl=True)
    if selected != [] :
        for s in selected :
            traverseTree(s)
    else :
        engines = cmds.ls(type='shadingEngine')
        for e in engines :
            if e in omit :
                continue
            ss = cmds.listConnections(e+'.surfaceShader')
            if ss == None :
                continue
            traverseTree(ss[0])

def checkIORLimit() :
    for v in cmds.ls(type='VRayMtl') :
        if cmds.getAttr(v+'.fresnelIOR') > 10 :
            cmds.setAttr(v+'.fresnelIOR',10)
            print(v)

def vsub() :
	mesh = cmds.ls(type='mesh')
	for m in mesh :
		if cmds.attributeQuery('vraySubdivEnable', n=m, ex=True) and cmds.getAttr(m+'.vraySubdivEnable') :
			cmds.setAttr(m+'.aiSubdivIterations', 2)
			cmds.setAttr(m+'.aiSubdivType', 1)
			print(m)

def useTx() :
	import os
	files = cmds.ls(type='file')
	targets = ['.tif', '.tga']
	for f in files :
		path = cmds.getAttr(f+'.fileTextureName')
		ext = os.path.splitext(path)[1]
		if ext in targets :
			path = path.replace(ext, '.tx')
			if os.path.isfile(path) :
				print('[%s] ok' % f)
				cmds.setAttr(f+'.fileTextureName', path, type='string')
			else :
				print('[%s] missing tx: %s' % (f,path) )