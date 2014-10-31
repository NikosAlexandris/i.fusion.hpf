#!/usr/bin/env python
#-*- coding:utf-8 -*-


from grass.pygrass.modules.shortcuts import raster as r, vector as v, general as g, display as d
from grass.pygrass.modules import Module

# Simply commented is bash code!

#if [ -z "$GISBASE" ] ; then
    g.message -e "You must be in GRASS GIS to run this program." #1>&2
    #exit 1
#fi