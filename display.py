from maya import cmds

def wireframe():
    panel = cmds.getPanel(withFocus=True)
    cmds.modelEditor(panel,e=True,wos=(not cmds.modelEditor(panel,q=True,wos=True)))

def xray():
    panel = cmds.getPanel(withFocus=True)
    cmds.modelEditor(panel,e=True,xray=(not cmds.modelEditor(panel,q=True,xray=True)))

def grid():
    panel =cmds.getPanel(withFocus=True)
    cmds.modelEditor(panel,e=True,grid=(not cmds.modelEditor(panel,q=True,grid=True)))