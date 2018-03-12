from maya import cmds

def run() :
    cmds.select(hi=True)
    mesh = cmds.ls(sl=True,type='mesh')
    print('meshCount: %d' % len(mesh))