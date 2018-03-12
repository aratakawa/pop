import os

def txconvert() :
	files = os.listdir(os.getcwd())
	for f in files :
		if f.endswith('.tga') or f.endswith('.tif') :
			print('mzMaketx %s' % f)
			os.system('mzMaketx %s' % f)