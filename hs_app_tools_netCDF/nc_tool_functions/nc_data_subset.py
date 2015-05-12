"""
Module data subset for .nc file in netcdf resource

"""
from collections import OrderedDict
from django.forms.formsets import formset_factory
from hs_app_tools_netCDF.forms import DimensionForm, VariableNamesForm, DataInspectorForm
from hs_app_netCDF.nc_functions.nc_utils import get_nc_dataset, get_nc_data_variables, get_nc_variable_data
from hs_core.models import ResourceFile
from hs_app_tools_netCDF.nc_tool_functions.nc_tools_utils import *
from hs_app_netCDF.models import NetcdfResource


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
        variable_names_form = None

    return variable_names_form


def get_variable_names_info(nc_file_path):
    """
    get the variable names with shape information ordered dict with given netcdf file path

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


# functions for data subset tool backend #####################################################################
def run_data_subset_tool(request, shortkey):
    """
    Run data subset function for netcdf resource file based on the request data subset form information

    :param request:
    :return: execute_info as list to show if there is an error or success for running the tool. ['error', 'error info detail']
    """

    res, res_cls = get_res_and_class(request, shortkey)
    file_process = request.POST.getlist('file_process')

    if res_cls is NetcdfResource:

        # run data subset info check
        data_subset_form_info = get_data_subset_form_info(request)
        execute_info = run_data_subset_info_check(data_subset_form_info)

        # run data subset for .nc file
        if execute_info[0] == 'success':
            # initiate the nc_tools_obj
            nc_tools_obj = create_nc_tools_obj(res, 'data_subset')

            # run nco for data subset
            if nc_tools_obj:
                # create nco command
                nc_file_path = nc_tools_obj.data_subset_file.file.name
                data_subset_nco_cmd = create_data_subset_nco_cmd(data_subset_form_info, nc_file_path)

                # run nco command
                execute_info = run_nco_data_subset(data_subset_nco_cmd)

        # run file process
        if execute_info[0] == 'success':
            check_info = execute_file_process(res, file_process, nc_file_path, request)
            if check_info:
                execute_info = ['error', check_info]
            else:
                execute_info = ['success', 'Success! Data subset is finished']

        # delete tool obj after tool run
        nc_tools_obj = NetcdfTools.objects.filter(short_id=res.short_id).first()
        if nc_tools_obj:
            nc_tools_obj.delete()

    else:
        execute_info = ['error', 'please check if this is a Multidimentional NetCDF resource.']

    return execute_info


def get_data_subset_form_info(request):
    data_subset_form_info = {}

    if request.method == 'POST':
        formset = formset_factory(DimensionForm)
        dim_formset = formset(request.POST)

        # get variable info
        data_subset_form_info['variable_info'] = request.POST.getlist('variable_names')

        # get dimension info
        data_subset_form_info['dimension_info'] = {}
        if dim_formset.is_valid():
            for form in dim_formset:
                form_clean_data = form.cleaned_data
                data_subset_form_info['dimension_info'][form_clean_data['dim_name']] = form_clean_data['dim_subset_value']

        # refine dimension info
        raw_info = data_subset_form_info['dimension_info']
        if raw_info:
            data_subset_form_info['dimension_info'] = refine_data_subset_form_dimension_info(raw_info)

    return data_subset_form_info


def refine_data_subset_form_dimension_info(data_subset_dimension_info, pattern=['start', 'step', 'end']):
    for form_dim_name, form_dim_subset_value in data_subset_dimension_info.items():
        dim_name = ''.join(list(form_dim_name)[:form_dim_name.index('(')])

        # rearrange the index sequence and convert as integer value
        try:
            dim_subset_value = [int(x) for x in form_dim_subset_value.split(':')]
            dim_subset_value = [dim_subset_value[pattern.index('start')],
                                dim_subset_value[pattern.index('end')],
                                dim_subset_value[pattern.index('step')]
                                ]
        except:
            dim_subset_value = []

        del data_subset_dimension_info[form_dim_name]

        # validate the index value
        dim_length = int(form_dim_name[form_dim_name.find("=")+1:form_dim_name.find(")")])
        if dim_subset_value:
            if (dim_subset_value[1] >= dim_length) or (dim_subset_value[0] > dim_subset_value[1]):
                dim_subset_value = []
            elif dim_subset_value[0] == 0 and dim_subset_value[1] == dim_length and dim_subset_value[2] == 1:
                continue

        # assign the refined dim info
        data_subset_dimension_info[dim_name] = dim_subset_value

    return data_subset_dimension_info


def run_data_subset_info_check(data_subset_form_info):
    if data_subset_form_info['dimension_info'] and data_subset_form_info['variable_info']:
        error_dim_info = []
        for dim_name, dim_subset_value in data_subset_form_info['dimension_info'].items():
            if not dim_subset_value:
                error_dim_info.append(dim_name)

        if error_dim_info:
            execute_info = ['error',
                             'please provide correct dimension subset index for: {0}'.format(', '.join(error_dim_info))]
        else:
            execute_info = ['success']

    else:
        execute_info = ['error', 'please complete the required dimension and variable information. ']

    return execute_info


def create_data_subset_nco_cmd(data_subset_form_info, nc_file_path):
    pass



def run_nco_data_subset(data_subset_cmd):
    execute_info = ['success']
    return execute_info