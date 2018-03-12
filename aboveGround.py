from maya import cmds
import pymel.core as pc

def run() :
    selected = pc.selected()
    for s in selected :
        #print( s.name() )
        bb = pc.xform( s, q=True, bb=True, ws=True )
        pc.xform( s, r=True, translation=(0,-bb[1],0), ws=True )