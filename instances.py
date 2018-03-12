import pymel.core as pm
pm.select([x.getAllParents() for x in pm.selected()[0].getChildren()[0].getInstances()])