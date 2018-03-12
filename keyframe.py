at='interaxialSeparation'
obj = 'stereoCameraCenterCamShape'
scale = 1.5
keys = cmds.keyframe(obj, q=True, at=at)
print(keys)
ct = cmds.currentTime(q=True)
for k in keys :
    cmds.currentTime(k)
    val = cmds.getAttr(obj+'.'+at)
    print(val, val*scale)
    cmds.keyframe(t=(k,k), a=True, vc=val*scale)
cmds.currentTime(ct)
pass