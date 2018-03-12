# -*- coding:  utf-8 -*-
from maya import cmds
from maya import mel
import re, os

import eST
eSTVal = eST.startup.values

primitiveCameras = ["|persp","|top","|front","|side"]


def mzRenameTransformAsUnique(meshName):

    count = 0
    nodeList = []
    parentList = []
    basename = ""
    newname = ""
    flag = 1
    loopCount = 0
    for loop in range(10000):
        loopCount += 1
        if flag == 0:
            break
        flag = 0
        if meshName != "":
            nodeList = cmds.ls(tr=True)
            nodeList.sort()
        else:
            if not cmds.nodeType(meshName) == "transform":
                res = cmds.listRelatives(meshName, allParents=True, type="transform")
            nodeList = [meshName]

        for node in nodeList: 
            tmp = re.match(".*\|.*", node)
            if tmp:
                if node in primitiveCameras:
                    continue
                if cmds.referenceQuery(node, isNodeReferenced=True):
                    continue #ignore

                name = re.search("[^|]+$", node)
                name = name.group(0)
                tempList = cmds.ls(name, r=1, tr=True)

                if len(tempList) == 1:
                    continue #instance

                nums = re.search("[0-9]+$", name)
                if nums != None:
                    basename = re.sub("[0-9]+$", "", name)
                    num = int(nums.group(0))
                else:
                    basename = name
                    num = 0

                newname = node
                temp = re.match(".*\|.*", newname)

                while temp:
                    num += 1
                    tempname = basename + str(num)
                    newname = cmds.rename(newname, tempname, ignoreShape = True)
                    temp = re.match(".*\|.*", newname)

                print ("rename " + node + " " + newname + "\n")
                count += 1

                flag = 1
                break

    if loopCount >= 10000:
        raise "Please contact Engineers. it may be BUG!"

    return count


###
### uniquify all transform node name
### and rename shape nodes based on the transform node name.
###
def mzRenameAsUniqueWithShape(meshName = ""):
    count = mzRenameTransformAsUnique(meshName)

    if meshName == "":
        shapeList = cmds.ls(l=True, type="shape")
    else:
        shapeList = [meshName]

    for shape in shapeList:
        if cmds.objExists(shape):
            count += mzRenameShapeByTransform(shape)

    if not count or count == 0:
        print "OK. it seems not to need to rename."

    return count


###
### check not unique name
###
def mzCheckUniqueName():
    count = 0
    res = []
    lst = []
    resDict = {}
    cmds.select(cl=True)
    nodeList = cmds.ls()
#    print nodeList
    for node in nodeList:
        tmp = re.match(".*\|.*", node)
        if tmp:
            name = re.search("[^|]+$", node)
            name = name.group(0)
            tempList = cmds.ls(name, r=1)
            #print "tempList"
            #print tempList
            if len(tempList) == 1:
                continue #instance

            #i = len(tempList) - 1
            if name in lst:
                indx = lst.index(name)
            else:
                #print name + ":"
                #for a in tempList:
                #    print " " + a
                lst.append(name)
                res.append(node)
                resDict[name] = tempList
                count += 1
                if count > 200:
                    print "ERROR Too match error(not unique). abort."
                    return -1

        #cmds.select(node, add=True)

    if not count or count == 0:
        print "OK. all nodes seem to be unique."

#    print count
#    print "mzCheckUniqueName"
#    print res
    return resDict



def mzRenameShapeByTransform(shape):
    parentList = []

    if cmds.referenceQuery(shape, isNodeReferenced=True):
        return 0 # ignore

    parentList = cmds.listRelatives(shape, f=True, p=True)
    tr = re.search("[^|]*$", parentList[0])
    tr = tr.group(0)

    shname = re.search("[^|]*$", shape)
    if not shname:
        print "Error: wrong param " + shape
        return False
    shname = shname.group(0)

    tmp = re.match(tr + ".*", shname)

    if tr != shname and tmp:
        name = re.sub("^" + tr, "", shname)
        nummatch = re.match("^[0-9]", name)
        if not nummatch:
            return False

    basename = tr
    while re.match(".*[0-9].*", basename):
        basename = re.sub("[0-9]+", "", basename)

    shname = re.search("[^|]*$", shape)
    if shname:
        shname = shname.group(0)
        while re.match(".*[0-9].*", shname):
            shname = re.sub("[0-9]+", "", shname)

    count = 0
    sfxname = ""
    n = len(basename)
    if n > len(shname):
        n = len(shname)
    for i in range(n):
        count = i
        c = basename[i]
        if c != shname[i]:
            sfxname = shname[i:len(shname)]
            break

    if count >= n:
        sfxname = shname[count:len(shname)]
    if re.match(".*Shape.*", sfxname):
        sfxname = re.search("Shape.*$", sfxname)
        sfxname = sfxname.group(0)
    if sfxname == "":
        sfxname = "Shape"

    newname = tr + sfxname
    temp = re.search("[^|]*$", shape)
    if temp:
        temp = temp.group(0)
        if temp != newname:
            shname = cmds.rename(shape, newname)
            shname = re.search("[0-9]+$", shname)
    if shname:
        shname = shname.group(0)
        while shname != "":
            newname += "X"
            shname = cmds.rename(shname, newname)

        print "rename " + shape + " " + newname + "\n"

    return True



#    case"checkNumNode_dag":
#        $nodes = onyxRenameTool("check_eSTNodeOpt", {"numberedNodeName_dag"});
#        select -r $nodes;
#        break;
#    case"check_eSTNodeOpt":
#        string $nodeOptType = $args[0];
#        $nodes = _eSTnodeOpt("select", $nodeOptType);
#        select -r $nodes;
#        break;



