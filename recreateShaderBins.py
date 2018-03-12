shaders = cmds.ls(materials=True)
for s in shaders :
    bins = cmds.binMembership(s, q=True, listBins=True)
    if len(bins) > 0 :
        for bin in bins :
            cmds.binMembership(s, addToBin=bin)
    print(s, bins)