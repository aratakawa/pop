from maya import cmds

def parseTree(node) :
    aovsupported = ['mzStandardShader', 'mzStandardMerge', 'LayeredShader']
    if cmds.objectType(shader) in aovsupported :
        return True
    nodes = cmds.listConnections(shader, d=False, s=True)
    if nodes == None or len(nods) == 0 :
        return False
    for n in nodes :
        if parseTree(n) :
            return True
    return False

def checkAOVSupport() :
    engines = cmds.ls(type='shadingEngine')
    omit = ['initialShadingGroup', 'lambert1', 'initialParticleSE']
    invalid = []
    for e in engines :
        if e in omit :
            continue
        shader = cmds.listConnections(e+'.surfaceShader')
        if shader == None or len(shader) == 0 :
            continue
        shader = shader[0]
        if shader in omit :
            continue
        supported = parseTree(shader)
        if supported:
            #print('supported: %s' % shader)
            pass
        else :
            print('NOT supported: %s' % shader)
            invalid.append(shader)

    if len(invalid) > 0 :
        cmds.select(invalid)