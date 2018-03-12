import os, re
import shutil

def minValue() :
	files = os.listdir(os.getcwd())
	targets = []
	ext = 'tif'
	for f in files :
		if re.match('.*\.\d\d\d\d\.%s'%ext, f) :
			print(f)
			targets.append(f)
	files = targets
	files.sort()
	for i in range(len(files)) :
		print('#'*10)
		shutil.copyfile(files[0], 'min.%04d.%s' % (i, ext))	
		if i > 0 :
			cmd = 'convert min.%04d.%s %s -compose Darken -composite min.%04d.%s' % (i-1, ext, files[i], i, ext)
			print(cmd)
			os.system(cmd)

def maxValue() :
	files = os.listdir(os.getcwd())
	targets = []
	for f in files :
		if re.match('.*\.\d\d\d\d\.tif', f) :
			print(f)
			targets.append(f)
	files = targets
	files.sort()
	for i in range(len(files)) :
		print('#'*10)
		shutil.copyfile(files[0], 'max.%04d.jpg' %i)	
		if i > 0 :
			cmd = 'convert max.%04d.jpg %s -compose Lighten -composite max.%04d.jpg' % (i-1, files[i], i )
			print(cmd)
			os.system(cmd)

def exr2jpg() :
	import ImageLibrary as il
	files = os.listdir(os.getcwd())
	for f in files :
		if not os.path.splitext(f)[-1] == '.exr' :
			continue
		outfile = os.path.splitext(f)[0]+'.jpg'
		if os.path.isfile(outfile) :
			continue
		print('%s -> %s' % (f, outfile))
		il.formatExr(f, outfile)