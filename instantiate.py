from maya import cmds
from maya import mel
import pymel.core as pc

def storeBelow( tree, root ) :
    roots = cmds.listRelatives( root, children=True, fullPath=True )
    for r in roots :
        if cmds.objectType( r ) == 'transform' :
            tree[r] = {}
            storeBelow( tree[r], r )
        elif cmds.objectType( r ) == 'mesh' :
            tree[r] = None

def printTree( tree, depth ) :
    for r in tree.keys() :
        if tree[r] != None :
            print( ' '*depth + r.split('|')[-1] )
            printTree( tree[r], depth+1 )
        else :
            print( ' '*depth + r.split('|')[-1] +'(' + cmds.objectType( r ) + ')' )

def selectInstancedObjects() :
    cmds.select( hi=True )
    mesh = cmds.ls( type='mesh', sl=True )
    instances = []
    for m in mesh :
        if( len(cmds.ls( m, ap=True, long=True )) > 1 ) :
            if m not in instances :
                instances.append( m )
                print( m )
    if len(instances) == 0 :
        cmds.select( cl=True )
        print( 'No object instanced.' )
    else :
        cmds.select( instances )

def isDirectParent( node ) :
    #print( node )
    children = cmds.listRelatives( node, children=True, fullPath=True )
    #print( children )
    if len(children) != 1 :
        return False
    if cmds.objectType( children[0] ) == 'mesh' :
        return True
    return False

def isIdentity( node ) :
    t = cmds.getAttr( node+'.translate' )[0]
    if t != (0,0,0) :
        return False
    r = cmds.getAttr( node+'.rotate' )[0]
    if r != (0,0,0) :
        return False
    s = cmds.getAttr( node+'.scale' )[0]
    if s != (0,0,0) :
        return False
    return True

def checkIdentityTree( tree ) :
    for r in tree.keys() :
        if tree[r] != None :
            if not isIdentity( r ) :
                print( 'Not Identity: %s(%s)' % (r,str(isDirectParent(r)) ) )
            checkIdentityTree( tree[r] )

def mirrorInstanceTree( tree, root ) :
    for r in tree.keys() :
        if tree[r] != None :
            """
            if not isIdentity( r ) :
                cmds.makeIdentity( r, apply=True, t=True, r=True, s=True, n=False )
            cmds.xform( piv=(0,0,0), ws=True )
            """
            if isDirectParent( r ) :
                #print( r.split('|')[-1].replace('_L', '_R') )
                #new = cmds.instance( r, n=r.split('|')[-1].replace('_L', '_R') )[0]
                #new = cmds.instance( r, n=r.split('|')[-1].replace('L', 'R') )[0]
                #new = cmds.instance( r, n=r.split('|')[-1] )[0]
                #cmds.parent( new, root )
                new = pc.instance(r,n=r.split('|')[-1])
                pc.parent( new, pc.ls(root)[0] )
            else :
                #subroot = cmds.group(em=True,n=r.split('|')[-1].replace('L','R'))
                #subroot = cmds.ls(sl=True,long=True)[0]
                #cmds.parent( subroot, root )
                subroot = pc.group(em=True,n=r.split('|')[-1])
                pc.parent(subroot,pc.ls(root)[0])
                mirrorInstanceTree( tree[r], subroot )

def mirrorInstance(parent=None) :
    tree = {}
    selected = cmds.ls( sl=True, long=True )
    cmds.select( cl=True )
    root = selected[0]
    parent = cmds.listRelatives(root,p=True,fullPath=True)[0]
    tree[root] = {}
    storeBelow( tree[root], root )
    #printTree( tree, 0 )
    #checkIdentityTree( tree[root] )
    """
    if parent != None :
        newroot = cmds.group( em=True, n=root.split('|')[-1], p=parent )
    else :
        newroot = cmds.group( em=True, n=root )
    """
    print(parent)
    newroot = cmds.group( em=True, n=root.split('|')[-1], p=parent )
    newroot = cmds.ls( sl=True, long=True )[0]
    mirrorInstanceTree( tree[root], newroot )
    cmds.select(newroot)
    return newroot

