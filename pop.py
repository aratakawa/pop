from maya import cmds
from maya import mel
import maya.OpenMaya as om
import re
import os

name = 'pop'
menuBar = name+'menuBarLayout'
scrollField = name+'ScrollField'
scrollList = name+'TextScrollList'
classificationMenu = name+'ClassificationMenuItem'
classificationLimit = False
shaders = {'shader':'Shader', 'texture':'Texture', 'light':'Light', 'utility':'Utility', 'imagePlane':'Utility', 'postprocess':'PostProcess'}
mayafiles = ['maya_commands.txt']
customfiles = ['custom_commands.txt']

print(__file__)

data = {}
customcommand = {}
mayacommand = {}

def collectNodes() :
    global data
    nodes = cmds.ls( nodeTypes=True )
    classifications = []
    for n in nodes :
        for cl in cmds.getClassification(n)[0].split(':') :
            for s in shaders.keys() :
                if cl.startswith( s ) :
                    data[n] = cl
                    if cl not in classifications :
                        classifications.append(cl)
    for cl in classifications :
        #print( cl )
        pass

def createDataFromFile( command, files, label ) :
    global data
    thisfile = os.path.split(__file__)[-1]
    for f in files :
        path = __file__.replace(thisfile,f )
        if os.path.isfile( path ) :
            print( 'loading %s.' % f )
            lines = open( path ).readlines()
            for l in lines :
                if l.startswith( '#' ) :
                    continue
                l = l.rstrip()
                l = l.split(',')
                if len(l) < 2 :
                    continue
                data[l[0]] = label
                command[l[0]] = ','.join(l[1:])

def collectMayaCommands() :
    global data
    global mayacommand
    createDataFromFile( mayacommand, mayafiles, 'maya' )


def collectCustomCommands() :
    global data
    global customcommand
    createDataFromFile( customcommand, customfiles, 'custom' )

def createNodeCommand( node ) :
    cmds.createNode( node )

def createMayaCommand( cmd ) :
    global mayacommand
    exec( mayacommand[cmd] )

def createCustomCommand( cmd ) :
    global customcommand
    exec( customcommand[cmd] )

def createShaderCommand( node, label ) :
    flag = label.split('/')[0].capitalize()
    cmd = 'cmds.shadingNode("%s", as%s=True)' % (node, flag)
    exec(cmd)

def executeCommand( attr ) :
    item = cmds.textScrollList( scrollList, q=True, selectItem=True )[0].split(' ')
    try :
        print( item )
        if len( item ) == 1 :
            createNodeCommand( item[0] )
        else :
            label = item[-1].strip('[').strip(']')
            if 'custom' in label :
                createCustomCommand( item[0] )
            elif 'maya' in label :
                createMayaCommand( item[0] )
            else :
                createShaderCommand( item[0], label )
    except Exception, e:
        om.MGlobal.displayError(e)
    cmds.evalDeferred( run )

def tmpExecuteCommand() :
    executeCommand( 'dummy' )

def textChanged():
    global classificationLimit
    text = cmds.scrollField( scrollField, q=True, text=True )
    if( text != text.rstrip('\n') ) :
        executeCommand( 'dummy' )
        return
    match = []
    text = text.lower()
    if text != text.rstrip() :
        comp = re.compile( '%s\Z' % text.rstrip() )
    else :
        comp = re.compile( '.*%s.*' % text )
    for n in data.keys() :
        if data[n] == "" and classificationLimit :
            continue
        #if n.lower().find( text ) > -1 :
        if comp.match( n.lower() ) != None :
            item = n
            if data[n] != "" :
                item += ' [%s]' % data[n]
            match.append(item)
    cmds.textScrollList( scrollList, e=True, removeAll=True )
    if len( match ) > 0 :
        match.sort()
        cmds.textScrollList( scrollList, e=True, append=match, selectItem=match[0] )

def cmCB( arg ) :
    global classificationLimit
    classificationLimit = arg
    print( classificationLimit )

def run():
    global classificationLimit
    if cmds.window( name, q=True, ex=True ) :
        cmds.deleteUI( name, window=True )
    else :
        cmds.window( name, title=name, w=300, h=500 )
        cmds.menuBarLayout( menuBar )
        cmds.menu( label='Edit')
        cmds.menuItem( classificationMenu, label='Classification Limit', checkBox=classificationLimit, c=cmCB )
        cmds.columnLayout( )
        sf = cmds.scrollField( scrollField, editable=True, h=20, nl=1, kpc=lambda x: cmds.evalDeferred( textChanged ), ec=executeCommand)
        tsg = cmds.textScrollList( scrollList, numberOfRows=10, allowMultiSelection=False, sc=tmpExecuteCommand )
        cmds.showWindow( name )

collectNodes()
collectMayaCommands()
collectCustomCommands()