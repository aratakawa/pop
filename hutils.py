import os, getpass, time, shutil

import harvester.lib.datatypes as hd
import harvester.lib.utils     as hu
import harvester.lib.functions as hf

import omoikane.client.functions as ocf

def getProject() :
	return os.environ['VE_ENV_PROJ']

def getUser() :
    return getpass.getuser()

def getFrameRange(seq, shot) :
	s = ocf.list_projects(getProject())[0].get_sequence(seq).get_shot(shot)
	return s.start_frame, s.end_frame

def getDefaultTokens() :
	htokens = {}
	htokens['startFrame'] = 1
	htokens['endFrame'] = 1
	htokens['byFrame'] = 1
	htokens['perTask'] = 1
	htokens['sys_pr'] = 10
	htokens['prj_pr'] = 10
	htokens['job_type'] = 'default'
	htokens['title'] = 'Command'
	htokens['outpath'] = '/tmp'
	htokens['tags'] = ['maya']
	return htokens

def envwrapCmd(root=None, proj=None, seq=None, shot=None, dep=None, arch=None, env_file=None, env_base=None):
    if not root:
        root = os.environ.get('VE_ENV_ROOT','z:/marza/proj')
    if not proj:
        proj = os.environ.get('VE_ENV_PROJ','onyx')
    if not seq:
        seq  = os.environ.get('VE_ENV_SEQ','PROJ')
    if not shot:
        shot = os.environ.get('VE_ENV_SHOT','ALL')
    if not dep:
        dep  = os.environ.get('VE_ENV_DEPT','ALL')
    env_parm = ''
    cur_env_bases = os.environ.get('VE_ENV_BASES','maya2013')
    cur_env_file = os.environ.get('VE_ENV_FILE','')
    if env_base:
        env_parm = ' -n '+env_base
        if cur_env_bases==env_base and cur_env_file!='':
            env_parm = ' -f '+cur_env_file
    else:
        if env_file:
            env_parm = ' -f '+env_file
        else:
            if cur_env_file:
                env_parm = ' -f '+cur_env_file
            else:
                env_parm = ' -n '+cur_env_bases
    if not arch:
        arch = os.environ.get('VE_ARCH','x64')
    cmdStr = 'z:/ve/team/rnd/mzLauncher/mzenvwrap -r %s -p %s -s %s -t %s -d %s %s -a %s -- ' % (root, proj, seq, shot, dep, env_parm, arch)
    return cmdStr

def createJob(htokens) :
	fset = hu.frameSet('%d-%d/%d:%d' % (htokens['startFrame'], htokens['endFrame'], htokens['byFrame'], htokens['perTask']))
	hjob = hd.Job(system_priority = htokens['sys_pr'],
			project_priority = htokens['prj_pr'] ,
			job_type = htokens['job_type'] ,
			title = htokens['title'],
			frame_range_str = hu.frameStr(fset),
			total_frame = len(fset['frameList']),
			render_layer='layer',
			max_process=0,
			timeout=120,
			output=htokens['outpath'],
			message=''
			)
	return hjob

def dispatchSingleCommand(htokens, command) :
	hjob = createJob(htokens)
	hfold = hd.Folder(threads = -2,
						title=htokens['title'],
						frame_range_str='1-1',
						total_frame=1,
						output=htokens['outpath'],
						tags=htokens['tags'],
						environ={}
						)
	htask = hd.Task(title=htokens['title'],
						command=command,
						#frame_range_str='%d-%d' % (htokens['startFrame'], htokens['endFrame']),
						frame_range_str='%d-%d' % (1, 1),
						total_frame=1,
						output=htokens['outpath'],
						dependencies=None
					)
	hfold.append(htask)
	hjob.append(hfold)
	proj = getProject()
	user = getUser()
	seq = 'PROJ'
	shot = 'ALL'
	result = hf.save([hjob], user, proj, seq, shot, host='harvester4', port='80')
	print('Harvester Job ID: '+str(result))
