"""
Code to generate finding charts

To do:
"""
import sys
import urllib
import numpy as np
from astroquery.skyview import SkyView
from astropy.io import fits
import astropy.units as u
import matplotlib
matplotlib.use('QT5Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from scipy.ndimage import rotate

def checkCache(cache_id):
    """
    Look for a cached image of this object
    """
    try:
        data = fits.open(cache_id)[0].data
        print('Found cached image {}'.format(cache_id))
    except FileNotFoundError:
        data = None
        print('No cached image found for {}'.format(cache_id))
    return data

def correctPa(angle):
    """
    Correct the PA for instrument config
    """
    return angle - 90

def drawSlit(ax, data, slit_width=20):
    """
    Work out the slit position from the image data
    """
    y, x = data.shape
    slit_upper_left = (0, int(y/2)-slit_width/2)
    rect = patches.Rectangle(slit_upper_left,
                             x-1, slit_width,
                             linewidth=1,
                             edgecolor='r',
                             facecolor='none')
    ax.add_patch(rect)
    return ax

if __name__ == "__main__":
    # set up the object
    object_id = "1SWASPJ084626.17+445626.3"
    position = "08:46:26.17 +44:56:26.3"
    angle = 137
    coordinates = "J2000"
    surveys = ["SDSSr", "SDSSi", "DSS2 Red", "DSS2 Blue"]
    # dimensions in arcmin
    width = 3
    height = 3
    # check for a cached image
    cache_location = "/Users/jmcc/Dropbox/PythonScripts/Finders/cache/"
    cache_id = "{}/{}_{}_{}.fits".format(cache_location,
                                         object_id,
                                         height,
                                         width)
    data = checkCache(cache_id)
    if data is None:
        sv = SkyView()
        for survey in surveys:
            print(survey)
            try:
                path = sv.get_images(position=position,
                                     coordinates=coordinates,
                                     survey=survey,
                                     width=width*u.arcmin,
                                     height=height*u.arcmin)
                data = path[0][0].data
                hdr = path[0][0].header
                # write out the fits file into the cache
                fits.writeto(cache_id, data, header=hdr)
                break
            except urllib.error.HTTPError:
                print('No image in {} for {}'.format(survey, position))
                continue
        # if we get here there are no images!
        else:
            print('No images found, exiting...')
            sys.exit(1)
    # if we make it here plot the finder
    fig, ax = plt.subplots(1, figsize=(10, 10))
    ndata = rotate(data, correctPa(angle))
    # cameras need to have the images fliped about the Y axis
    # to match up with DS9 x and y axes
    ndata =  np.flip(ndata, 1)
    ax.imshow(ndata, origin='lower')
    ax = drawSlit(ax, ndata)
    plt.show()
