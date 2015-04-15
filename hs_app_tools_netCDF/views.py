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
import numpy as np
from hs_core import hydroshare
from hs_core.hydroshare import utils

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

        if meta_elements:
            check_info = run_meta_edit_tool(res, meta_elements, file_process)
            if check_info:
                messages.add_message(request, messages.ERROR, check_info)
            else:
                messages.add_message(request, messages.SUCCESS, 'Success! Metadata Editing is finished.')
        else:
            messages.add_message(request, messages.ERROR,
                                 'Error! Metadata Editing: please select the metadata elements.')

    return HttpResponseRedirect(reverse('nc_tools:index', args=[res.short_id, 'processing']))


def run_meta_edit_tool(res, meta_elements, file_process):
    check_info = ''
    import os
    for f in ResourceFile.objects.filter(object_id=res.id):
        ext = os.path.splitext(f.resource_file.name)[-1]
        if ext == '.nc':
            # initiate the nc_tools_obj for meta edit tool
            nc_tools_obj = NetcdfTools.objects.filter(short_id=res.short_id).first()
            if not nc_tools_obj:
                nc_tools_obj = NetcdfTools(short_id=res.short_id)
            else:
                if nc_tools_obj.meta_edit_file:
                    storage, path = nc_tools_obj.meta_edit_file.storage, nc_tools_obj.meta_edit_file.path
                    nc_tools_obj.meta_edit_file.delete()
                    storage.delete(path)



            # add meta_edit initial file
            meta_edit_file_name = os.path.basename(f.resource_file.name)
            if 'metaEdit_' not in os.path.basename(f.resource_file.name):
                meta_edit_file_name = 'metaEdit_'+os.path.basename(f.resource_file.name)
            meta_edit_file = open(f.resource_file.file.name)  # ContentFile(f.resource_file.file.read())
            nc_tools_obj.meta_edit_file.save(meta_edit_file_name, File(meta_edit_file))

            # write meta in the file
            nc_file_name = nc_tools_obj.meta_edit_file.file.name
            check_info = edit_meta_in_file(res, nc_file_name, meta_elements)

            # file process after editing
            if check_info:
                return check_info
            else:
                if 'new_ver_res' in file_process:

                    try:
                        # add new .nc file

                        for f in ResourceFile.objects.filter(object_id=res.id):
                            f.resource_file.delete()
                            f.delete()
                        f = ResourceFile.objects.create(content_object=res)
                        meta_edit_file_name = os.path.basename(nc_tools_obj.meta_edit_file.name).replace("metaEdit_",'')
                        meta_edit_file = open(nc_tools_obj.meta_edit_file.file.name)
                        f.resource_file.save(meta_edit_file_name, File(meta_edit_file))

                        # create InMemoryUploadedFile text file to store the dump info and add it to resource

                        import hs_app_netCDF.nc_functions.nc_dump as nc_dump
                        if nc_dump.get_nc_dump_string_by_ncdump(nc_file_name):
                            dump_str = nc_dump.get_nc_dump_string_by_ncdump(nc_file_name)
                        else:
                            dump_str = nc_dump.get_nc_dump_string(nc_file_name)
                        if dump_str:
                            from django.core.files.uploadedfile import InMemoryUploadedFile
                            import StringIO, os
                            io = StringIO.StringIO()
                            io.write(dump_str)
                            dump_file_name = '.'.join(os.path.basename(nc_file_name.replace("metaEdit_",'')).split('.')[:-1])+'_header_info.txt'
                            dump_file = InMemoryUploadedFile(io, None, dump_file_name, 'text', io.len, None)
                            dump_file.seek(0)
                            hydroshare.add_resource_files(res.short_id, dump_file)

                    except:
                        for f in ResourceFile.objects.filter(object_id=res.id):
                            if not f.resource_file:
                                f.delete()
                        check_info = "Error! Metadata Editing failed to create new version of resource with the edited file."

                if 'new_res' in file_process:
                    try:
                        pass
                    except:
                        if check_info:
                            check_info = "Error! Metadata Editing failed to create new version of resource and the new resource."
                        else:
                            check_info = "Error! Metadata Editing failed to create a new resource with the edited file."

                return check_info

    check_info = "Error! Metadata Editing: there is no .nc file in the resource. "

    return check_info


