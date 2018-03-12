from maya import cmds
from maya import mel

name = 'popSetAttrs'
stringCheckBox = name+'CheckBox'
attrField = name+'AttrTextFieldGrp'
valueField = name+'ValueTextFieldFrp'

def doSetAttrs( args ) :
    cmd = 'setAttr "%s.%s" %g %s'
    string = cmds.checkBox( stringCheckBox, q=True, v=True )
    strtype = ''
    if string :
        strtype = '-type "string"'
    attr = cmds.textFieldGrp( attrField, q=True, text=True )
    value = cmds.textFieldGrp( valueField, q=True, text=True )
    val = eval( value )
    for s in cmds.ls( sl=True ) :
        if not cmds.attributeQuery(attr, n=s, ex=True) :
            continue
        mel.eval( cmd % (s,attr, val, strtype) )

def run() :
    selected = cmds.ls( sl=True )
    if cmds.window( name, q=True, ex=True ):
        cmds.deleteUI( name, window=True )
    cmds.window( name, title=name )
    cmds.columnLayout()
    cmds.checkBox( stringCheckBox, label='string', v=0)
    cmds.textFieldGrp( attrField, label='attribute' )
    cmds.textFieldGrp( valueField, label='value')
    cmds.button( label='setAttrs', c=doSetAttrs )
    cmds.showWindow( name )