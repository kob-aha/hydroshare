"""
Module providing utility functions to support netcdf tools function
"""

from hs_core.hydroshare.resource import ResourceFile
from django.core.files import File
from django.core.files.uploadedfile import InMemoryUploadedFile
import StringIO, os
from hs_core import hydroshare
from hs_core.hydroshare import utils
from django.core.files import File
import uuid
from hs_app_tools_netCDF.models import *
import hs_app_netCDF.nc_functions.nc_meta as nc_meta
import netCDF4


def create_nc_tools_obj(res, tool_name):
    """
    create the netcdf tool obj and add netcdf file to the the tool file field

    :param res: netcdf resource obj
    :param tool_name: string name of the netcdf tools refer to NetcdfTool class field(e.g.: meta_edit)
    :return: netcdf tool object with the original netcdf file stored in the tool file field
    """

    for f in ResourceFile.objects.filter(object_id=res.id):
        ext = os.path.splitext(f.resource_file.name)[-1]
        if ext == '.nc':

            # initiate the nc_tools_obj and tool_file_filed for the resource
            nc_tools_obj = NetcdfTools.objects.filter(short_id=res.short_id).first()
            tool_file_field_name = tool_name+'_file'
            if nc_tools_obj and getattr(nc_tools_obj, tool_file_field_name):
                tool_file_field = getattr(nc_tools_obj, tool_file_field_name)
                storage, path = tool_file_field.storage, tool_file_field.path
                tool_file_field.delete()
                storage.delete(path)
            else:
                nc_tools_obj = NetcdfTools(short_id=res.short_id)

            # add initial netcdf file name for the tool file field
            res_nc_file_name = os.path.basename(f.resource_file.name).split('_')
            random = str(uuid.uuid4())[0:6]
            if 'HS' in res_nc_file_name[0] and len(res_nc_file_name[0]) == 8:
                tool_file_name = '_'.join(['HS'+random]+res_nc_file_name[1:])
            else:
                tool_file_name = '_'.join(['HS'+random]+res_nc_file_name)

            # add netcdf file to tool file field
            res_nc_file = open(f.resource_file.file.name)  # ContentFile(f.resource_file.file.read())
            tool_file_field = getattr(nc_tools_obj, tool_file_field_name)
            tool_file_field.save(tool_file_name, File(res_nc_file))

            return nc_tools_obj

    return None


def execute_file_process(res, file_process, nc_file_path, request=None):
    """
    create a new version of resource or a new resource with given netcdf file

    :param res: netcdf resource obj
    :param nc_file_path: full file path name of the .nc file, this needs to be the file path accessible by system
    :param file_process: list including the options of the file processing e.g. ['new_ver_res', 'new_res']
    :param request: request obj
    :return:
    """
    check_info = []

    if 'new_ver_res' in file_process:
        check_info.append(create_new_ver_res(res, nc_file_path))

    if 'new_res' in file_process and request:
        check_info.append(create_new_res(request, nc_file_path))

    check_info = ' and '.join(filter(None, check_info))

    return check_info


def create_new_ver_res(res, nc_file_path, nc_file_name=None):
    """
    create a new version of resource with the given netcdf file path

    :param res: netcdf resource obj
    :param nc_file_path: full file path name of the .nc file, this needs to be the file path accessible by system
    :param nc_file_name: a meaningful name of the netcdf file which will be shown as the resource file name(optional)
    :return: check_info: if success return '', otherwise return error info string
    """

    # add netcdf file to resource
    nc_res_file_obj = add_nc_file_to_res(res, nc_file_path, nc_file_name=None)

    # add ncdump .txt file to resource
    ncdump_res_file_obj = add_ncdump_file_to_res(res, nc_file_path, nc_file_name=None)

    # delete old resource file objs
    if nc_res_file_obj and ncdump_res_file_obj:
        check_info = ''
        new_res_file_name = os.path.basename(nc_res_file_obj.resource_file.name)
        for f in ResourceFile.objects.filter(object_id=res.id):
            if new_res_file_name.replace('.nc', '') not in f.resource_file.name:
                f.resource_file.delete()
                f.delete()
    else:
        if nc_res_file_obj:
            nc_res_file_obj.resource_file.delete()
            nc_res_file_obj.delete()
        if ncdump_res_file_obj:
            ncdump_res_file_obj.resource_file.delete()
            ncdump_res_file_obj.delete()

        check_info = 'failed to create new version of resource'

    return check_info


