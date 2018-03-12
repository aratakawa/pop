from maya import cmds

import instantiate as inst
reload( inst )

selected = cmds.ls( sl=True )
src = 'A'
dst = 'D'
main = 'mainGun%sroll_geoGp_B' % src
rot = cmds.getAttr( main+'.rz') * -2.0

target = []
selected = cmds.ls( sl=True, long=True )
for s in selected :
  print( '%s' % s.replace('L','R') )
  dstloc = s.replace('mainGun'+src,'mainGun'+dst)
  children = cmds.listRelatives( s, fullPath=True, children=True, type='transform' )
  cmds.select( children )
  grp = cmds.group()
  children = cmds.listRelatives( grp, fullPath=True, children=True, type='transform' )
  grp = cmds.ls( sl=True, long=True )[0]
  cmds.select( grp )
  newroot = inst.mirrorInstance(s)
  tmpgrp = cmds.createNode( 'transform', n='tmpGp', p=main )
  cmds.select( newroot )
  cmds.parent( newroot, tmpgrp )
  newroot = cmds.ls( sl=True )[0]
  cmds.rotate( 0,0,rot, tmpgrp, r=True, os=True )
  cmds.parent( children, s )
  cmds.delete(grp)
  print( newroot )

  newchildren = cmds.listRelatives( newroot, fullPath=True, children=True, type='transform' )
  target.append( cmds.listRelatives( s.replace('L','R'), fullPath=True, children=True, type='transform' ) )
  cmds.parent( newchildren, dstloc )
  cmds.delete( tmpgrp )




"""
{
              string $sels[] = `ls -sl`;
              string $src = "A";
              string $dst = "D";
              string $main = ("mainGun"+$src+"roll_geoGp_C");
              float $rot = `getAttr ($main + ".rz") ` * -2;

              for($s in $sels){
                  string $dstLoc = `substitute ("mainGun"+$src) $s ("mainGun"+$dst)`;
                            string $tmpGp = "tmpGp";
                            string $listMdl[] = `listRelatives -f -c -type transform $s`;
                            string $dupMdl[] = `duplicate -rr -rc $listMdl`;
                            createNode transform -n $tmpGp -p $main;
                            parent $dupMdl $tmpGp;
                            rotate -r -os 0 0 $rot $tmpGp;
        parent $dupMdl $dstLoc;
        delete $tmpGp;
    }
}
"""
pass

from maya import cmds

import instantiate as inst
reload( inst )

target = []
selected = cmds.ls( sl=True, long=True )
for s in selected :
  print( '%s' % s.replace('L','R') )
  children = cmds.listRelatives( s, fullPath=True, children=True, type='transform' )
  cmds.select( children )
  grp = cmds.group()
  children = cmds.listRelatives( grp, fullPath=True, children=True, type='transform' )
  grp = cmds.ls( sl=True, long=True )[0]
  cmds.select( grp )
  newroot = inst.mirrorInstance()
  cmds.parent( children, s )
  cmds.delete(grp)
  print( newroot )

  newchildren = cmds.listRelatives( newroot, fullPath=True, children=True, type='transform' )
  target.append( cmds.listRelatives( s.replace('L','R'), fullPath=True, children=True, type='transform' ) )
  cmds.parent( newchildren, dstloc )
  cmds.delete( newroot )

for t in target :
  cmds.delete( t )
