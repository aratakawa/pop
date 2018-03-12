from maya import cmds

def run():
    engines = cmds.ls( type='shadingEngine', long=True )
    for e in engines :
        cmds.select( e )
        assigned = cmds.ls( sl=True, long=True )
        if len(assigned) > 0 :
            objs = []
            for a in assigned :
                obj = a.split('.')[0]
                if obj not in objs :
                    objs.append( obj )
            ss = cmds.listConnections( e+'.surfaceShader' )[0]
            cmds.select( objs )
            cmds.pickWalk( direction='up' )
            cmds.hyperShade( assign=ss )

def select():
    engines = cmds.ls( type='shadingEngine', long=True )
    for e in engines :
        objs = []
        cmds.select( e )
        assigned = cmds.ls( sl=True, long=True )
        if len(assigned) > 0 :
            for a in assigned :
                if '.f[' in a :
                    print(a)
                    if a not in objs :
                        objs.append(a)
            if len(objs) > 0 :
                cmds.select(objs)
                break