# -*- coding: utf-8 -*-
"""
Created on Sat Nov  1 09:23:09 2014

@author: nik
"""

#!/usr/bin/env python
 
# simple example for pyGRASS usage: raster processing via modules approach
# source: <http://grasswiki.osgeo.org/wiki/GRASS_and_Python>
 
from grass.pygrass.modules.shortcuts import general as g
from grass.pygrass.modules.shortcuts import raster as r
 
g.message("Filter elevation map by a threshold...")
 
# set computational region
input = '12DEC02053035.pan'
g.region(rast=input)
 
# hardcoded:
# r.mapcalc('elev_100m = if(elevation > 100, elevation, null())', overwrite = True)
# with variables
 
output = 'test'
thresh = 100
r.mapcalc("%s = if(%s > %d, %s, null())" % (output, input, thresh, input), overwrite = True)
r.colors(map=output, color="random")