def edit_meta_in_file(res, nc_file_name, meta_elements):
    try:
        import netCDF4
        check_info = ''
        nc_dataset = netCDF4.Dataset(nc_file_name, 'a')

        # edit metadata elements
        if 'title' in meta_elements and (res.metadata.title.value != 'Untitled Resource'):  # Done
            nc_dataset.title = res.metadata.title.value

        if 'description' in meta_elements and res.metadata.description.abstract:  # Done
            nc_dataset.summary = res.metadata.description.abstract

        if 'subjects' in meta_elements and res.metadata.subjects.all().first():
            res_meta_subjects = []
            for res_subject in res.metadata.subjects.all():
                res_meta_subjects.append(res_subject.value)
            nc_dataset.keywords = ','.join(res_meta_subjects)

        if 'rights' in meta_elements and res.metadata.rights:
            nc_dataset.license = "{0} {1}".format(res.metadata.rights.statement, res.metadata.rights.url)

        if 'publisher' in meta_elements: #TODO need to confirm about this element info
            nc_dataset.publisher_name = 'HydroShare'
            nc_dataset.publisher_url = 'http://www.hydroshare.org'

        if 'identifier' in meta_elements and res.metadata.identifiers.all():
            if res.metadata.identifiers.all().filter(name="doi"):
                res_identifier = res.metadata.identifiers.all().filter(name="doi")[0]
            else:
                res_identifier = res.metadata.identifiers.all().filter(name="hydroShareIdentifier")[0]
            nc_dataset.id = res_identifier.url

        if 'source' in meta_elements and res.metadata.sources.all():  # Done
            res_meta_source = []
            for source in res.metadata.sources.all():
                res_meta_source.append(source.derived_from)
            nc_dataset.source = ' \n'.join(res_meta_source)

        if 'relation' in meta_elements and res.metadata.relations.all().filter(type='cites'): # Done
            res_meta_ref = []
            for reference in res.metadata.relations.all().filter(type='cites'):
                res_meta_ref.append(reference.value)
            nc_dataset.references = ' \n'.join(res_meta_ref)

        if 'variable' in meta_elements and res.metadata.variables.all():
            meta_elements.remove('variable')
            res_var_dict = nc_dataset.variables
            for variable in res.metadata.variables.all():
                if variable.name in res_var_dict.keys():
                    res_var = res_var_dict[variable.name]
                    if variable.unit != 'Unknown':
                        res_var.setncattr('units', variable.unit)
                    if variable.descriptive_name:
                        res_var.setncattr('long_name', variable.descriptive_name)
                    if variable.method:
                        res_var.setncattr('comment', variable.method)
                    if variable.missing_value:
                        try:
                            dt = np.dtype(res_var.datatype.name)
                            missing_value = np.fromstring(variable.missing_value+' ', dtype=dt.type, sep=" ")
                            res_var.setncattr('missing_value', missing_value)
                        except:
                            pass

        if 'temporal_coverage' in meta_elements and res.metadata.coverages.all().filter(type='period').first():
            res_meta_cov = res.metadata.coverages.all().filter(type='period').first()
            nc_dataset.time_coverage_start = res_meta_cov.value['start']
            nc_dataset.time_coverage_end = res_meta_cov.value['end']

        if 'spatial_coverage' in meta_elements and res.metadata.coverages.all().filter(type='box').first():
            res_meta_cov = res.metadata.coverages.all().filter(type='box').first()
            nc_dataset.geospatial_lat_min = res_meta_cov.value['southlimit']
            nc_dataset.geospatial_lat_max = res_meta_cov.value['northlimit']
            nc_dataset.geospatial_lon_min = res_meta_cov.value['westlimit']
            nc_dataset.geospatial_lon_max = res_meta_cov.value['eastlimit']

        if 'contributor' in meta_elements and res.metadata.contributors.all():
            res_contri_name = []
            for contributor in res.metadata.contributors.all():
                res_contri_name.append(contributor.name) # name, email, homepage, id
            nc_dataset.contributor_name = ', '.join(res_contri_name)

        if 'creator' in meta_elements and res.metadata.creators.all().filter(order=1):
            creator = res.metadata.creators.all().filter(order=1).first()
            nc_dataset.creator_name = creator.name
            if creator.email:
                nc_dataset.creator_email = creator.email
            if creator.description or creator.homepage:
                nc_dataset.creator_url = creator.homepage if creator.homepage else creator.description

        # edit convention meta if ACDD terms are edited in file:
        if meta_elements:
            ori_con = nc_dataset.Conventions if hasattr(nc_dataset, "Conventions") else ''
            if not ori_con:
                nc_dataset.Conventions = "ACDD-1.3"
            elif "ACDD" not in ori_con:
                nc_dataset.Conventions = ', '.join(ori_con.split(',')+["ACDD-1.3"])

        # close nc_dataset
        nc_dataset.close()

    except:
        nc_tools_obj = NetcdfTools.objects.filter(short_id=res.short_id).first()
        if nc_tools_obj:
            nc_tools_obj.meta_edit_file.delete()
        check_info = "Error! Metadata Editing: failed to edit the meta info in the .nc file."

    return check_info
