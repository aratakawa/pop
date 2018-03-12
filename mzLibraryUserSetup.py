def setup() :
	import os
	import mzLibraryBrowser as LB
	import mzLibraryBrowser.apps as LBApps
	import mzLibraryBrowser.publish as LBP
	apps = []
	print(LB.getProjectPath())
	# character art
	tokens = LBApps.getDefaultTokens()
	tokens['name'] = 'Character Art'
	tokens['path'] = os.path.join(LB.getProjectPath(), 'users/ArakawaT/CharacterArt').replace('\\','/')
	tokens['ext'] = ['.jpg', '.jpeg', '.bmp', '.psd', '.gif', '.mov']
	tokens['actions']['General'] = ['OpenDirectoryAction']
	tokens['imagedir'] = ''
	tokens['imageext'] = ['.jpg', '.jpeg', '.bmp', '.psd', '.gif', '.mov']
	apps.append(LBApps.LibraryApp(tokens))
	# environment art
	tokens = LBApps.getDefaultTokens()
	tokens['name'] = 'Environment Art'
	tokens['path'] = os.path.join(LB.getProjectPath(), 'users/ArakawaT/EnvironmentArt').replace('\\','/')
	tokens['ext'] = ['.jpg', '.jpeg', '.bmp', '.psd', '.gif', '.mov']
	tokens['actions']['General'] = ['OpenDirectoryAction']
	tokens['imagedir'] = ''
	tokens['imageext'] = ['.jpg', '.jpeg', '.bmp', '.psd', '.gif', '.mov']
	apps.append(LBApps.LibraryApp(tokens))
	# work
	tokens = LBApps.getDefaultTokens()
	tokens['name'] = 'Work'
	tokens['path'] = os.path.join(LB.getProjectPath(), 'users/ArakawaT/Work').replace('\\','/')
	tokens['ext'] = ['.jpg', '.jpeg', '.bmp', '.psd', '.gif', '.exr', '.mov']
	tokens['actions']['General'] = ['OpenDirectoryAction']
	tokens['imagedir'] = ''
	tokens['imageext'] = ['.jpg', '.jpeg', '.bmp', '.psd', '.gif', '.exr', '.mov']
	apps.append(LBApps.LibraryApp(tokens))
	return apps