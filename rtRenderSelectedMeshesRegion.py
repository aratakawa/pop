# -----------------------------------------------------------------------------------
# rtRenderSelectedMeshesRegion Version 1.0
# Author:  Ryan Trowbridge
# Contact: admin@rtrowbridge.com 
#
# Please give credit where credit is due this is written by Ryan Trowbridge
# with lots of experimentation to try to get python to work correctly.
#
# Description:
# This script was desgined to find the bounding box of the selected meshes then to render
# that bounding box as a region in the renderer. The script will check for the current render size
# then fix the render region aspect ratio to adjust to the size of the render.
#
# To use: 
# import this python script and select one or more mesh objects then execute the 
# rtRenderSelectedMeshesRegion() python command.
# The region around the selected meshes will be rendered
# -----------------------------------------------------------------------------------	

import maya.OpenMaya as OpenMaya
import maya.OpenMayaUI as OpenMayaUI
import maya.cmds as cmds
import maya.mel as mel
import sys

debug = False

# To test create a sphere then run this function
def rtRenderSelectedMeshesRegion():

	# get current render width and height settings
	renderWidth = cmds.getAttr('defaultResolution.width')
	renderHeight = cmds.getAttr('defaultResolution.height')

	# get the active viewport
	activeView = OpenMayaUI.M3dView.active3dView()
	
	# define python api pointers to get data from api class
	xPtrInit = OpenMaya.MScriptUtil()
	yPtrInit = OpenMaya.MScriptUtil()
	widthPtrInit = OpenMaya.MScriptUtil()
	heightPtrInit = OpenMaya.MScriptUtil()
	
	xPtr = xPtrInit.asUintPtr()
	yPtr = yPtrInit.asUintPtr()
	widthPtr = widthPtrInit.asUintPtr()
	heightPtr = heightPtrInit.asUintPtr()
	
	# retreive viewport width and height
	activeView.viewport(xPtr, yPtr, widthPtr, heightPtr)
	viewX = xPtrInit.getUint( xPtr )
	viewY = yPtrInit.getUint( yPtr )
	viewWidth = widthPtrInit.getUint( widthPtr )
	viewHeight = heightPtrInit.getUint( heightPtr )
	
	
	# determin aspect ratio of render size
	# then determin what the viewport renderable height is
	aspectRatio = float(renderHeight) / float(renderWidth)
	viewportRenderableMax = 0
	heightDiff = 0  # actual viewport renderable pixels
	heightClip = 0	# area of user viewport not renderable
	
	if(renderWidth > renderHeight):
		viewportRenderableMax = viewWidth * aspectRatio
		heightDiff = viewHeight - viewportRenderableMax
		heightClip = heightDiff / 2
	else:
		viewportRenderableMax = viewHeight * aspectRatio
		heightDiff = viewportRenderableMax - viewHeight
		heightClip = heightDiff / 2
	
	if(debug):
		sys.__stdout__.write( '############Start Render Selected Mesh(s) Region#############' + '\n')
		sys.__stdout__.write( 'viewLowerLeftX: ' + str(viewX) + '\n')
		sys.__stdout__.write( 'viewLowerLeftY: '+ str(viewY) + '\n')
		sys.__stdout__.write( 'viewWidth: ' + str(viewWidth) + '\n')
		sys.__stdout__.write( 'viewHeight: ' + str(viewHeight) + '\n')
		sys.__stdout__.write( 'aspectRatio: ' + str(aspectRatio) + '\n')
		sys.__stdout__.write( 'heightDiff: ' + str(heightDiff) + '\n')
		sys.__stdout__.write( 'heightClip: ' + str(heightClip) + '\n')
		sys.__stdout__.write( 'viewportRenderableMax: ' + str(viewportRenderableMax) + '\n')
	
	# get the active selection
	selection = OpenMaya.MSelectionList()
	OpenMaya.MGlobal.getActiveSelectionList( selection )
	iterSel = OpenMaya.MItSelectionList(selection, OpenMaya.MFn.kMesh)

	# bounding box vars
	minX = 0
	maxX = 0
	minY = 0
	maxY = 0

	iterGeoNum = 0
	
	# loop through the selected nodes
	while not iterSel.isDone():

		dagPath = OpenMaya.MDagPath()
		iterSel.getDagPath( dagPath )
		
		if(debug):
			name = dagPath.fullPathName()
			sys.__stdout__.write(name + '\n')

		
		iterGeo = OpenMaya.MItGeometry( dagPath )

		# iterate through vertex positions
		# check each vertex position and get its x, y cordinate in the viewport
		# generate the minimum x and y position and the max x and y position
		
		while not iterGeo.isDone():

			vertexMPoint = iterGeo.position(OpenMaya.MSpace.kWorld)
			xPosShortPtrInit = OpenMaya.MScriptUtil()
			yPosShortPtrInit = OpenMaya.MScriptUtil()
			xPosShortPtr = xPosShortPtrInit.asShortPtr()
			yPosShortPtr = yPosShortPtrInit.asShortPtr()

			activeView.worldToView(vertexMPoint, xPosShortPtr, yPosShortPtr)

			xPos = xPosShortPtrInit.getShort(xPosShortPtr)
			yPos = yPosShortPtrInit.getShort(yPosShortPtr)

			if iterGeoNum == 0:
				minX = xPos
				minY = yPos

			if xPos < minX: minX = xPos
			if xPos > maxX: maxX = xPos
			if yPos < minY: minY = yPos
			if yPos > maxY: maxY = yPos
			
			iterGeoNum = iterGeoNum + 1
			iterGeo.next()
		
		# move on to next selected node
		iterSel.next()
		
	# the renderWindowCheckAndRenderRegion arguments are ymax, xmin, ymin, xmax		
	# convert the min max values to scalars between 0 and 1
	minXScalar = 0
	maxXScalar = 0
	minYScalar = 0
	maxYScalar = 0

	if(renderWidth > renderHeight):
		minXScalar = float(minX)/float(viewWidth)
		maxXScalar = float(maxX)/float(viewWidth)
	else:
		minXScalar = (float(minX)/float(viewportRenderableMax)/aspectRatio)
		maxXScalar = (float(maxX)/float(viewportRenderableMax)/aspectRatio)

	if(renderWidth > renderHeight):
		minYScalar = ((float(minY)-heightClip)/float(viewWidth))
		maxYScalar = ((float(maxY)-heightClip)/float(viewWidth))
	else:
		minYScalar = ((float(minY)+heightDiff+heightClip)/aspectRatio)/float(viewportRenderableMax)
		maxYScalar = ((float(maxY)+heightDiff+heightClip)/aspectRatio)/float(viewportRenderableMax)

	# define viewport pixel based bounding box and scalar bounding box
	# scalar is the only one useful for rendering a region
	boundingBoxes = []
	boundingBoxasViewport = [maxY, minX, minY, maxX]
	boundingBoxAsScaler = [ maxYScalar, minXScalar, minYScalar, maxXScalar]
	boundingBoxes.append(boundingBoxAsScaler)
	
	# Show and render only the region of the selected mesh
	mel.eval('RenderViewWindow;')
	mel.eval('renderWindowCheckAndRenderRegion ' + str(maxYScalar) + ' ' + str(minXScalar) + ' ' + str(minYScalar) + ' ' + str(maxXScalar) + ';')
	return boundingBoxes
