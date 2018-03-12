attrs = ['castsShadows','receiveShadows','motionBlur','primaryVisibility','smoothShading',
         'visibleInReflections','visibleInRefractions','doubleSided','opposite']
attrs.extend(['aiSelfShadows','aiOpaque','aiVisibleInDiffuse','aiVisibleInGlossy'])
attrs.extend(['aiSubdivType','aiSubdivIterations','aiSubdivAdaptiveMetric','aiSubdivPixelError',
              'aiSubdivUvSmoothing'])
attrs.extend(['aiExportTangents','aiExportColors'])
marzaAttrs = {'mtoa_invisible':['bool','Invisible'],'mtoa_matteout':['bool','Matte Out'],'mtoa_outputPref':['bool','Output Pref'],'mtoa_objectid':['long','Object ID']}


from maya import cmds

def setAttrs(obj,values):
    global attrs, marzaAttrs
    for attr in attrs :
        cmds.setAttr(obj+'.'+attr,values[attr])
    for attr in marzaAttrs.keys() :
        if not values.has_key(attr):
            continue
        if not cmds.attributeQuery(attr,ex=True,n=obj):
            cmds.addAttr(obj,ln=attr,at=marzaAttrs[attr][0],nn=marzaAttrs[attr][1])
            cmds.setAttr(obj+'.'+attr, e=True,keyable=True)
        #print(attr,values[attr])
        cmds.setAttr(obj+'.'+attr,values[attr])

def getAttrs(obj) :
    global attrs, marzaAttrs
    values = {}
    for attr in attrs :
        values[attr] = cmds.getAttr(obj+'.'+attr)
    for attr in marzaAttrs.keys() :
        if cmds.attributeQuery(attr,ex=True,n=obj) :
            values[attr] = cmds.getAttr(obj+'.'+attr)
    return values

def sameAttrs(a, b) :
    global attrs, marzaAttrs
    for attr in attrs:
        if cmds.getAttr(a+'.'+attr) != cmds.getAttr(b+'.'+attr) :
            return False
    for attr in marzaAttrs.keys():
        state = (cmds.attributeQuery(attr,ex=True,n=a)==cmds.attributeQuery(attr,ex=True,n=b))
        if not state :
            return False
        if cmds.attributeQuery(attr,ex=True,n=a) :
            if cmds.getAttr(a+'.'+attr) != cmds.getAttr(b+'.'+attr) :
                return False
    return True

def run() :
    from maya import cmds
    orig = cmds.ls(sl=True)

    cmds.select(hi=True)
    mesh = cmds.ls( type='mesh', sl=True, long=True )
    engines = {}
    for m in mesh :
        con = cmds.listConnections(m, type='shadingEngine')
        for c in con :
            if not engines.has_key(c) :
                engines[c] = []
            engines[c].append(m)

    for e in engines.keys() :
        objs = engines[e]
        print('[%s] %d objs.' % (e,len(objs)))
        groups = []
        while(len(objs)>0) :
            base = objs.pop(0)
            grp = []
            for o in objs :
                if sameAttrs(base,o) :
                   grp.append(o)
            for o in grp :
                objs.pop(objs.index(o))
            grp.append(base)
            groups.append(grp)
        for g in groups :
            print(' [group] %d objs' % len(g))
            g = list(set(g))
            if len(g) > 1:
                attrs = getAttrs(g[0])
                cmds.select(g)
                newobj = cmds.polyUnite(ch=False)
                newobj = cmds.listRelatives(newobj,c=True)
                #cmds.select(newobj,hi=True)
                #newobj = cmds.ls(sl=True,type='mesh')
                cmds.sets(e=True,forceElement=e)
                setAttrs(newobj[0],attrs)

    cmds.select(orig)