def create_new_res(request, nc_file_path):
    """
    create a new resource with given netcdf file

    :param request: request obj
    :param nc_file_path: full file path name of the .nc file, this needs to be the file path accessible by system
    :return: check_info if success return '', otherwise error info
    """

    if hasattr(request, 'user'):
        check_info = ''

        # get the nc meta populate list
        nc_file_name = os.path.basename(nc_file_path)
        metadata = get_nc_meta_populate_list(nc_file_path, nc_file_name)

        # create new resource
        res = hydroshare.create_resource(
                    resource_type='NetcdfResource',
                    owner=request.user,
                    title=nc_file_name,
                    keywords=None,
                    metadata=metadata,
                    files=(),
                    content=nc_file_name,
        )

        # add new .nc file and check identifier info
        meta_elements = request.POST.getlist('meta_elements')
        if 'identifier' in meta_elements and res.metadata.identifiers.all():
            res_identifier = res.metadata.identifiers.all().filter(name="hydroShareIdentifier")[0]
        nc_dataset = netCDF4.Dataset(nc_file_path, 'a')
        a = nc_dataset.id
        b = res_identifier.url
        a == b
        nc_dataset.setncattr('id', res_identifier.url)
        nc_dataset.close()
        nc_res_file_obj =add_nc_file_to_res(res, nc_file_path, nc_file_name)

        # add new ncdump file
        ncdump_res_file_obj = add_ncdump_file_to_res(res,nc_file_path, nc_file_name)

        # check info:
        if nc_res_file_obj and ncdump_res_file_obj:
            check_info = ''

        else:
            hydroshare.delete_resource(res.short_id)
            check_info = 'failed to create a new resource'

    else:
        check_info = 'failed to create a new resource'

    return check_info


def add_nc_file_to_res(res, nc_file_path, nc_file_name=None):
    """
    add netcdf .nc file to resource

    :param res: netcdf resource obj
    :param nc_file_path: full file path name of the .nc file, this needs to be the file path accessible by system
    :param nc_file_name: a meaningful name of the netcdf file which will be shown as the resource file name 'XXX.nc'
    :return: if success returns resource file obj for the netcdf file, otherwise none

    """

    try:
        f = ResourceFile.objects.create(content_object=res)
        if not nc_file_name:
            nc_file_name = os.path.basename(nc_file_path)
            if '.nc' not in nc_file_name:
                nc_file_name.append('.nc')

        nc_file = open(nc_file_path)
        f.resource_file.save(nc_file_name, File(nc_file))

    except:
        for f in ResourceFile.objects.filter(object_id=res.id):
            if not f.resource_file:
                f.delete()
        f = None

    return f


