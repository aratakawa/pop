from maya import cmds

omit = ['initialParticleSE', 'initialShadingGroup']

def validSurfaceShader( name, mute=True ) :
  blocks = name.split( '_' )
  if len(blocks) != 2 :
    if blocks[-1] == 'ss' :
      if not mute :
        print( 'Error: SurfaceShader should have a name like this: "baseName_ss".' )
      return ''.join(blocks[0:-1])+'_ss'
      return blocks[0]+'_ss'
  if blocks[-1] != "ss" :
    return ''.join(blocks)+'_ss'
  if not blocks[0][0].islower() :
    if not mute :
      print( 'Error: Name should starts with lower case' )
    blocks[0] = blocks[0][0].lower()+blocks[0][1:]
    return '_'.join( blocks )
  return ''

def doRename( sg, ss, ds ) :
  cmds.rename( sg, ss.replace('_ss','_sg') )
  if ds != '' :
    cmds.rename( sg, ss.replace('_ss', '_ds') )

def run():
  targets = {}
  engines = cmds.ls( type='shadingEngine' )
  for e in engines :
    if e in omit :
      continue
    ss = cmds.listConnections( e+'.surfaceShader' )
    if ss == None :
      ss = ""
    else :
      ss = ss[0]
    ds = cmds.listConnections( e+'.displacementShader' )
    if ds == None :
      ds = ""
    else:
      ds = ds[0]
    if ss != '' :
      targets[e] = (ss,ds)

  print( 'There are %d shadingEngines.' % len(targets.keys()) )

  end = False
  for t in targets.keys() :
    ss, ds = targets[t]
    #print( 'ss: %s' % ss )
    new = validSurfaceShader( ss, mute=False )
    if new != '' :
      print( e )
      print( '%s -> %s.' % (targets[t][0], new) )
      valid = False
      while( not valid ) :
        result = cmds.promptDialog( title='Rename', text=new, message='Original Name: %s\nSuggestion: %s' % (ss,new),button=['OK', 'Cancel'], defaultButton='OK', cancelButton='Cancel', dismissString='Cancel' )
        if result == 'OK' :
          text = cmds.promptDialog( q=True, text=True )
          valid = validSurfaceShader( text )
          if valid == '' :
            cmds.rename( ss, text )
            doRename( t, ss, ds )
            break
        elif result == 'Cancel' :
          end = True
          break
      if end :
        break