import os, shutil

def copy() :
	path = '/marza/proj/kibble/work/Lookdev/FunLandMob01/lookdev/ArakawaT/mocap/data'
	data = {}
	files = os.listdir(os.getcwd())
	for f in files :
		if 'ass' in f.split('.')[-1] :
			name = f.split('.')[0]
			if not data.has_key(name) :
				data[name] = []
				#print(name)
				pass
			data[name].append(f)

	for name in data :
		d = os.path.join(path, name)
		if not os.path.isdir(d) :
			os.makedirs(d)
		for f in data[name] :
			shutil.move(f, os.path.join(d, f).replace('\\', '/'))
			print(f)

if(point(opinputpath(".",0), $PT, "vorticity", 0) > 0, point(opinputpath(".",0), $PT, "vorticity", 0)), 0.1)