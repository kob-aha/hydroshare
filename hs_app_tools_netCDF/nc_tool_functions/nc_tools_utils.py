"""
Module providing utility functions to support netcdf tools function
"""

from hs_core.hydroshare.resource import ResourceFile
from hs_app_tools_netCDF.models import *
from django.core.files import File
from django.core.files.uploadedfile import InMemoryUploadedFile
import StringIO, os
from hs_core import hydroshare
from hs_core.hydroshare import utils
from django.core.files import File
import uuid


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


def execute_file_process(res, file_process, nc_file_path):
    """
    create a new version of resource or a new resource with given netcdf file

    :param res: netcdf resource obj
    :param nc_file_path: full file path name of the .nc file, this needs to be the file path accessible by system
    :param file_process: list including the options of the file processing e.g. ['new_ver_res', 'new_res']
    :return:
    """
    check_info = []
    if 'new_ver_res' in file_process:
        check_info.append(create_new_ver_res(res, nc_file_path))

    if 'new_res' in file_process:
        check_info.append(create_new_res(res, nc_file_path))

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

    try:
        # add new .nc file
        f = ResourceFile.objects.create(content_object=res)
        if not nc_file_name:
            nc_file_name = os.path.basename(nc_file_path)
            if '.nc' not in nc_file_name:
                nc_file_name.append('.nc')

        nc_file = open(nc_file_path)
        f.resource_file.save(nc_file_name, File(nc_file))

        # add new ncdump .txt file
        check_info = add_nc_dump_file(res, nc_file_path, nc_file_name)

        # delete resource files based on execution
        new_res_file_name = os.path.basename(f.resource_file.name)
        if not check_info:
            for f in ResourceFile.objects.filter(object_id=res.id):
                if new_res_file_name.replace('.nc', '') not in f.resource_file.name:
                    f.resource_file.delete()
                    f.delete()
        else:
            for f in ResourceFile.objects.filter(object_id=res.id):
                if new_res_file_name.replace('.nc', '') in f.resource_file.name:
                    f.resource_file.delete()
                    f.delete()

    except:
        for f in ResourceFile.objects.filter(object_id=res.id):
            if not f.resource_file:
                f.delete()
        check_info = "failed to create new version of resource"

    return check_info


def add_nc_dump_file(res, nc_file_path, nc_file_name=None):
    """
    create ncdump info .txt file and add file to netCDF resource

    :param res: netcdf resource object
    :param nc_file_path: full file path name of the .nc file, this needs to be the file path accessible by system
    :param nc_file_name: a meaningful name of the netcdf file which will be shown as the resource file name 'XXX.nc'
    :return: check_info: if success return '', otherwise return error info string
    """
    check_info = ''

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
            hydroshare.add_resource_files(res.short_id, dump_file)

            # add file format for text file
            file_format_type = utils.get_file_mime_type(dump_file_name)
            if file_format_type not in [mime.value for mime in res.metadata.formats.all()]:
                res.metadata.create_element('format', value=file_format_type)

    except:
        check_info = "failed to create the ncdump file"

    return check_info


def create_new_res(nc_tools_obj):
    check_info = ''

    return check_info