import maya.OpenMaya as om
import maya.cmds as cmds

def isX(obj) :
    sellist = om.MSelectionList()
    sellist.add(obj)
    mobj = om.MObject()
    sellist.getDependNode(0, mobj)
    dagpath = om.MDagPath()
    sellist.getDagPath(0, dagpath)
    print(dagpath.fullPathName())
    meshfn = om.MFnMesh(mobj)
    points = om.MPointArray()
    meshfn.getPoints(points)
    sellist.clear()
    viter = om.MItMeshVertex(mobj)
    while not viter.isDone() :
        point = viter.position()
        if point.x > 0 :
            sellist.add(dagpath, viter.currentItem())
        viter.next()
    om.MGlobal.setActiveSelectionList(sellist)

def isZ(obj) :
    sellist = om.MSelectionList()
    sellist.add(obj)
    mobj = om.MObject()
    dagpath = om.MDagPath()
    sellist.getDependNode(0, mobj)
    sellist.getDagPath(0, dagpath)
    sellist.clear()
    fiter = om.MItMeshPolygon(dagpath)
    while not fiter.isDone() :
        points = om.MPointArray()
        fiter.getPoints(points, om.MSpace.kWorld)
        for i in range(points.length()) :
            if points[i].z > 0 :
                sellist.add(dagpath, fiter.currentItem())
                break
        fiter.next()
    om.MGlobal.setActiveSelectionList(sellist)

def izY(obj) :
    sellist = om.MSelectionList()
    sellist.add(obj)
    mobj = om.MObject()
    dagpath = om.MDagPath()
    sellist.getDependNode(0, mobj)
    sellist.getDagPath(0, dagpath)
    piter = MItInstancer(dagpath)
    while not piter.isDone() :
        piter.next()

def extractFaces(obj, p) :
    nobj = cmds.duplicate(obj)[0]
    shape = cmds.listRelatives(nobj, s=True)[0]
    sellist = om.MSelectionList()
    sellist.add(shape)
    dagpath = om.MDagPath()
    sellist.getDagPath(0, dagpath)
    fiter = om.MItMeshPolygon(dagpath)
    meshfn = om.MFnMesh(dagpath)
    remove = []
    print(p)
    while not fiter.isDone() :
        if fiter.index() not in p :
            remove.append(fiter.index())
        fiter.next()
    remove.sort()
    remove.reverse()
    for i in remove :
        meshfn.deleteFace(i)
    return nobj

def extractFaces2(obj, p) :
    sellist = om.MSelectionList()
    sellist.add(obj)
    dagpath = om.MDagPath()
    sellist.getDagPath(0, dagpath)
    meshfn = om.MFnMesh(dagpath)
    su = om.MScriptUtil(0)
    iarray = om.MIntArray()
    for index in p :
        iarray.append(index)
    print(p)
    fv = om.MFloatVector()
    meshfn.extractFaces(iarray, fv)

def getArea(fiter)    :
    su = om.MScriptUtil(0)
    area = su.asDoublePtr()
    fiter.getArea(area, om.MSpace.kWorld)
    aval = su.getDouble(area)
    return aval

def getConnectedFaces(fiter, p) :
    bki = fiter.index()
    faces = []
    for i in p :
        iarray = om.MIntArray()
        su = om.MScriptUtil(bki)
        pi = su.asIntPtr()
        fiter.setIndex(i, pi)
        fiter.getConnectedFaces(iarray)
        faces.extend(iarray)
    fiter.setIndex(bki, pi)
    return list(set(faces))

def area(obj, threshold=100000) :
    sellist = om.MSelectionList()
    sellist.add(obj)
    dagpath = om.MDagPath()
    sellist.getDagPath(0, dagpath)
    fiter = om.MItMeshPolygon(dagpath)
    meshfn = om.MFnMesh(dagpath)
    patches = []
    faces = []
    nfaces = meshfn.numPolygons()
    print('numPolygons: %d' % nfaces)
    totalarea = 0
    while not fiter.isDone() :
        index = fiter.index()
        if index in faces :
            fiter.next()
            continue
        patch = [index]
        totalarea = getArea(fiter)
        iii = 0
        while not totalarea > threshold :
            if iii > 1000 :
                break
            iii += 1
            cfaces = getConnectedFaces(fiter, patch)
            for f in cfaces:
                if f in faces :
                    continue
                faces.append(f)
                patch.append(f)
                su = om.MScriptUtil()
                pi = su.asIntPtr()
                fiter.setIndex(f, pi)
                totalarea += getArea(fiter)
                fiter.setIndex(index, pi)
                if len(faces) == nfaces :
                    break
        patch.sort()
        patch.reverse()
        patch = list(set(patch))
        patches.append(patch)
        print(patch)
        print(len(faces), nfaces)
        fiter.next()

    if totalarea > 0 :
        patches.append(patch)
    print('%d patches' % len(patches))
    
    out = []
    nobj = cmds.duplicate(obj)[0]
    out.append(nobj)
    shape = cmds.listRelatives(nobj, s=True)[0]
    for p in patches :
        extractFaces2(shape, p)
    if len(out) > 0 :
        cmds.select(out)
            