import os
import logging
from django.conf import settings
import arcpy
import tempfile
import shutil
from contextlib import contextmanager


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

    try:
        template_file = os.path.abspath(os.path.join(BASE_DIR, "eventkit_arcgis_service", "static", "template.mxd"))
        logger.debug('Opening MXD: {0}'.format(template_file))
        shutil.copyfile(template_file, temp_file.name)
        mxd = arcpy.mapping.MapDocument(temp_file.name)
        ext = None
        for lyr in arcpy.mapping.ListLayers(mxd):
            logging.debug(lyr)
            try:
                print lyr.workspacePath
            except Exception:
                continue
            try:
                lyr.findAndReplaceWorkspacePath(lyr.workspacePath, gpkg, True)
                if lyr.isFeatureLayer and lyr.name != "main.boundary":
                    arcpy.RecalculateFeatureClassExtent_management(lyr)
                    ext = lyr.getExtent()
            except Exception as e:
                print str(e)
        logger.debug('Getting dataframes...')
        df = arcpy.mapping.ListDataFrames(mxd, "Layers")[0]
        df.extent = ext
        mxd.save()
        del mxd #remove handle on file
        yield temp_file.name
    finally:
        # temp_file_name = temp_file.name
        temp_file.close()
        # os.unlink(temp_file.name)
        # assert not os.path.isfile(temp_file_name)


if __name__ == "__main__":
    with get_temp_mxd(r"F:\data\template\data\osm\template.gpkg") as temp_mxd_file:
        shutil.copy(temp_mxd_file, r"F:\eventkit_arcgis_service\eventkit_arcgis_service\static\template7.mxd")
