import os
from astropy import constants, units as u, table, stats, coordinates, wcs, log, coordinates as coord, convolution, modeling, time; from astropy.io import fits, ascii
import reproject
import glob
from reproject.mosaicking import find_optimal_celestial_wcs
from reproject.mosaicking import reproject_and_coadd
from reproject import reproject_interp

import requests
from bs4 import BeautifulSoup

from astropy.utils.console import ProgressBar

from astroquery.eso import Eso

Eso.ROW_LIMIT = 10000
Eso.cache_location = '.'
Eso.login('aginsburg')

tbl = Eso.query_surveys(surveys='VPHASplus', coord1=0, coord2=0, coord_sys='gal', box=5*u.deg)
files = Eso.retrieve_data(tbl['ARCFILE'])

hdus = [fits.open(x) for x in glob.glob("ADP*.fits.fz")]
hdus = [h for h in hdus if (260 < h[1].header['CRVAL1'] < 270)]
#wcs_out, shape_out = find_optimal_celestial_wcs([h[1] for h in hdus], frame='galactic')

wcs_out = wcs.WCS({"CTYPE1": "GLON-CAR",
                   "CTYPE2": "GLAT-CAR",
                   "CRPIX1": 14000.0,
                   "CRPIX2": 14000.0,
                   "CRVAL1": 0.0,
                   "CRVAL2": 0.0,
                   "CDELT1": -1/3600., # downsample to 1" pixels
                   "CDELT2": 1/3600.,
                   "CUNIT1": "deg",
                   "CUNIT2": "deg",
                  })
shape_out = (28000,28000)

array_line, footprint = reproject_and_coadd([h[1] for h in hdus], wcs_out, shape_out=shape_out, reproject_function=reproject_interp)
fits.PrimaryHDU(data=array_line, header=wcs_out.to_header()).writeto('gc_vphas_mosaic_halpha.fits', overwrite=True)
