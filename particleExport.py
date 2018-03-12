import partio

selected = cmds.ls(sl=True)
cmds.select(hi=True)
particles = cmds.ls(sl=True, type='particle')

path = 'Z:/marza/proj/onyx/team/lookdev/bake/nodesOfTime'

for pobj in particles :
	pset = partio.create()
	pattr = pset.addAttribute("position", partio.VECTOR, 3)
	cattr = pset.addAttribute("color", partio.VECTOR, 3)
	nattr = pset.addAttribute("normal", partio.VECTOR, 3)
	pcount = cmds.getAttr(pobj+'.count')
	pset.addParticles(pcount)
	print('[Particle Export] Exporting %s (%d points)...' % (pobj, pcount))
	for i in range(pcount) :
		# get position
		pos = cmds.getParticleAttr(pobj+'.pt[%d]'%i, at='position')[0:3]
		# get color
		if cmds.attributeQuery('rgbPP', n=pobj, ex=True) :
			col = cmds.getParticleAttr(pobj+'.pt[%d]'%i, at='rgbPP')[0:3]
		elif cmds.attributeQuery('colorRed', n=pobj, ex=True) :
			col = (cmds.getAttr(pobj+'.colorRed'), cmds.getAttr(pobj+'.colorGreen'), cmds.getAttr(pobj+'.colorBlue'))
		else :
			col = (1,0,0)
		# normal
		nml = (0,0,0)
		# set attributes
		pset.set(pattr, i, pos)
		pset.set(cattr, i, col)
		pset.set(nattr, i, nml)
	partio.write(str('%s/%s.bgeo' % (path, pobj)), pset, True)
	print('[Particle Export] Written to %s/%s.bgeo' %(path, pobj))
print('-'*50)
print('[Particle Export] Done %d objects.' % len(particles))
cmds.select(selected)