def checkIdentity() :
    tree = {}
    selected = cmds.ls( sl=True, long=True )
    cmds.select( cl=True )
    root = selected[0]
    tree[root] = {}
    storeBelow( tree[root], root )
    checkIdentityTree( tree[root] )

def matchTranslate() :
    selected = cmds.ls( sl=True, long=True )
    t = cmds.xform( selected[1], q=True, rp=True, ws=True )
    cmds.move( t[0], t[1], t[2], selected[0], a=True, ws=True, rpr=True )

def matchRotation() :
    selected = cmds.ls( sl=True, long=True )
    r = cmds.xform( selected[1], q=True, rotation=True, ws=True )
    cmds.rotate( r[0], r[1], r[2], selected[0], a=True, ws=True )

def matchScale() :
    selected = cmds.ls( sl=True, long=True )
    s = cmds.xform( selected[1], q=True, scale=True, ws=True )
    cmds.scale( s[0], s[1], s[2], selected[0], a=True )

def matchTargetScale() :
    selected = cmds.ls( sl=True, long=True )
    s = cmds.xform( selected[0], q=True, scale=True, ws=True )
    cmds.scale( s[0], s[1], s[2], selected[1], a=True )

def getShape( parent ) :
    return cmds.listRelatives( parent, children=True, fullPath=True )[0]

def separateObjs( tree ) :
    tra = []
    obj = []
    for r in tree.keys() :
        if isDirectParent( r ) :
            obj.append( r )
        else :
            tra.append( r )
    return tra, obj

def instantiateTree( stree, ttree, parent ) :
    stra, sobj = separateObjs( stree )
    ttra, tobj = separateObjs( ttree )
    for st in stra :
        for tt in ttra :
            if st.split('|')[-1] == tt.split('|')[-1] :
                print( 'transform: %s matches %s.' % (st,tt) )
                instantiateTree( stree[st], ttree[tt], tt )
    for so in sobj :
        for to in tobj :
            if so.split('|')[-1] == to.split('|')[-1] :
                print( 'object: %s matches %s.' % (so, to) )
                inst = cmds.instance( so )[0]
                sp = cmds.listRelatives( so, parent=True, fullPath=True )[0]
                inst = '%s|%s' % (sp,inst)
                cmds.select( inst )
                cmds.select( to, add=True )
                mel.eval( 'CenterPivot' )
                matchTranslate()
                matchRotation()
                #matchTargetScale()
                print( 'created: %s, parent: %s, newparent: %s' % (inst, sp, parent) )
                cmds.parent( inst, parent )
                cmds.delete( to )

def instantiate() :
    selected = cmds.ls( sl=True, long=True )
    source = selected[-1]
    targets = selected[0:-1]
    if isDirectParent( source ) :
        for t in targets :
            inst = cmds.instance( source )[0]
            sp = cmds.listRelatives( source, parent=True, fullPath=True )[0]
            tp = cmds.listRelatives( t, parent=True, fullPath=True )[0]
            inst = '%s|%s' % (sp,inst)
            cmds.select( inst )
            cmds.select( t, add=True )
            mel.eval( 'CenterPivot' )
            matchTranslate()
            matchRotation()
            print( 'created: %s, parent: %s' % (inst, sp) )
            try :
                cmds.parent( inst, tp )
            except :
                pass
            cmds.delete( t )
    else :
        stree = {}
        stree[source] = {}
        storeBelow( stree[source], source )
        for t in targets :
            ttree = {}
            ttree[t] = {}
            storeBelow( ttree[t], t )
            instantiateTree( stree[source], ttree[t], t )


#mirrorInstance()
#selectInstancedObjects()
#instantiate()
