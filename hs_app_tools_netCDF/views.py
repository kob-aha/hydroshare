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
            check_info = run_meta_edit_tool(res, meta_elements, file_process)
            if check_info:
                messages.add_message(request, messages.ERROR, check_info)
            else:
                messages.add_message(request, messages.SUCCESS, 'Success! Metadata Editing is finished.')
        else:
            messages.add_message(request, messages.ERROR,
                                 'Error! Metadata Editing: please select both of the required checkboxes.')

    return HttpResponseRedirect(reverse('nc_tools:index', args=[res.short_id, 'processing']))


def run_meta_edit_tool(res, meta_elements, file_process):
    check_info = ''
    for f in ResourceFile.objects.filter(object_id=res.id):
        ext = os.path.splitext(f.resource_file.name)[-1]
        if ext == '.nc':
            # create or get the nc_tools_obj
            nc_tools_obj = NetcdfTools.objects.filter(short_id=res.short_id).first()
            if not nc_tools_obj:
                nc_tools_obj = NetcdfTools(short_id=res.short_id)

            # add meta_edit initial file
            meta_edit_file_name = os.path.basename(f.resource_file.name)
            meta_edit_file = open(f.resource_file.file.name)  # ContentFile(f.resource_file.file.read())
            nc_tools_obj.meta_edit_file.save(meta_edit_file_name, File(meta_edit_file))

            # write meta in the file
            nc_file_name = nc_tools_obj.meta_edit_file.file.name
            check_info = edit_meta_in_file(res, nc_file_name, meta_elements)

            # file process after editing
            if check_info:
                return check_info
            else:
                return check_info

    check_info = "Error! Metadata Editing: there is no .nc file in the resource. "

    return check_info


def edit_meta_in_file(res, nc_file_name, meta_elements):
    try:
        import netCDF4
        check_info = ''
        nc_dataset = netCDF4.Dataset(nc_file_name, 'a')

        # a= res.get_absolute_url() #'/resource/short_id/'
        # a= res.metadata.subjects.all().first()
        # a = res.metadata.subjects.all().first().value# relation object manager
        # a= res.metadata.rights # meta object: statement, url is useful
        # a = res.metadata.sources # relation object manager
        # a = res.metadata.sources.all().frist()
        # a=res.metadata.relations
        # a=res.metadata.relations.all().first() # meta object: has attr as type, value,
        # a=res.metadata.variables.all()
        # a=res.metadata.variables.all().first()
        # a= res.get_absolute_url
        # a = res.metadata.description.abstract # string: value of the abstract

        if 'title' in meta_elements and (res.metadata.title.value != 'Untitled Resource'):  # Done
            nc_dataset.title = res.metadata.title.value

        if 'description' in meta_elements and res.metadata.description.abstract:  #Done
            nc_dataset.summary = res.metadata.description.abstract

        if 'subjects' in meta_elements and res.metadata.subjects.all().first():  #Done
            res_meta_subjects = []
            for res_subject in res.metadata.subjects.all():
                res_meta_subjects.append(res_subject.value)
            nc_dataset.keywords = ','.join(res_meta_subjects)

        if 'rights' in meta_elements and res.metadata.rights: #Done
            nc_dataset.license = "{0} \n {1}".format(res.metadata.rights.statement, res.metadata.rights.url)


        if 'publisher' in meta_elements: #Done TODO not sure about this element info
            nc_dataset.publisher_name = 'HydroShare'
            nc_dataset.publisher_url = 'http://www.hydroshare.org'

        if 'identifier' in meta_elements and res.metadata.identifiers.all(): #Done
            if res.metadata.identifiers.all().filter(name="doi"):
                res_identifier = res.metadata.identifiers.all().filter(name="doi")[0]
            else:
                res_identifier = res.metadata.identifiers.all().filter(name="hydroShareIdentifier")[0]
            nc_dataset.id = res_identifier.url

        # if 'source' in meta_elements and res.metadata.sources.all():
        #     pass

        if 'relation' in meta_elements and res.metadata.relations.all().filter(type='cites'):
            pass

        if 'variable' in meta_elements and res.metadata.variables.all().first():
            for variable in res.metadata.variables.all():
                pass

        nc_dataset.close()

        # just for testing
        from hs_app_netCDF.nc_functions.nc_meta import get_nc_meta_dict
        meta_info = get_nc_meta_dict(nc_file_name)

    except:
        nc_tools_obj = NetcdfTools.objects.filter(short_id=res.short_id).first()
        if nc_tools_obj:
            nc_tools_obj.meta_edit_file.delete()
        check_info = "Error! Metadata Editing: failed to edit the meta info in the .nc file."

    return check_info

META_ELEMENTS = (
        ('creator', 'Creator'),
        ('contributor', 'Contributor'),
        ('spatial_coverage', 'Spatial Coverage'),
        ('temporal_coverage', 'Temporal Coverage'),
    )