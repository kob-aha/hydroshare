"""
Module edit meta data in netcdf resource file based on the resource metadata information

"""
import numpy as np
import netCDF4
from hs_app_tools_netCDF.nc_tool_functions.nc_tools_utils import *



def run_meta_edit_tool(res, meta_elements, file_process, request):

    check_info = ''

    # initiate the nc_tools_obj of nc resource for meta edit tool
    tool_name = 'meta_edit'
    nc_tools_obj = create_nc_tools_obj(res, tool_name)

    if nc_tools_obj:
        # write meta in the file
        nc_file_path = nc_tools_obj.meta_edit_file.file.name
        check_info = edit_meta_in_file(res, meta_elements, nc_file_path)

        # file process after writing meta
        if (not check_info) and file_process:
            check_info = execute_file_process(res, file_process, nc_file_path, request)
    else:
        check_info = "there is no .nc file in the resource. "

    # delete tool obj after function run
    nc_tools_obj.delete()

    return check_info


def edit_meta_in_file(res, meta_elements, nc_file_path):
    """
    Function to edit the netcdf file with meta data info in the netcdf resource.

    :param res:  netcdf resource obj
    :param nc_file_path:  netcdf file path of the file stored in system
    :param meta_elements:  core and extended meta terms for netcdf resource obj
    :return: check_info:  if success return '', otherwise return error info string
    """
    check_info = ''
    try:
        # edit metadata elements
        nc_dataset = netCDF4.Dataset(nc_file_path, 'a')

        if 'title' in meta_elements and (res.metadata.title.value != 'Untitled Resource'):
            nc_dataset.title = res.metadata.title.value

        if 'description' in meta_elements and res.metadata.description:
            nc_dataset.summary = res.metadata.description.abstract

        if 'subjects' in meta_elements and res.metadata.subjects.all().first():
            res_meta_subjects = []
            for res_subject in res.metadata.subjects.all():
                res_meta_subjects.append(res_subject.value)
            nc_dataset.keywords = ','.join(res_meta_subjects)

        if 'rights' in meta_elements and res.metadata.rights:
            nc_dataset.license = "{0} {1}".format(res.metadata.rights.statement, res.metadata.rights.url)

        if 'publisher' in meta_elements: #TODO need to confirm this info
            nc_dataset.publisher_name = 'HydroShare'
            nc_dataset.publisher_url = 'http://www.hydroshare.org'

        if 'identifier' in meta_elements and res.metadata.identifiers.all(): # TODO need to confirm this info
            if res.metadata.identifiers.all().filter(name="doi"):
                res_identifier = res.metadata.identifiers.all().filter(name="doi")[0]
            else:
                res_identifier = res.metadata.identifiers.all().filter(name="hydroShareIdentifier")[0]
            nc_dataset.id = res_identifier.url

        if 'source' in meta_elements and res.metadata.sources.all():
            res_meta_source = []
            for source in res.metadata.sources.all():
                res_meta_source.append(source.derived_from)
            nc_dataset.source = ' \n'.join(res_meta_source)

        if 'relation' in meta_elements and res.metadata.relations.all().filter(type='cites'):
            res_meta_ref = []
            for reference in res.metadata.relations.all().filter(type='cites'):
                res_meta_ref.append(reference.value)
            nc_dataset.references = ' \n'.join(res_meta_ref)

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
                res_contri_name.append(contributor.name)
            nc_dataset.contributor_name = ', '.join(res_contri_name)

        if 'creator' in meta_elements and res.metadata.creators.all().filter(order=1):
            creator = res.metadata.creators.all().filter(order=1).first() #TODO: need to make sure of this info
            nc_dataset.creator_name = creator.name
            if creator.email:
                nc_dataset.creator_email = creator.email
            if creator.description or creator.homepage:
                nc_dataset.creator_url = creator.homepage if creator.homepage else creator.description

        if 'variable' in meta_elements and res.metadata.variables.all():
        #TODO: need to change the variable form name (method-comment, descriptive name- long name)
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
        # clear the file fields and delete the file
        nc_tools_obj = NetcdfTools.objects.filter(short_id=res.short_id).first()
        if nc_tools_obj and nc_tools_obj.meta_edit_file:
            storage, path = nc_tools_obj.meta_edit_file.storage, nc_tools_obj.meta_edit_file.path
            nc_tools_obj.meta_edit_file.delete()
            storage.delete(path)

        check_info = "failed to edit the meta info in the .nc file."

    return check_info


