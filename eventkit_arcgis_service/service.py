from __future__ import absolute_import

import os
import logging
from django.conf import settings
import tempfile
import shutil
from contextlib import contextmanager
from multiprocessing import Pool
import json
import arcpy


logger = logging.getLogger(__name__)

try:
    BASE_DIR = settings.BASE_DIR
except Exception:
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))


@contextmanager
def get_temp_mxd(gpkg):
    temp_file = tempfile.NamedTemporaryFile(mode='rb', delete=False)
    temp_file.close()
    temp_file.name = "{0}.mxd".format(temp_file.name)
    ext = arcpy.Extent(0, 0, 0, 0)  # default to global
    try:
        template_file = os.path.abspath(os.path.join(BASE_DIR, "eventkit_arcgis_service", "static", "template.mxd"))
        logger.debug('Opening MXD: {0}'.format(template_file))
        logger.debug('Updating for filepath: {0}'.format(gpkg))
        shutil.copyfile(template_file, temp_file.name)
        mxd = arcpy.mapping.MapDocument(temp_file.name)
        for lyr in arcpy.mapping.ListLayers(mxd):
            logging.debug(lyr)
            try:
                logger.debug(lyr.workspacePath)
            except Exception:
                continue
            try:
                # Try to update the extents based on the layers
                lyr.findAndReplaceWorkspacePath(lyr.workspacePath, gpkg, False)
                if lyr.isFeatureLayer and lyr.name != "main.boundary":
                    arcpy.RecalculateFeatureClassExtent_management(lyr)
                    lyr_ext = lyr.getExtent()
                    if lyr_ext:
                        ext = expand_extents(ext, lyr_ext)
            except AttributeError:
                continue
            except Exception as e:
                logger.warning(e)
        logger.debug('Getting dataframes...')
        df = arcpy.mapping.ListDataFrames(mxd, "Layers")[0]
        # if extent not updated then use global bounds
        if extent2bbox(ext) == [0, 0, 0, 0]:
            ext = arcpy.Extent(-180, -90, 180, 90)
        df.extent = ext
        mxd.save()
        del mxd  # remove handle on file
        yield temp_file.name
    finally:
        temp_file.close()
        os.unlink(temp_file.name)


def create_mxd(mxd=None, gpkg=None):
    """
    Updates the template mxd with a new gpkg datasource. If an mxd is provided the result is written to that file.
    :param mxd: An mxd to write the result to (optional).
    :param gpkg: The geopackage file to use for updating the mxd.
    :return: The contents (binary) of the mxd file.
    """
    with get_temp_mxd(gpkg) as temp_mxd_file:
        # copy temp file to permanent file if specified.
        if mxd:
            shutil.copy(temp_mxd_file, mxd)
        with open(temp_mxd_file, 'rb') as open_mxd_file:
            return open_mxd_file.read()


def create_mxd_process(mxd=None, gpkg=None):
    """
    This wraps create_mxd to overcome issues with licensing by running in a unique process.
    Updates the template mxd with a new gpkg datasource. If an mxd is provided the result is written to that file.
    :param mxd: An mxd to write the result to (optional).
    :param gpkg: The geopackage file to use for updating the mxd.
    :return: The contents (binary) of the mxd file.
    """
    pool = Pool()
    result = pool.apply_async(create_mxd, kwds={"mxd": mxd, "gpkg": gpkg})
    mxd = result.get()
    return mxd


def expand_extents(original_bbox, new_bbox):
    return bbox2ext(expand_bbox(extent2bbox(original_bbox), extent2bbox(new_bbox)))


def extent2bbox(ext):
    bounds = json.loads(ext.JSON)
    return [val for k, val in bounds.iteritems()]


def bbox2ext(bbox):
    return arcpy.Extent(*bbox)


def expand_bbox(original_bbox, new_bbox):
    """
    Takes two bboxes and returns a new bbox containing the original two.
    :param bbox: A list representing [west, south, east, north]
    :param new_bbox: A list representing [west, south, east, north]
    :return: A list containing the two original lists.
    """
    if not original_bbox:
        original_bbox = list(new_bbox)
        return original_bbox
    original_bbox[0] = min(new_bbox[0], original_bbox[0])
    original_bbox[1] = min(new_bbox[1], original_bbox[1])
    original_bbox[2] = max(new_bbox[2], original_bbox[2])
    original_bbox[3] = max(new_bbox[3], original_bbox[3])
    return original_bbox