def mzCheckFuncName(root, funcNames):

    childs = cmds.listRelatives(root, f=True, ad=True)

    collectNodes = []
    results = []
    for child in childs:
        div = child.split("|")
        node = div[-1]
        child_funcName = eSTVal.nodeName_decode(node)[1]
        for i in range(len(funcNames)):
            if re.match(".*%s.*"%child_funcName, funcNames[i]):
                collectNodes.append(child)
                break

    print collectNodes
    sorted(set(childs), key=childs.index)
    for child in childs:
        if child in collectNodes:
            pass
        else:
            results.append(child)

    return results



def mzCheck_eSTNodeOpt(mode, nodeOptType):

#    //////////////////////////////
#    //$mode... select , print
#    //$nodeOptType...unoptimizeDeformerNodeName, duplicatedNodeName, invalidNodeNameConvention_dag, invalidNodeNameConvention_nonDag, numberedNodeName_dag, numberedNodeName_nonDag
#    //////////////////////////////

    eST.loadLibrary( 'lib_elementModifier' )
    prefix = ':'
    fn = eST.elementModifier('optimize', 'builtinOptimize030_nodeName01', nodeOptType)
    eST.activateElementModifiers( [fn], True, prefix=prefix )
    items = fn.detect( echo=True, solution=0 )
    return items


def mzCheckNumNode_dag():
    nodes = mzCheck_eSTNodeOpt("select","numberedNodeName_dag")
    if nodes != []:
        cmds.select(nodes, r=True)
    return nodes


def mzCheckCHM_funcName():
    nodes = mzCheckFuncName("all", ["gp", "geo", "geoGp", "crv", "crvGp", "scalpGeo", "scalpGeoGp", "guideCrv", "guideCrvGp", "guideGeoGp", "geoShape", "crvShape", "scalpGeoShape", "guideCrvShape", "dummyGeo", "dummyGeoShape","cageGeo","cageGeoShape"])
    if nodes != []:
        cmds.select(nodes, r=True)
    return nodes



def mzCheckName(typ="checkCHPM_publishName", root=""):
    nodes = []
    a = c = d = []
    b = {}
    if typ == "checkCHM_publishName":
        #a = onyxRenameTool("checkNumNode_dag", {});
        a = mzCheckNumNode_dag()
        print("check number")
        print a
        # unique name check is inside mzModelCheckTool already
        """
        b = mzCheckUniqueName()
        print("check non-unique");
        print b
        """
        mel.eval("source \"Z:/marza/proj/onyx/tools/maya/onyxRenameTool/onyxRenameTool.mel\"")
        c = mel.eval('onyxRenameTool("check_eSTNodeOpt", {"invalidNodeNameConvention_dag"});')
        #c = mzCheck_eSTNodeOpt("select","invalidNodeNameConvention_dag")
        print("check non-capital & underBar");
        print c
        d = mel.eval('onyxRenameTool(\"checkCHM_funcName\", {});')
#        d = onyxRenameTool("checkCHM_funcName", {});
        #d = mzCheckCHM_funcName()
        print("check non-funcName");
        print d
            
        cmds.select(cl=True)
        if a != []:
            cmds.select(a, add=True)
        for bb in b.keys():
            if b[bb] != []:
                cmds.select(b[bb], add=True)
        if c != []:
            cmds.select(c, add=True)
        if d != []:
            cmds.select(d, add=True)
        nodes = cmds.ls(sl=True)

    elif typ == "checkCHPM_publishName":
        #string $a[] = onyxRenameTool("checkNumNode_dag", {});
        a = mzCheckNumNode_dag()
        print("check number")
        print a
        # unique name check is inside mzModelCheckTool already
        """
        b = mzCheckUniqueName()
        print("check non-unique")
        print b
        """

        cmds.select(cl=True)
        if a != []:
            cmds.select(a, add=True)
        for bb in b.keys():
            cmds.select(b[bb], add=True)
#        cmds.select( b, add=True)
        nodes = cmds.ls(sl=True)

    elif typ == "checkCHPM_publishName2":
        #string $a[] = onyxRenameTool("checkNumNode_dag", {});
        a = mzCheckNumNode_dag()
        print("check number")
        print a
        # unique name check is inside mzModelCheckTool already
        """
        b = mzCheckUniqueName()
        print("check non-unique")
        print b
        """
        mel.eval("source \"Z:/marza/proj/onyx/tools/maya/onyxRenameTool/onyxRenameTool.mel\"")
        c = mel.eval('onyxRenameTool("check_eSTNodeOpt", {"invalidNodeNameConvention_dag"});')
        #c = mzCheck_eSTNodeOpt("select","invalidNodeNameConvention_dag")
        print("check non-capital & underBar");
        print c
        if root != "":
            d = mel.eval('onyxRenameTool(\"checkCHM_funcName2\", {\"%s\"});'%root)
#        d = onyxRenameTool("checkCHM_funcName", {});
        #d = mzCheckCHM_funcName()
            print("check non-funcName");
            print d
        else:
            print "pass checking non-funcName. Root node name is not given."
            d = []

        cmds.select(cl=True)
        if a != []:
            cmds.select(a, add=True)
        for bb in b.keys():
            cmds.select(b[bb], add=True)
#        cmds.select( b, add=True)
        if c != []:
            cmds.select(c, add=True)
        if d != []:
            cmds.select(d, add=True)

        nodes = cmds.ls(sl=True)

    elif typ == "checkCHM_sotaiName":
        proj = os.environ["VE_ENV_PROJ"]
        mel.eval('source "Z:/marza/proj/%s/tools/maya/scripts/mzsuCheckSotaiName.mel";'%proj)
        nodes = mel.eval("mzsuCheckSotaiName()")

    elif typ == "checkCHM_funcName":
        nodes = mzCheckCHM_funcName()

    return nodes


