"""
Script to look through all EBLMs and
cache the images needed to make finders
"""
import os
import sys
import urllib
from astroquery.skyview import SkyView
from astropy.io import fits
import astropy.units as u
import pymysql

def checkCache(cache_id):
    """
    Look for a cached image of this object
    """
    if os.path.exists(cache_id):
        return True
    else:
        return False

if __name__ == "__main__":
    # dimensions in arcmin
    width = 3
    height = 3
    # set up coords and surveys
    coordinates = "J2000"
    surveys = ["DSS2 Red", "DSS2 Blue", "SDSSr", "SDSSi"]
    # check for a cached image
    cache_location = "/Users/jmcc/Dropbox/PythonScripts/Finders/cache/"
    # query swasp_ids
    qry = """
        SELECT swasp_id, ra_hms, dec_dms
        FROM eblm_parameters
        WHERE dec_deg >= -25
        """
    with pymysql.connect(host='localhost',
                         db='eblm',
                         password='mysqlpassword') as cur:
        cur.execute(qry)
        results = cur.fetchall()
    # loop pver each swasp_id
    failed_ids = []
    n_swasp_ids = len(results)
    for i, row in enumerate(results):
        swasp_id = row[0]
        ra = row[1]
        dec = row[2]
        cache_id = "{}/{}_{}_{}.fits".format(cache_location,
                                             swasp_id,
                                             height,
                                             width)
        print("[{}:{}] {}".format(i+1, n_swasp_ids, swasp_id))
        position = "{} {}".format(ra, dec)
        cached = checkCache(cache_id)
        if not cached:
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
                failed_ids.append(swasp_id)
    print("{} failed objects".format(len(failed_ids)))
    for failed in failed_ids:
        print(failed)
