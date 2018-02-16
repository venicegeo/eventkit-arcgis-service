from django.views.decorators.http import require_http_methods
from django.utils.encoding import smart_str
from django.http import HttpResponse, JsonResponse
from service import get_temp_mxd
import os
from django.views.decorators.csrf import csrf_exempt
import json
import logging


logger = logging.getLogger(__name__)

# None of this works, I think the arcpy stuff needs to run on main thread will look at celery
@csrf_exempt
@require_http_methods(['GET', 'POST'])
def mxd(request):
    if request.method == 'POST':
        r = json.loads(request.body)
        if r.get('geopackage'):
            with get_temp_mxd(r['geopackage']) as mxd_file:
                mxd_file_name = "{0}.mxd".format(os.path.splitext(os.path.basename(r.get('geopackage')))[0])
                response = HttpResponse(content_type='application/force-download')
                with open(mxd_file.name) as open_file:
                    response.write(open_file)
                    response['Content-Disposition'] = 'attachment; filename={0}'.format(smart_str(mxd_file_name))
                    response['Content-Length'] = open_file.tell()
            return response
    else:
        return JsonResponse({"error": "Invalid method",
                             "message": "This endpoint requires a POST request with a JSON body, with the name of the geopackage."}, status=401)