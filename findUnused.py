from maya import cmds
import os
import shutil

#ext = ['.tx','.tga','.tif']
ext = ['.tx']
subext = ['.tx','.tga','.tif']

def run() :
    result = cmds.promptDialog(title='findUnused',message='Enter Path',button=['OK','Cancel'],defaultButton='OK',cancelButton='Cancel',dismissString='Cancel')
    if result == 'OK':
        text = cmds.promptDialog(q=True,text=True)
        if not os.path.isdir(text) :
            print('invalid path.')
            return
        files = os.listdir(text)
        fnodes = cmds.ls(type='file')
        used = []
        for f in fnodes :
            name = os.path.split(cmds.getAttr(f+'.fileTextureName'))[-1]
            if name not in used :
                used.append(name)
        print(files)
        unused = []
        for f in files :
            if os.path.splitext(f)[-1] in ext :
                if f not in used and f not in unused :
                    unused.append(f)

        for u in unused :
            print( u )

        result = cmds.confirmDialog( title='findUnused', message='There are %d unused files.\nMove unused files to "unsused" directory?'%len(unused), button=['Yes','No'], defaultButton='Yes', cancelButton='No', dismissString='No' )
        if result == 'Yes' :
            if not os.path.isdir(os.path.join(text,'unused')) :
                os.makedirs(os.path.join(text,'unused'))
            for u in unused :
                for e in subext :
                    file = os.path.splitext(u)[0]+e
                    if os.path.isfile(os.path.join(text,file)) :
                        shutil.move(os.path.join(text,file),os.path.join(text,'unused',file))