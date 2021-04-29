# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

try:
    import idfpy
    idfpy_imported = True
except ImportError:
    idfpy_imported = False

import rasterio
import numpy as np

from functools import partial
import logging
import os

log = logging.getLogger(os.path.basename(__file__))

# rio.DatasetReader.sample method does not work when trying to sample  
# outside of the raster's spaial extent. This is a workaround.
def take_rio_sample(dataset, coords):
    ''' take sample from raster workaround method (simplified without rasterio.windows.Window) 
    it yields np.nan if you look outside of the raster's spatial extent'''
    for x,y in coords:
        ix, iy = dataset.index(x, y)
        if ix < dataset.shape[0] and ix >= 0 and iy < dataset.shape[1] and iy >= 0:
            yield [dataset.read()[0, ix, iy]]
        else:
            yield [np.nan]


def sample_raster(rasterfile, coords):
    '''sample raster file at coords'''
    log.debug('reading rasterfile {}'.format(os.path.basename(rasterfile)))
    with rasterio.open(rasterfile) as src:
        for value in take_rio_sample(src, coords):
            if value[0] in src.nodatavals:
                yield np.nan
            elif np.isnan(value[0]) and any(np.isnan(src.nodatavals)):
                yield np.nan
            else:
                yield float(value[0])


def sample_idf(idffile, coords):
    '''sample IDF file at coords'''
    log.debug('reading idf file {}'.format(os.path.basename(idffile)))
    with idfpy.open(idffile) as src:
        for value in src.sample(coords):
            if value[0] == src.header['nodata']:
                yield np.nan
            elif np.isnan(value[0]) and any(np.isnan(src.header['nodata'])):
                yield np.nan
            else:
                yield float(value[0])


def sample(gridfile, coords):
    '''sample gridfile at coords'''
    if idfpy_imported and gridfile.lower().endswith('.idf'):
        sample = partial(sample_idf)
    else:
        sample = partial(sample_raster)
    return sample(gridfile, coords)
