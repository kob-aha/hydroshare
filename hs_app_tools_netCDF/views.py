import json
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import get_object_or_404, render_to_response, render
from django.forms.formsets import formset_factory
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from hs_core.views.utils import authorize
from hs_app_netCDF.models import NetcdfResource
from hs_app_tools_netCDF.forms import *
from hs_app_tools_netCDF.nc_tool_functions.nc_meta_edit import *
from hs_app_tools_netCDF.nc_tool_functions.nc_data_subset import *
from hs_app_tools_netCDF.nc_tool_functions.nc_data_inspector import *
from hs_app_tools_netCDF.nc_tool_functions.nc_tools_utils import *

# view for create ncdump file button
@login_required
def create_ncdump_view(request, shortkey):
    """
    create ncdump file function for create ncdump button in landing page
    """

    res, res_cls = get_res_and_class(request, shortkey)

    if res_cls is NetcdfResource:
        nc_file_obj = None
        nc_file_name = ''
        for f in ResourceFile.objects.filter(object_id=res.id):
            ext = os.path.splitext(f.resource_file.name)[-1]
            if ext == '.nc':
                nc_file_obj = f
                nc_file_name = os.path.basename(f.resource_file.name)
                break

        if nc_file_obj:
            nc_file_path = nc_file_obj.resource_file.file.name
            nc_dump_file_obj = add_ncdump_file_to_res(res, nc_file_path, nc_file_name)

    if nc_dump_file_obj:
        messages.add_message(request, messages.SUCCESS, 'Success! The header info .txt file is created.')
    else:
        messages.add_message(request, messages.ERROR, 'Error! Failed to create the netcdf header info .txt file.')

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


# view for tool landing page
@login_required
def index_view(request, shortkey, state):
    """
    Netcdf tool landing page view function
    """

    res, res_cls = get_res_and_class(request, shortkey)
    context = {}

    # context for resource obj
    if res_cls is NetcdfResource:
        context['nc_res'] = res
    else:
        context['nc_res'] = None

    # context for meta edit tool form
    meta_elements_form = MetaElementsForm()
    context['meta_elements_form'] = meta_elements_form

    # context for data subset tool form
    dimension_formset = create_dimension_formset(res)
    context['dimension_formset'] = dimension_formset
    variable_names_form = create_variable_names_form(res)

    # context for data inspector form
    context['variable_names_form'] = variable_names_form
    context['data_inspector_form'] = create_data_inspector_form(res)

    # # context for file process form
    # file_process = FileProcess()
    # context['file_process_form'] = file_process

    # # context for the nc_tool_obj:
    # nc_tools_obj = NetcdfTools.objects.filter(short_id=res.short_id).first()
    # if state == 'initial':
    #     if nc_tools_obj:
    #         nc_tools_obj.delete()
    #     context['nc_tools_obj'] = None
    # elif state == 'processing':
    #     context['nc_tools_obj'] = nc_tools_obj

    return render(request, 'pages/nc_tools.html', context)


# view for meta edit Tool
@login_required
def meta_edit_view(request, shortkey, **kwargs):
    """
    Meta Edit Tool view function
    """

    res, res_cls = get_res_and_class(request, shortkey)

    if request.method == 'POST'and (res_cls is NetcdfResource):
        meta_elements = request.POST.getlist('meta_elements')

        if meta_elements:
            check_info = run_meta_edit_tool(res, meta_elements, request)

            if check_info:
                messages.add_message(request, messages.ERROR, 'Error! Metadata Editing: ' + check_info)
            else:
                messages.add_message(request, messages.SUCCESS, 'Success! Meta Editing is finished. ')
        else:
            messages.add_message(request, messages.ERROR,
                                 'Error! Metadata Editing: please select the required options.')

    return HttpResponseRedirect(reverse('nc_tools:index', args=[res.short_id, 'processing']))


# view for data inspector tool
@login_required
def data_inspector_view(request, shortkey, **kwargs):
    """
    Data Inspector tool view function
    """

    res, res_cls = get_res_and_class(request, shortkey)

    if request.is_ajax and res_cls is NetcdfResource:
        var_name = request.POST.getlist('var_name')[0]
        nc_file_path = get_nc_file_path_from_res(res)
        data_inspector_info = get_data_inspector_info(nc_file_path, var_name)
        ajax_response_data = data_inspector_info

    else:
        messages.add_message(request, messages.ERROR,
                             'Error! Data Inspector: please check if the tool is running for NetCDF resource.')

    return HttpResponse(json.dumps(ajax_response_data))


# views for data subset tool
@login_required
def data_subset_view(request, shortkey, **kwargs):
    """
    Data subset tool view function
    """

    if request.method == 'POST':
        execute_info = run_data_subset_tool(request, shortkey)

        if execute_info[0] == 'error':
            error_info = 'Error! Data Subset: ' + execute_info[1]
            messages.add_message(request, messages.ERROR, error_info)
        else:
            suc_message = execute_info[1]
            messages.add_message(request, messages.SUCCESS, suc_message)

    return HttpResponseRedirect(reverse('nc_tools:index', args=[shortkey, 'processing']))