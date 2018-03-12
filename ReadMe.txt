Author: 	Ryan Trowbridge
Modified: 	5-22-09
Command:	rtRenderSelectedMeshesRegion()
Description:
This Python script will run in Maya 2008 and beyond. Select one or more meshes and it will figure out the bounding box of those meshes in the viewport and only render out the region of those selected meshes based on the bounding box. The render size is based on your current render size settings. So if you wanted to change the size of the render you could set those settings through script then select your objects and then run the script function.