def add_ncdump_file_to_res(res, nc_file_path, nc_file_name=None):
    """
    create ncdump info .txt file and add file to netCDF resource

    :param res: netcdf resource object
    :param nc_file_path: full file path name of the .nc file, this needs to be the file path accessible by system
    :param nc_file_name: a meaningful name of the netcdf file which will be shown as the resource file name 'XXX.nc'
    :return: if success returns resource file obj for the netcdf ncdump file, otherwise none
    """

    try:
        import hs_app_netCDF.nc_functions.nc_dump as nc_dump

        # get nc_file_name
        if not nc_file_name:
            nc_file_name = os.path.basename(nc_file_path)

        # get ncdump string
        if nc_dump.get_nc_dump_string_by_ncdump(nc_file_path):
            dump_str = nc_dump.get_nc_dump_string_by_ncdump(nc_file_path)
        else:
            dump_str = nc_dump.get_nc_dump_string(nc_file_path)

        # create InMemoryUploadedFile text file to store the dump info and add it to resource
        if dump_str:
            # refine dump_str first line
            first_line = list('netcdf {0} '.format(nc_file_name.replace('.nc', '')))
            first_line_index = dump_str.index('{')
            dump_str_list = first_line + list(dump_str)[first_line_index:]
            dump_str = "".join(dump_str_list)

            # write dump_str to temporary file
            io = StringIO.StringIO()
            io.write(dump_str)
            dump_file_name = nc_file_name.replace('.nc', '')+'_header_info.txt'
            dump_file = InMemoryUploadedFile(io, None, dump_file_name, 'text', io.len, None)
            dump_file.seek(0)

            # add file as resource file obj
            f = ResourceFile.objects.create(content_object=res)
            f.resource_file.save(dump_file_name, File(dump_file))

            # add file format for text file
            file_format_type = utils.get_file_mime_type(dump_file_name)
            if file_format_type not in [mime.value for mime in res.metadata.formats.all()]:
                res.metadata.create_element('format', value=file_format_type)

    except:
        for f in ResourceFile.objects.filter(object_id=res.id):
            if not f.resource_file:
                f.delete()
        f = None

    return f


def get_nc_meta_populate_list(nc_file_path, nc_res_title="Untitled resource"):
    """
    extract meta info from .nc file and create the meta populate list

    :param nc_file_path:
    :return: meta data list for prepopulating the metadata info
    """

    metadata = []

    # add meta default info
    metadata.append({'rights':
                     {'statement': 'This resource is shared under the Creative Commons Attribution CC BY.',
                      'url': 'http://creativecommons.org/licenses/by/4.0/'
                     }
                })
    metadata.append({'title': {'value': nc_res_title}})

    # extract the metadata from netcdf file

    try:
        res_md_dict = nc_meta.get_nc_meta_dict(nc_file_path)
        res_dublin_core_meta = res_md_dict['dublin_core_meta']
        res_type_specific_meta = res_md_dict['type_specific_meta']
    except:
        res_dublin_core_meta = {}
        res_type_specific_meta = {}

    # add title
    if res_dublin_core_meta.get('title'):
        if nc_res_title == 'Untitled resource':
            title = {'title': {'value': res_dublin_core_meta['title']}}
            metadata.append(title)
    # add description
    if res_dublin_core_meta.get('description'):
        description = {'description': {'abstract': res_dublin_core_meta['description']}}
        metadata.append(description)
    # add source
    if res_dublin_core_meta.get('source'):
        source = {'source': {'derived_from': res_dublin_core_meta['source']}}
        metadata.append(source)
    # add relation
    if res_dublin_core_meta.get('references'):
        relation = {'relation': {'type': 'cites', 'value': res_dublin_core_meta['references']}}
        metadata.append(relation)
    # add coverage - period
    if res_dublin_core_meta.get('period'):
        period = {'coverage': {'type': 'period', 'value': res_dublin_core_meta['period']}}
        metadata.append(period)
    # add coverage - box
    if res_dublin_core_meta.get('box'):
        box = {'coverage': {'type': 'box', 'value': res_dublin_core_meta['box']}}
        metadata.append(box)

    # Save extended meta to metadata variable
    for var_name, var_meta in res_type_specific_meta.items():
        meta_info = {}
        for element, value in var_meta.items():
            if value != '':
                meta_info[element] = value
        metadata.append({'variable': meta_info})

    # Save extended meta to original spatial coverage
    if res_dublin_core_meta.get('original-box'):
        if res_dublin_core_meta.get('projection-info'):
            ori_cov = {'originalcoverage': {'value': res_dublin_core_meta['original-box'],
                                            'projection_string_type': res_dublin_core_meta['projection-info']['type'],
                                            'projection_string_text': res_dublin_core_meta['projection-info']['text']}}
        else:
            ori_cov = {'originalcoverage': {'value': res_dublin_core_meta['original-box']}}

        metadata.append(ori_cov)
    return metadata


