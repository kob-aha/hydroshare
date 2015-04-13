from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import get_object_or_404, render_to_response, render
from hs_core.views.utils import authorize
from hs_app_netCDF.models import NetcdfResource
from hs_app_tools_netCDF.forms import MetaElementsForm
from hs_app_tools_netCDF.models import *
from hs_core.hydroshare.resource import ResourceFile
from django.contrib import messages
import os
from django.core.files import File
from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse


# views for index page
def index_view(request, shortkey, state):
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

        if meta_elements and file_process:
            check_info = write_meta_in_file(res)
            if check_info:
                # TODO: check the file_process parameter and to the processes
                messages.add_message(request, messages.ERROR, check_info)
            else:
                messages.add_message(request, messages.SUCCESS, 'Success! Metadata Editing is finished.')
        else:
            messages.add_message(request, messages.ERROR,
                                 'Error! Metadata Editing: please select both of the required checkboxes.')

    return HttpResponseRedirect(reverse('nc_tools:index', args=[res.short_id, 'processing']))


def write_meta_in_file(res):
    check_info = ''
    for f in ResourceFile.objects.filter(object_id=res.id):
        ext = os.path.splitext(f.resource_file.name)[-1]
        if ext == '.nc':
            # create or get the nc_tools_obj
            nc_tools_obj = NetcdfTools.objects.filter(short_id=res.short_id).first()
            if not nc_tools_obj:
                nc_tools_obj = NetcdfTools(short_id=res.short_id)

            # add meta_edit initial file
            meta_edit_file_content = ContentFile(f.resource_file.file.read())
            meta_edit_file_name = os.path.basename(f.resource_file.name)
            nc_tools_obj.meta_edit_file.save(meta_edit_file_name, meta_edit_file_content)
            nc_tools_obj.save()

            # write meta in the file TODO write meta back to nc_file
            a= 'jamy'
            # from hs_app_netCDF.nc_functions.nc_meta import *
            # import netCDF4
            #
            # nc_dataset = netCDF4.Dataset(nc_tools_obj.meta_edit_file.file.name,'a')
            # nc_dataset.title ='this is test for metaediting'
            # nc_dataset.close()
            # meta_info = get_nc_meta_dict(nc_tools_obj.meta_edit_file.file.name)
            return check_info

    check_info = "Error! Metadata Editing: there is no .nc file for editing. "

    return check_info
