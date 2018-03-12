from maya import cmds
from maya import mel
import maya.OpenMaya as om

class MatchObj( object ) :
    def __init__( self, name ) :
        self.name = name
        self.pnum = cmds.polyEvaluate( self.name, vertex=True )
        self.basis = []
        self.rotationAxis = []
        self.matrix = []
    def createBasis( self ) :
        p1 = cmds.pointPosition( self.name+'.vtx[0]' )
        v1 = om.MVector( p1[0],p1[1],p1[2] )
        v1.normalize()
        p2 = cmds.pointPosition( self.name+'.vtx[1]' )
        tmpv = om.MVector( p2[0],p2[1],p2[2] )
        tmpv.normalize()
        self.basis.append( v1 )
        v2 = v1^tmpv
        v2.normalize()
        self.basis.append( v2 )
        v3 = v1^v2
        v3.normalize()
        self.basis.append( v3 )
        self.matrix = self.createMatrix( v1, v2, v3 )
    def createMatrix( self, v1, v2, v3 ) :
        out = om.MMatrix()
        vlist = (v1[0],v1[1],v1[2],0.0,v2[0],v2[1],v2[2],0.0,v3[0],v3[1],v3[2],0.0,0.0,0.0,0.0,1.0 )
        om.MScriptUtil.createMatrixFromList( vlist, out )
        return out
    def visualizeBasis( self ) :
        for b in self.basis :
            cmds.curve( d=1, p=[(0,0,0),(b[0],b[1],b[2])] )
    def cross( self, v1, v2 ) :
        return  mel.eval( 'cross <<%f,%f,%f>> <<%f,%f,%f>>' % (v1[0],v1[1],v1[2],v2[0],v2[1],v2[2]) )

def transformByMatrix( m ) :
    sellist = om.MSelectionList()
    om.MGlobal.getActiveSelectionList( sellist )
    dagpath = om.MDagPath()
    sellist.getDagPath(0,dagpath)
    transform = om.MFnTransform( dagpath )
    transform.set( om.MTransformationMatrix(m) )   

def visualizeBB() :
    selected = cmds.ls( sl=True )[0]
    bb = cmds.xform( q=True, bb=True )
    for x in range( 2 ) :
        xv = x*(x+3)
        for y in range( 2 ) :
            yv = y*(y+3)
            for z in range( 2 ) :
                zv = z*(z+3)
                cmds.spaceLocator( p=(bb[xv],bb[yv],bb[zv]) )

def getDifBB( obj ) :
    bb = cmds.xform( obj, q=True, bb=True )
    return (bb[3]-bb[0], bb[4]-bb[1], bb[5]-bb[2])

def getScaleValue( src, dst ) :
    sbb = getDifBB( src )
    dbb = getDifBB( dst )
    return (dbb[0]/sbb[0],dbb[1]/sbb[1],dbb[2]/sbb[2])

def match( source, destination, instObj ) :
    d2 = cmds.duplicate( destination )[0]
    s2 = cmds.instance( instObj )[0]
    cmds.xform( s2, cp=True )
    cmds.xform( d2, cp=True )
    # move to origin
    dpiv = cmds.xform( d2, q=True, ws=True, piv=True )
    cmds.xform( d2, r=True, ws=True, translation=(-dpiv[0],-dpiv[1],-dpiv[2]) ) 
    cmds.makeIdentity( d2, apply=True, t=True, r=True, s=True, n=False )
    #cmds.xform( target, cp=True )
    src = MatchObj( s2 )
    dst = MatchObj( d2)
    src.createBasis()
    dst.createBasis()
    # create instance of src, move to origin
    cmds.select( s2 )
    transformByMatrix( src.matrix.inverse() )
    #cmds.xform( target, cp=True )
    tmpg = cmds.group()
    # match rotation
    cmds.select( tmpg )
    transformByMatrix( dst.matrix )
    # clean up
    cmds.xform( s2, r=True, ws=True, translation=(dpiv[0],dpiv[1],dpiv[2]) ) 
    #cmds.xform( s2, r=True, ws=True, translation=(spiv[0],spiv[1],spiv[2]) )
    cmds.parent( s2, w=True )
    cmds.delete( d2 )
    cmds.delete( tmpg )
    return s2

def matchObjs() :
    selected = cmds.ls( sl=True )
    src = selected[0]
    dst = selected
    src2 = cmds.duplicate( src )[0]
    #src2 = cmds.instance(src)[0]
    cmds.xform( src2, cp=True )
    spiv = cmds.xform( src2, q=True, ws=True, piv=True )
    cmds.xform( src2, r=True, ws=True, translation=(-spiv[0],-spiv[1],-spiv[2]) )
    cmds.makeIdentity( src2, apply=True, t=True, r=True, s=True, n=False )
    newobj = []
    for d in dst :
        newobj.append( match( src2, d, src2 ) )
    cmds.delete( src2 )
    cmds.select( newobj )

def matchAll() :
    selected = cmds.ls( sl=True )
    src = selected[0]
    dst = selected
    src2 = cmds.duplicate( src )[0]
    #src2 = cmds.instance(src)[0]
    cmds.xform( src2, cp=True )
    spiv = cmds.xform( src2, q=True, ws=True, piv=True )
    cmds.xform( src2, r=True, ws=True, translation=(-spiv[0],-spiv[1],-spiv[2]) )
    cmds.makeIdentity( src2, apply=True, t=True, r=True, s=True, n=False )
    newobj = []
    matched = []
    for d in dst :
        dshape = cmds.listRelatives(d, s=True, f=True)[0]
        nobj = match( src2, d, src2)
        nshape = cmds.listRelatives(nobj, s=True, f=True)[0]
        npos = cmds.pointPosition(nshape+'.vtx[0]', w=True)
        dpos = cmds.pointPosition(dshape+'.vtx[0]', w=True)
        t = 0.01
        if d == dst[0] or (dpos[0]-t<npos[0]<dpos[0]+t and dpos[1]-t<npos[1]<dpos[1]+t and dpos[2]-t<npos[2]<dpos[2]+t) :
            newobj.append( nobj )
            matched.append(d)             
        else :
            cmds.delete(nobj)
    cmds.delete( src2 )
    if len(newobj) > 0 :
        cmds.select( newobj )
    if len(newobj) == 1 :
        gname = 'uninstance'
        if not cmds.objExists(gname) :
            cmds.group(em=True, n=gname)
        cmds.parent(newobj, gname)
    return matched

def matchRecursive() :
    selected = cmds.ls(sl=True)
    while len(selected) > 1 :
        cmds.select(selected, r=True)
        matched = matchAll()
        print(matched)
        print(selected)
        for m in matched :
            print(m)
            selected.pop(selected.index(m))
	print('[matchRecursive] Done. %s' % str(selected))
 
#matchObjs()
