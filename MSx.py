# -*- coding: utf-8 -*-
"""
@author: nik | Created on Tue Nov  4 15:20:27 2014
"""

import grass.script as grass


class Image:
    def __init__(self, msx):
        self.meta = grass.parse_command('r.info', map=msx, flags='e')
        self.map = self.meta['map']
        self.mapset = self.meta['mapset']
        self.location = self.meta['location']
        self.database = self.meta['database']
        self.date = self.meta['date']
        self.creator = self.meta['creator']
        self.title = self.meta['title']
        self.timestamp = self.meta['timestamp']
        self.units = self.meta['units']
        self.vdatum = self.meta['vdatum']
        self.source1 = self.meta['source1']
        self.source2 = self.meta['source2']
        self.description = self.meta['description']
        self.comments = self.meta['comments']
        self.info = grass.parse_command('r.info', map=msx, flags='g')
        self.north = self.info['north']
        self.south = self.info['south']
        self.east = self.info['east']
        self.west = self.info['west']
        self.nsres = self.info['nsres']
        self.ewres = self.info['ewres']
        self.rows = self.info['rows']
        self.cols = self.info['cols']
        self.cells = self.info['cells']
        self.datatype = self.info['datatype']
        self.ncats = self.info['ncats']

    def __str__(self):
        return "Image: " + self.map + "@" + self.mapset