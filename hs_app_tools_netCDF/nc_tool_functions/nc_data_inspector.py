"""
Module variable inspector for .nc file in netcdf resource

"""

from collections import OrderedDict
from hs_app_tools_netCDF.forms import DataInspectorForm
from hs_app_netCDF.nc_functions.nc_utils import get_nc_dataset, get_nc_variable, get_nc_variable_data, get_nc_variable_attr
from hs_core.models import ResourceFile
from hs_app_tools_netCDF.nc_tool_functions.nc_tools_utils import *


# Functions for frontend ###############################################################################################3
def create_data_inspector_form(nc_res):
    """
    create form for data inspector tool

    :param res: netcdf resource obj
    :return: data inspector form with all the variable names information
    """

    # get the variable names info:
    nc_file_path = get_nc_file_path_from_res(nc_res)
    var_names_info = get_var_names_info(nc_file_path)

    # create the data inspector initial form
    if var_names_info:
        data_inspector_form = DataInspectorForm()
        var_names_choices = [(n, v) for n, v in var_names_info.iteritems()]
        data_inspector_form.fields['var_name'].choices = var_names_choices
    else:
        data_inspector_form = None

    return data_inspector_form


def get_var_names_info(nc_file_path):
    """
    get the all the variable names with dimension information from netcdf file

    :param nc_file_path: netcdf file path which can be recognized by the system
    :return: dictionary including the coordinate and auxiliary coordinate variable names information which is {var_name: var_name(dim1,dim2)}
    """

    nc_dataset = get_nc_dataset(nc_file_path)
    var_names_info = OrderedDict()

    if nc_dataset:
        var_dict = nc_dataset.variables
        for var_name, var_obj in var_dict.items():
            shape_list = [str(x) for x in var_obj.dimensions]
            value = "{0} ({1})".format(var_name, ', '.join(shape_list))
            var_names_info[var_name] = value

    return var_names_info


# Functions for Backend ###########################################################################################

def get_data_inspector_info(nc_file_path, var_name):
    """
    get the variable attributes and data information for the data inspector tool

    :param nc_file_path: netcdf file path which can be recognized by the system
    :param var_name: variable name to get the info
    :return:
    """

    nc_dataset = get_nc_dataset(nc_file_path)
    data_inspector_info = {}

    if nc_dataset:
        var_data_info = get_var_data_info(nc_dataset, var_name)
        var_attr_info = get_var_attr_info(nc_dataset, var_name)
        data_inspector_info = {'var_data': var_data_info,
                               'var_attr': var_attr_info,
        }

    return data_inspector_info


def get_var_data_info(nc_dataset, var_name):
    """
    get the variable data information for the data inspector tool

    :param nc_dataset:
    :param var_name:
    :return: string including data information
    """
    var_data = get_nc_variable_data(nc_dataset, var_name,time_convert=True)

    if var_data is not None:
        import numpy
        numpy.set_printoptions(threshold=50000, edgeitems=500)  # set the numpy string representation format
        var_data_info = '{0}'.format(numpy.array_str(var_data))

    else:
        var_data_info = 'No data is defined for this variable.'

    return var_data_info


def get_var_attr_info(nc_dataset, var_name):
    """
    get the variable attributes information for data inspector tool

    :param nc_dataset:
    :param var_name:
    :return: string including attributes information
    """

    var_attr = get_nc_variable_attr(nc_dataset, var_name)
    var_attr_info = []

    if var_attr:
        for attr_name, attr_info in var_attr.items():
            var_attr_info.append('{0} : {1}'.format(attr_name, attr_info))
        var_attr_info = '\n'.join(var_attr_info)
    else:
        var_attr_info = 'No attribute information is defined for the variable.'

    return var_attr_info