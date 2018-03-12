from maya import cmds

def smoothMesh2Subdiv():
    mesh = cmds.ls( type='mesh' )
    for m in mesh :
        if cmds.getAttr( m+'.displaySmoothMesh' ) > 0 :
            if cmds.getAttr(m+'.useSmoothPreviewForRender') < 1 :
                level = cmds.getAttr(m+'.smoothLevel')
            else :
                level = cmds.getAttr(m+'.renderSmoothLevel')
            cmds.setAttr(m+'.aiSubdivType', 1)
            cmds.setAttr(m+'.aiSubdivIterations', level)
            cmds.setAttr(m+'.displaySmoothMesh',0)