from django.views.decorators.http import require_http_methods
from django.utils.encoding import smart_str
from django.http import HttpResponse, JsonResponse
from service import create_mxd_process
import os
from django.views.decorators.csrf import csrf_exempt
import json
import logging


logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(['GET'])
def healthcheck(request):
    """

    :param request: Takes json with keys 'geopackage' and 'mxd'.
    The `geopackage` key is required and will get the file written to the mxd file.
    If `mxd` is present the result will be written to that location (i.e. an nfs mount) if not present the
    result will be returned.
    :return:
    """
    try:
        import arcpy
        return JsonResponse({"Success": True}, status=200)
    except Exception as e:
        logger.error(e)
        return JsonResponse({"Success": False,
                             "Errors": [{"message": "Could not initialize ArcGIS"}]}, status=500)

@csrf_exempt
@require_http_methods(['GET', 'POST'])
def mxd(request):
    """

    :param request: Takes json with keys 'geopackage' and 'mxd'.
    The `geopackage` key is required and will get the file written to the mxd file.
    If `mxd` is present the result will be written to that location (i.e. an nfs mount) if not present the
    result will be returned.
    :return:
    """
    if request.method == 'POST':
        r = json.loads(request.body)
        if not r.get('gpkg'):
            return JsonResponse({"error": "Invalid method",
                                 "message": "This endpoint requires a key called 'gpkg' with a path to the gpkg."},
                                status=401)
        mxd = create_mxd_process(mxd=r.get('mxd'), gpkg=r['gpkg'])
        if r.get('mxd'):
            return JsonResponse({"Success": True}, status=201)
        mxd_file_name = "{0}.mxd".format(os.path.splitext(os.path.basename(r.get('gpkg')))[0])
        response = HttpResponse(content_type='application/force-download', status=201)
        response.write(mxd)
        response['Content-Disposition'] = 'attachment; filename={0}'.format(smart_str(mxd_file_name))
        response['Content-Length'] = len(mxd)
        return response
    else:
        return JsonResponse({"error": "Invalid method",
                             "message": "This endpoint requires a POST request with a JSON body, with the name of the geopackage."}, status=401)