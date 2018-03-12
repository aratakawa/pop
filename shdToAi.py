'''
Created on 03/02/2012

@summary: Converts maya shaders to arnold shaders
@author: chrisg
'''

import maya.cmds as cmds


mappingMia = [
            ['diffuse_weight', 'Kd'],
            ['diffuse', 'color'],
            ['diffuse_roughness', 'diffuseRoughness'],
            
            ['reflectivity', 'Ks'],
            ['refl_color', 'KsColor'],
            
            ['refl_gloss', 'specularRoughness'],
            
            ['transparency', 'Kt'],
            ['refr_color', 'KtColor'],
            
            ['refr_ior', 'IOR'],
            ['refr_gloss', 'refractionRoughness'],

            ['overall_bump', 'n'],
        ]
        
mappingMaya = [
            ['diffuse', 'Kd'],
            ['color', 'color'],
            
            ['reflectivity', 'Ks'],
            ['reflectedColor', 'KsColor'],
            
            ['transparency', 'KtColor'],
            
            ['refractiveIndex', 'IOR'],

            ['normalCamera', 'n'],
        ]
        
mappingSurface = [
            ['outColor', 'color'],
        ]
       
def convertUi():
    ret = cmds.confirmDialog( title='Convert shaders', message='Convert all shaders in scene, or selected shaders?', button=['All', 'Selected', 'Cancel'], defaultButton='All', cancelButton='Cancel' )
    if ret == 'All':
        convertAllShaders()
    elif ret == 'Selected':
        convertSelection()
        
      
        
def convertSelection():
    """
    Loops through the selection and attempts to create arnold shaders on whatever it finds
    """
    
    sel = cmds.ls(sl=True)
    if sel:
        for s in sel:
            ret = doMapping(s)
    else:
        print 'Select a mia material, chump'


def convertAllShaders():
    """
    Converts each (in-use) material in the scene
    """
    
    shaderColl = cmds.ls(type=['mia_material_x_passes', 'mia_material_x', 'mia_material',
                               'blinn', 'lambert', 'phong', 'phongE',
                               'surfaceShader'
                               ])
    if shaderColl:
        for x in shaderColl:
            # query the objects assigned to the shader
            # only convert things with members
            shdGroup = cmds.listConnections(x, type="shadingEngine")
            setMem = cmds.sets( shdGroup, query=True )
            if setMem:
                ret = doMapping(x)
    else:
        print 'cannot find any shaders in the scene'
        


def doMapping(inShd):
    """
    Figures out which attribute mapping to use, and does the thing.
    
    @param inShd: Shader name
    @type inShd: String
    """
    ret = None
    
    if 'mia_material' in cmds.objectType(inShd) :
        ret = shaderToAiStandard(inShd, 'aiStandard', mappingMia)
        
        # do some cleanup on the roughness params
        for chan in ['diffuseRoughness', 'specularRoughness', 'refractionRoughness']:
            conns = cmds.listConnections( ret + '.' + chan, d=False, s=True, plugs=True )
            if not conns:
                val = cmds.getAttr(ret + '.' + chan)
                setValue(ret + '.' + chan, (1 - val))
        
        
    elif cmds.objectType(inShd) in ['blinn', 'lambert', 'phong', 'phongE']:
        ret = shaderToAiStandard(inShd, 'aiStandard', mappingMaya)
        
    elif cmds.objectType(inShd) in ['surfaceShader']:
        ret = shaderToAiStandard(inShd, 'aiUtility', mappingSurface)
        cmds.setAttr(ret + '.shadeMode', 2)
        
    if ret:
        # assign objects to the new shader
        assignToNewShader(inShd, ret)



def assignToNewShader(oldShd, newShd):
    """
    Creates a shading group for the new shader, and assigns members of the old shader to it
    
    @param oldShd: Old shader to upgrade
    @type oldShd: String
    @param newShd: New shader
    @type newShd: String
    """
    
    retVal = False
    
    shdGroup = cmds.listConnections(oldShd, type="shadingEngine")
    print 'shdGroup:', shdGroup
    if shdGroup:
        
        setMem = cmds.sets( shdGroup[0], query=True )
        print 'setMem:', setMem
        
        # hook up the new shader
        newSet = cmds.sets(renderable=True,  noSurfaceShader=True, empty=True, name=newShd +"_SG")
#        cmds.defaultNavigation(connectToExisting=True, source=newShd, destination=newSet)
        cmds.connectAttr(newShd + '.outColor', newSet + '.surfaceShader')
        cmds.sets( setMem, edit=True, forceElement=newSet )
        retVal =True
        
    return retVal

    

def shaderToAiStandard(inShd, nodeType, mapping):
    """
    'Converts' a shader to arnold, using a mapping table.
    
    @param inShd: Shader to convert
    @type inShd: String
    @param nodeType: Arnold shader type to create
    @type nodeType: String
    @param mapping: List of attributes to map from old to new
    @type mapping: List
    """
    
    print 'Converting material:', inShd
    
    if ':' in inShd:
        aiName = inShd.rsplit(':')[-1] + '_ai'
    else:
        aiName = inShd + '_ai'
        
    aiNode = cmds.shadingNode(nodeType, name=aiName, asShader=True)
    for chan in mapping:
        fromAttr = chan[0]
        toAttr = chan[1]
        
        if cmds.objExists(inShd + '.' + fromAttr):
            print '\t', fromAttr, ' -> ', toAttr
            
            conns = cmds.listConnections( inShd + '.' + fromAttr, d=False, s=True, plugs=True )
            if conns:
                cmds.connectAttr(conns[0], aiNode + '.' + toAttr, force=True)
                
            else:
                # copy the values
                val = cmds.getAttr(inShd + '.' + fromAttr)
                setValue(aiNode + '.' + toAttr, val)
    
    print 'Done. New shader is ', aiNode
    
    return aiNode
        


def setValue(attr, value):
    """All singing, all dancing, simplified set attribute function.
    
    No "type=" bullshit.
    
    Ideas shamelessly pinched shamelessly from PyMel. Thanks, PyMel.

    @param attr: Attribute to set. Type will be queried dynamically
    @param value: Value to set to. Better be compatible with the attr type, or the whole thing will puke.
    """

    aType = None

    if cmds.objExists(attr):
        # temporarily unlock the attribute
        isLocked = cmds.getAttr(attr, lock=True)
        if isLocked:
            cmds.setAttr(attr, lock=False)

        # one last check to see if we can write to it
        if cmds.getAttr(attr, settable=True):
            attrType = cmds.getAttr(attr, type=True)
            
            if attrType in ['string']:
                aType = 'string'
                cmds.setAttr(attr, value, type=aType)
                
            elif attrType in ['long', 'short', 'float', 'byte', 'double', 'doubleAngle', 'doubleLinear', 'bool']:
                aType = None
                cmds.setAttr(attr, value)
                
            elif attrType in ['long2', 'short2', 'float2',  'double2', 'long3', 'short3', 'float3',  'double3']:

                cmds.setAttr(attr, *value[0], type=attrType)

                
            else:
                print 'cannot yet handle that data type!!'


        if isLocked:
            # restore the lock on the attr
            cmds.setAttr(attr, lock=True)
        
        