from maya import cmds
import instantiate as inst

def doRename( obj, name, type ) :
  counter = 0
  found = False
  while(not found):
    newname = name % (counter,type)
    match = cmds.ls(newname)
    if len(match) < 1 :
      found = True
      print( obj )
      cmds.rename(obj,newname)
      print('%s -> %s' % (obj,newname))
    counter += 1

def run():
    selected = cmds.ls(sl=True)
    result = cmds.promptDialog(title='RenameGeo',message='Enter Name',button=['OK','Cancel'],defaultButton='OK',cancelButton='Cancel',dismissString='Cancel')
    if result == 'OK':
        text = cmds.promptDialog(q=True,text=True)
        if '%d' not in text :
            cmds.rename(selected[0],text)
        else:
            for s in selected :
                """
                counter = 0
                found = False
                while(not found):
                    newname = text % counter
                    match = cmds.ls(newname)
                    if len(match) < 1 :
                        found = True
                        cmds.rename(s,newname)
                        print('%s -> %s' % (s,newname))
                    counter += 1
                """
                doRename(s, text, 'geo')

def storeGeo(g,geo) :
    if inst.isDirectParent(g) :
        if g not in geo :
            geo.append(g)
            return True
    return False

def storeGroup(g,group) :
    depth = len(g.split('|'))
    if not group.has_key( depth ) :
        group[depth] = []
    if not g in group[depth]:
        group[depth].append(g)

# rename hierarchy
def hrun():
    selected = cmds.ls(sl=True)
    result = cmds.promptDialog(title='RenameGeo',message='Enter Name',button=['OK','Cancel'],defaultButton='OK',cancelButton='Cancel',dismissString='Cancel')
    if result == 'OK':
        name = cmds.promptDialog(q=True,text=True)
        geo = []
        group = {}

        selected = cmds.ls( sl=True, long=True )
        for s in selected :
            if not storeGeo(s,geo) :
                storeGroup(s,group)
                cmds.select( cmds.listRelatives( children=True, fullPath=True, type='transform' ), hi=True )
                objs = cmds.ls( sl=True, type='transform', long=True )
                for o in objs :
                    if not storeGeo(o,geo) :
                        storeGroup(o,group)

        print(geo)
        for g in geo :
            try:
                doRename( g, name, 'geo' )
            except:
                print( '%s skipped.' % g)

        keys = group.keys()
        keys.sort(reverse=True)

        for k in keys :
            try:
                for g in group[k] :
                    doRename( g, name, 'geoGp' )
            except:
                print( '%s skipped.' % g)