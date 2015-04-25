"""
Module data subset in for .nc file in netcdf resource

"""
from collections import OrderedDict
from django.forms.formsets import formset_factory
from hs_app_tools_netCDF.forms import DimensionForm, VariableNamesForm
from hs_app_netCDF.nc_functions.nc_utils import get_nc_dataset, get_nc_data_variables
from hs_core.models import ResourceFile
from hs_app_tools_netCDF.nc_tool_functions.nc_tools_utils import *


# functions for data subset tool frontend ###############################################################

def create_dimension_formset(nc_res):
    """
    create formset for dimension form in data subset tool

    :param nc_res: netcdf resource object
    :return: dimension formset with initial values for each form
    """

    # get the dimensions info
    nc_file_path = get_nc_file_path_from_res(nc_res)
    dimensions_info = get_dimensions_info(nc_file_path)

    # create the formset context
    if dimensions_info:
        # create form initial values:
        initial_value = []
        for dim_name, dim_subset_value in dimensions_info.items():
            initial_value.append({"dim_subset_value": dim_subset_value,
                            "dim_name": dim_name
                })

        # create formset with initial values
        form_num = len(dimensions_info)
        formset = formset_factory(DimensionForm, extra=form_num, max_num=form_num)
        dimension_formset = formset(initial=initial_value)

    else:
        dimension_formset = None

    return dimension_formset


def get_dimensions_info(nc_file_path):
    """
    create the dimensions information ordered dict with given netcdf file path

    :param nc_file_path: netcdf file path which can be recognized by the system
    :return: dictionary including the dimensions information which is {dim_name: dime length}
    """

    nc_dataset = get_nc_dataset(nc_file_path)
    dimension_info = OrderedDict()

    if nc_dataset:
        for dim_name, dim_obj in nc_dataset.dimensions.items():
            name = "{0} (length={1})".format(dim_name, len(dim_obj))
            value = "0:1:{0}".format(str(len(dim_obj)-1))
            dimension_info[name] = value

    return dimension_info


def create_variable_names_form(nc_res):
    """
    create form for variable form in data subset tool

    :param nc_res : netcdf resource object
    :return: variable form context
    """

    # get the variable names info:
    nc_file_path = get_nc_file_path_from_res(nc_res)
    variable_names_info = get_variable_names_info(nc_file_path)

    # create the variable names form
    if variable_names_info:
        variable_names_form = VariableNamesForm()
        variable_names_form.fields['variable_names'].choices = variable_names_info
    else:
        variable_names_form= None

    return variable_names_form


def get_variable_names_info(nc_file_path):
    """
    create the variable names with shape information ordered dict with given netcdf file path

    :param nc_file_path: netcdf file path which can be recognized by the system
    :return: dictionary including the dimensions information which is {var_name: var_name(dim1,dim2)}
    """

    nc_dataset = get_nc_dataset(nc_file_path)
    variable_names_info = []

    if nc_dataset:
        nc_data_variables = get_nc_data_variables(nc_dataset)
        for var_name, var_obj in nc_data_variables.items():
            choice_backend = var_name
            shape_list = [str(x) for x in var_obj.dimensions]
            choice_frontend = "{0} ({1})".format(var_name, ', '.join(shape_list))
            variable_names_info.append((choice_backend, choice_frontend))

    return variable_names_info
