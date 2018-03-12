from maya import cmds
import os

# supported types
types = {}
types['file'] = ['fileTextureName']
types['mzTextureLayout'] = []
for i in range(10) :
  types['mzTextureLayout'].append( 'imageName%d' % i )

lods = ['hi', 'md', 'lo', 'an']
bad = ['.', '-']

# functions
def validFileName( path, mute=False ) :
  blocks = path.split('_')
  for b in bad :
    if b in path :
      if not mute :
        print( 'Error: invalid character is included.' )
        return False
  if len(blocks) < 3 :
    if not mute :
      print( 'Error: At least 3 blocks needed. ex: baseName_txDifCol_md or baseName_txDifCol_TA_md.tx' )
    return False
  if not blocks[1].startswith( 'tx' ) :
    if not mute :
      print( 'Error: 2nd block has to starts with "tx". ex: txDifCol' )
    return False
  if len(blocks[2]) == 2 and blocks[2].isupper() :
    if not mute :
      print( "Info: Artist's initials are included." )
    # initial is included
    if len(blocks) < 4 :
      if not mute :
        print( 'Error: At least 4 blocks needed with initials. ex: baseName_txDifCol_TA_md.tx' )
      return False
    if blocks[3] not in lods :
      if not mute :
        print( 'Error: LOD name has to be one of followings: %s.' % str(lods) )
      return False
  else :
    if not mute :
      print( "Info: Artist's initials are not included." )
    if blocks[2] not in lods :
      if not mute :
        print( 'Error: LOD name has to be one of followings: %s.' % str(lods) )
      return False
  return True

# doRename

def doRename( node, attr, before, after ) :
  newpath = attr[1].replace( before, after )
  if os.path.isfile( newpath ) :
    print( 'Info: texture already exists.' )
  else :
    os.rename( attr[1], attr[1].replace( before, after ) )
    if os.path.isfile( newpath ) :
      print( 'Info: renamed file: %s.' % newpath )
    else :
      print( 'Error: something is wrong.' )
  cmds.setAttr( '%s.%s' % (node,attr[0]), newpath, type="string")
  cmds.rename( node, after.split('.')[0] )

# finalCheck
def run():
  targets = {}
  for t in types.keys() :
    targets[t] = cmds.ls( type=t )

  invalid = {}
  for t in targets.keys() :
    for node in targets[t] :
      for attr in types[t] :
          path = cmds.getAttr( '%s.%s' % (node,attr) )
      if path == '' :
            continue
      if not validFileName( os.path.splitext( os.path.split(path)[-1] )[0], mute=True ) :
        if not invalid.has_key( node ) :
          invalid[node] = []
        invalid[node].append( (attr,path) )

  # print invalid
  end = False
  for node in invalid.keys() :
    print( '[%s]:' % node )
    cmds.select( node )
    for attr in invalid[node] :
      valid = False
      while( not valid ) :
        print( attr )
        name = os.path.split( attr[1] )[-1]
        result = cmds.promptDialog( title='Rename', text=name, message='Original Name:%s' % name,button=['OK', 'Cancel'], defaultButton='OK', cancelButton='Cancel', dismissString='Cancel' )
        if result == 'OK' :
          text = cmds.promptDialog( q=True, text=True )
          valid = validFileName( os.path.splitext(text)[0] )
          if valid :
            doRename( node, attr, name, text )
        elif result == 'Cancel' :
          end = True
          break
      if end :
        break
    if end :
      break

  missing = {}
  for t in targets.keys() :
    for node in targets[t] :
      for attr in types[t] :
        path = cmds.getAttr( '%s.%s' % (node,attr) )
        if path == '' :
          continue
        if not os.path.isfile( path ) :
          if not missing.has_key(node) :
            missing[node] = []
          missing.append( node )

  if len( missing.keys() ) == 0 :
    print( 'All well now.' )
  else :
    print( '%d paths are missing.' % len( missing.keys() ) )
    for m in missing.keys() :
      print( m )
