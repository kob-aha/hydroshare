from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render_to_response, render
from hs_core.views.utils import authorize
from hs_app_netCDF.models import NetcdfResource

# views for index page
def index(request, shortkey, **kwargs):
    res, _, _ = authorize(request, shortkey, edit=True, full=True, superuser=True)
    res_cls = res.__class__
    context = {}
    
    if res_cls is NetcdfResource:
        context['nc_res'] = res
    else:
        context['nc_res'] = None

    return render(request, 'pages/nc_tools.html', context)
