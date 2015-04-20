from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import get_object_or_404, render_to_response, render
from hs_core.views.utils import authorize
from hs_app_netCDF.models import NetcdfResource
from hs_app_tools_netCDF.forms import MetaElementsForm
from django.contrib import messages
from django.core.urlresolvers import reverse
from hs_app_tools_netCDF.nc_tool_functions.nc_meta_edit import *


# views for index page
def index_view(request, shortkey, state):
    """
    Netcdf tool landing page view function
    """
    res, _, _ = authorize(request, shortkey, edit=True, full=True, superuser=True)
    res_cls = res.__class__
    context = {}

    # context for resource obj
    if res_cls is NetcdfResource:
        context['nc_res'] = res
    else:
        context['nc_res'] = None

    # context for meta edit tool form
    meta_elements_form = MetaElementsForm()
    context['meta_elements_form'] = meta_elements_form

    # context for the nc_tool_obj:
    nc_tools_obj = NetcdfTools.objects.filter(short_id=res.short_id).first()
    if state == 'initial':
        if nc_tools_obj:
            nc_tools_obj.delete()
        context['nc_tools_obj'] = None
    elif state == 'processing':
        context['nc_tools_obj'] = nc_tools_obj

    return render(request, 'pages/nc_tools.html', context)


# views for Meta Edit Tool
def meta_edit_view(request, shortkey, **kwargs):
    """
    Meta Edit Tool view function
    """

    res, _, _ = authorize(request, shortkey, edit=True, full=True, superuser=True)
    res_cls = res.__class__

    if request.method == 'POST'and (res_cls is NetcdfResource):
        meta_elements = request.POST.getlist('meta_elements')
        file_process = request.POST.getlist('file_process')

        if meta_elements:
            check_info = run_meta_edit_tool(res, meta_elements, file_process, request)

            if check_info:
                check_info = 'Error! Metadata Editing: ' + check_info
                messages.add_message(request, messages.ERROR, check_info)
            else:
                suc_message = 'Success! Meta Edting is finished. '
                if 'new_ver_res' in file_process:
                    suc_message += 'A new version of resource is created. '
                if 'new_res' in file_process:
                    suc_message += 'A new resource is created. '
                messages.add_message(request, messages.SUCCESS, suc_message)
        else:
            messages.add_message(request, messages.ERROR,
                                 'Error! Metadata Editing: please select the metadata elements.')

    return HttpResponseRedirect(reverse('nc_tools:index', args=[res.short_id, 'processing']))



