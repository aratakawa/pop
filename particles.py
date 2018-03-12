from maya import cmds
import math
import pymel.core as pm
	import pymel.core.datatypes as pdt

def freezeParticles() :
	part = pm.selected()[0].getShape(type='particle')
	pts = [p.position for p in part.points]
	newpart = pm.particle(p=pts)
	print('[freezeParticles]:%s' % created.newpart)

def particleToDensity() :
	part = pm.selected()[0].getShape(type='particle')
	fluid = pm.selected()[1]
	pts = [p.position for p in part.points]
	print('Executing %d points.' % len(pts))
	density = 1.0
	radius = 0.1
	for p in pts :
	    voxels = pm.fluidVoxelInfo(fluid, voxel=p, radius=radius)
	    for i in range(len(voxels)/3) :
	        vx = voxels[i*3]
	        vy = voxels[i*3+1]
	        vz = voxels[i*3+2]
	        vc = pm.fluidVoxelInfo(fluid, voxelCenter=True, xi=vx, yi=vy, zi=vz)
	        dist = pdt.Vector(p[0]-vc[0], p[1]-vc[1], p[2]-vc[2]).length()
	        w = 1.0-dist/radius
	        curdensity = pm.getFluidAttr(fluid, at='density', xi=vx, yi=vy, zi=vz)[0]
	        pm.setFluidAttr(fluid, at='density', floatValue=(w*density+curdensity), xi=vx, yi=vy, zi=vz)

def distance(a, b) :
    return math.sqrt(math.pow(a[0]-b[0],2)+math.pow(a[1]-b[1],2)+math.pow(a[2]*b[2],2))
			
def smoothstep(min, max, val) :
	t = 0.0
	if val < min :
		t = 0.0
	elif val > max :
		t = 1.0
	else :
		t = (val-min) / (max-min)
		t = t*t * (3.0-2.0*t);
	return t
			
def emitFromSphere() :
	import maya.cmds as cmds
	selected = cmds.ls(sl=True)
	objs = selected[:-1]
	fluid = selected[-1]
	input = 3.0

	for o in objs :
		t = cmds.getAttr(o+'.translate')[0]
		radius = cmds.getAttr(o+'.scaleX')
		voxels = cmds.fluidVoxelInfo(fluid, voxel=[t[0],t[1],t[2]], radius=radius)
		if not voxels :
			continue
		for i in range(len(voxels)/3) :
			v = [voxels[i*3], voxels[i*3+1], voxels[i*3+2]]
			density = cmds.getFluidAttr(fluid, attribute='density', xi=v[0], yi=v[1], zi=v[2])[0]
			vc = cmds.fluidVoxelInfo(fluid, voxelCenter=True, xi=v[0], yi=v[1], zi=v[2])
			density = density+input*(1-smoothstep(0.0, radius, distance(t,vc)))
			#print(density)
			cmds.setFluidAttr(fluid, attribute='density', floatValue=density, xi=v[0], yi=v[1], zi=v[2])
			print(cmds.getFluidAttr(fluid, attribute='density', xi=v[0], yi=v[1], zi=v[2])[0])
			pass
