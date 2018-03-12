from maya import cmds
from maya import mel

frames = 50

data = {}

import pymel.core as pm

pm.select(hi=True)
part = pm.selected(type='particle')[0]
print(part.name())
print(dir(part))
ids = part.particleIds()
print(ids)

for f in range(frames) :
	cmds.currentTime(f+1)
	print('frame: %d' % f)
	for i in ids :
		#print('id: %d' % i)
		if not data.has_key(i) :
			data[i] = []
		pos = cmds.particle(part.name(), q=True, attribute='position', id=i)
		#print(pos)
		data[i].append(pos)

for i in ids :
	if len(data[i]) > 0 :
		print(len(data[i]))
		cmds.curve(d=3, p=data[i])