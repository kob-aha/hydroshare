"""
Module provides utility functions to manipulate netCDF dataset.
- classify variable types of coordinate, coordinate bounds, grid mapping, scientific data, auxiliary coordinate
- show original metadata of a variable

Reference code
http://netcdf4-python.googlecode.com/svn/trunk/docs/netCDF4-module.html
"""
__author__ = 'Tian Gan'


import netCDF4
import re
from collections import OrderedDict


# Functions for General Purpose ####################################################################################
def get_nc_dataset(nc_file_name):
    """
    (string)-> object

    Return: the netCDF dataset
    """

    nc_dataset = netCDF4.Dataset(nc_file_name, 'r')
    return nc_dataset


def get_nc_variable_original_meta(nc_dataset, nc_variable_name):
    """
    (object, string)-> OrderedDict

    Return: netCDF variable original metadata information defined in the netCDF file
    """

    nc_variable = nc_dataset.variables[nc_variable_name]

    nc_variable_original_meta = OrderedDict([('dimension', str(nc_variable.dimensions)),
                                             ('shape', str(nc_variable.shape)),
                                             ('data_type', str(nc_variable.dtype))])

    for key, value in nc_variable.__dict__.items():
        nc_variable_original_meta[key] = str(value)

    return nc_variable_original_meta


def get_nc_variable_dimensions_detail(nc_file_name, nc_variable_name):
    """
    (string, string)-> dict

    Return: netCDF variable's dimension info which shows the dimension name, unit, and dimension values
    """

    nc_dataset = get_nc_dataset(nc_file_name)
    nc_variable = nc_dataset.variables[nc_variable_name]
    nc_variable_dimension_namelist = list(nc_variable.dimensions)
    nc_variable_dimensions_detail = {}
    for name in nc_variable_dimension_namelist:
        nc_variable_dimensions_detail[name] = get_nc_coordinate_variable_info(nc_dataset, name)

    return nc_variable_dimensions_detail


def get_nc_variable_dimensions_mapping(nc_dataset, nc_variable_name):
    """
    (object,string) -> dict

    Return: assign X,Y,Z,T to all the dimensions for the variables.
    If the type is not discerned, Unknown is assigned to that coordinate variable
    """

    nc_variable = nc_dataset.variables[nc_variable_name]
    nc_variable_dimension_namelist = list(nc_variable.dimensions)
    nc_variable_dimensions_mapping = OrderedDict([])
    for dim_name in nc_variable_dimension_namelist:
        nc_coordinate_variable = nc_dataset.variables[dim_name]
        nc_variable_dimensions_mapping[dim_name] = get_coordinate_variable_type(nc_coordinate_variable)

    return nc_variable_dimensions_mapping


# Functions for Coordinate Variable##############################################################################
def get_nc_coordinate_variables(nc_dataset):
    """
    (object)-> dict

    Return netCDF coordinate variable
    """

    nc_all_variables = nc_dataset.variables
    nc_dimensions = nc_dataset.dimensions.keys()
    nc_coordinate_variables = {}
    for var_name, var_obj in nc_all_variables.items():
        if len(var_obj.shape) == 1 and var_obj.dimensions[0]in nc_dimensions:
            nc_coordinate_variables[var_name] = nc_dataset.variables[var_name]

    return nc_coordinate_variables


def get_nc_coordinate_variable_namelist(nc_dataset):
    """
    (object)-> list

    Return netCDF coordinate variable names
    """
    nc_coordinate_variables = get_nc_coordinate_variables(nc_dataset)
    nc_coordinate_variable_namelist = nc_coordinate_variables.keys()

    return nc_coordinate_variable_namelist


def get_nc_coordinate_variables_mapping(nc_dataset):
    """
    (object)-> dict

    Return: assign X,Y,Z,T to all the coordinate variables in netCDF.
    If the type is not discerned, Unknown is assigned to that coordinate variable
    """
    nc_coordinate_variables = get_nc_coordinate_variables(nc_dataset)
    nc_coordinate_variables_mapping = {}
    for var_name, var_obj in nc_coordinate_variables.items():
        nc_coordinate_variables_mapping[var_name] = get_coordinate_variable_type(var_obj)

    return nc_coordinate_variables_mapping


def get_coordinate_variable_type(nc_variable):
    """
    (object)-> string

    Return: One of X, Y, Z, T is assigned to given coordinate variable.
            If not discerned as X, Y, Z, T, Unknown is returned
    """

    if hasattr(nc_variable, 'axis'):
        return nc_variable.axis

    nc_variable_standard_name = getattr(nc_variable, 'standard_name', getattr(nc_variable, 'long_name', None))
    if nc_variable_standard_name:
        compare_dict = {
            u'latitude': u'Y',
            u'longitude': u'X',
            u'time': u'T',
            u'projection_x_coordinate': u'X',
            u'projection_y_coordinate': u'Y'
        }
        for standard_name, coor_type in compare_dict.items():
            if re.match(nc_variable_standard_name, standard_name, re.I):
                return coor_type

    if hasattr(nc_variable, 'positive'):
        return u'Z'

    return 'Unknown'


def get_nc_coordinate_variables_detail(nc_dataset):
    """
    (string) -> dict

    Return: coordinate metadata and data for all the netCDF coordinate variables
    """

    nc_coordinate_variable_namelist = get_nc_coordinate_variable_namelist(nc_dataset)
    nc_coordinate_variables_detail = {}
    for nc_coordinate_variable_name in nc_coordinate_variable_namelist:
        nc_coordinate_variables_detail[nc_coordinate_variable_name] = \
            get_nc_coordinate_variable_info(nc_dataset, nc_coordinate_variable_name)

    return nc_coordinate_variables_detail


def get_nc_coordinate_variable_info(nc_dataset, nc_coordinate_variable_name):
    """
    (object, string) -> dict

    Return: coordinate metadata and data for the given netCDF coordinate variable
    """

    nc_coordinate_variable = nc_dataset.variables[nc_coordinate_variable_name]
    coordinate_data = nc_coordinate_variable[:].tolist()
    coordinate_type = get_coordinate_variable_type(nc_coordinate_variable)

    if coordinate_type == 'T' and hasattr(nc_coordinate_variable, 'units'):
        nc_time_calendar = nc_coordinate_variable.calendar if hasattr(nc_coordinate_variable, 'calendar') else 'standard'
        for i in range(len(coordinate_data)):
            coordinate_data[i] = str(netCDF4.num2date(coordinate_data[i],
                                                      units=nc_coordinate_variable.units,
                                                      calendar=nc_time_calendar))

    nc_coordinate_variable_info = {
        'coordinate_type': coordinate_type,
        'coordinate_units': nc_coordinate_variable.units if hasattr(nc_coordinate_variable, 'units') else '',
        'coordinate_data': coordinate_data,
        'coordinate_start': coordinate_data[0],
        'coordinate_end': coordinate_data[-1],
        'coordinate_size': len(coordinate_data)
    }

    return nc_coordinate_variable_info


# Functions for Coordinate Bound Variable ###########################################################################
def get_nc_coordinate_bounds_variables(nc_dataset):
    """
    (object) -> dict

    Return: the netCDF coordinate bound variable
    """

    nc_coordinate_variables = get_nc_coordinate_variables(nc_dataset)
    nc_coordinate_bound_variables = {}
    for var_name, var_obj in nc_coordinate_variables.items():
        if hasattr(var_obj, 'bounds') and nc_dataset.variables.get(var_obj.bounds, None):
            nc_coordinate_bound_variables[var_obj.bounds] = nc_dataset.variables[var_obj.bounds]

    return nc_coordinate_bound_variables


def get_nc_coordinate_bounds_variable_namelist(nc_dataset):
    """
    (object) -> list

    Return: the netCDF coordinate bound variable names
    """

    nc_coordinate_bound_variables = get_nc_coordinate_bounds_variables(nc_dataset)
    nc_coordinate_bound_variable_namelist = list(nc_coordinate_bound_variables.keys())

    return nc_coordinate_bound_variable_namelist


def get_nc_coordinate_bounds_variables_mapping(nc_dataset):
    """
    (object)-> dict

    Return: assign X_bounds, Y_bounds, Z_bounds, T_bounds to the coordinate bounds variables in netCDF.
    If not discerned then Unknown_bounds is returned to that variable
    """

    nc_coordinate_variables = get_nc_coordinate_variables(nc_dataset)
    nc_coordinate_bounds_variables_mapping = {}
    for var_name, var_obj in nc_coordinate_variables.items():
        coordinate_variable_type = get_coordinate_variable_type(var_obj)
        if hasattr(var_obj, 'bounds'):
            nc_coordinate_bounds_variables_mapping[coordinate_variable_type + '_bounds'] = var_obj.bounds

    return nc_coordinate_bounds_variables_mapping


# Function for Auxiliary Coordinate Variable ########################################################################
def get_nc_auxiliary_coordinate_variable_namelist(nc_dataset):
    """
    (object) -> list

    Return: the netCDF auxiliary coordinate variable names
    """

    nc_all_variables = nc_dataset.variables
    nc_auxiliary_coordinate_variable_namelist = []
    for var_name, var_obj in nc_all_variables.items():
        if hasattr(var_obj, 'coordinates'):
            nc_auxiliary_coordinate_variable_namelist = var_obj.coordinates.split(' ')
            break

    return nc_auxiliary_coordinate_variable_namelist


def get_nc_auxiliary_coordinate_variables(nc_dataset):
    """
    (object) -> dict

    Return: the netCDF auxiliary coordinate variables
    """

    nc_auxiliary_coordinate_variable_namelist = get_nc_auxiliary_coordinate_variable_namelist(nc_dataset)
    nc_auxiliary_coordinate_variables = {}
    for name in nc_auxiliary_coordinate_variable_namelist:
        if nc_dataset.variables.get(name, ''):
            nc_auxiliary_coordinate_variables[name] = nc_dataset.variables[name]

    return nc_auxiliary_coordinate_variables


# Function for Grid Mapping Variable ###############################################################################
def get_nc_grid_mapping_variable_name(nc_dataset):
    """
    (object)-> string

    Return: the netCDF grid mapping variable name
    """
    nc_all_variables = nc_dataset.variables
    nc_grid_mapping_variable_name = ''
    for var_name, var_obj in nc_all_variables.items():
        if hasattr(var_obj, 'grid_mapping_name'):
            nc_grid_mapping_variable_name = var_name

    return nc_grid_mapping_variable_name


def get_nc_grid_mapping_variable(nc_dataset):
    """
    (object)-> object

    Return: the netCDF grid mapping variable object
    """

    nc_all_variables = nc_dataset.variables
    nc_grid_mapping_variable = None
    for var_name, var_obj in nc_all_variables.items():
        if hasattr(var_obj, 'grid_mapping_name'):
            nc_grid_mapping_variable = var_obj

    return nc_grid_mapping_variable


def get_nc_grid_mapping_projection_name(nc_dataset):
    """
    (object)-> string

    Return: the netCDF grid mapping projection name
    """

    nc_grid_mapping_variable = get_nc_grid_mapping_variable(nc_dataset)
    if nc_grid_mapping_variable is not None:
        nc_grid_mapping_projection_name = nc_grid_mapping_variable.grid_mapping_name
    else:
        nc_grid_mapping_projection_name = ''

    return nc_grid_mapping_projection_name


def get_nc_grid_mapping_projection_import_string(nc_dataset):
    """
    (object)-> string

    Return: the netCDF grid mapping proj4 string used for creating projection object with pyproj.Proj()
    Reference: Cf convention for grid mapping projection
    """
    # get the proj name, proj variable
    nc_grid_mapping_projection_name = get_nc_grid_mapping_projection_name(nc_dataset)
    nc_grid_mapping_projection_import_string = ''
    nc_grid_mapping_variable = get_nc_grid_mapping_variable(nc_dataset)

    # get the proj info from cf convention
    albers_conical_equal_area = OrderedDict([
        ('+proj=', 'aea'),
        ('+lat_1=', 'standard_parallel'),
        ('+lat_0=', 'latitude_of_projection_origin'),
        ('+lon_0=', 'longitude_of_central_meridian'),
        ('+x_0=', 'false_easting'),
        ('+y_0=','false_northing'),
    ])
    azimuthal_equidistant = OrderedDict([
        ('+proj=', 'aeqd'),
        ('+lat_0=', 'latitude_of_projection_origin'),
        ('+lon_0=', 'longitude_of_projection_origin'),
        ('+x_0=', 'false_easting'),
        ('+y_0=','false_northing'),
    ])
    lambert_azimuthal_equal_area = OrderedDict([
        ('+proj=', 'laea'),
        ('+lat_0=', 'latitude_of_projection_origin'),
        ('+lon_0=', 'longitude_of_projection_origin'),
        ('+x_0=', 'false_easting'),
        ('+y_0=', 'false_northing'),
    ])
    lambert_conformal_conic = OrderedDict([
        ('+proj=', 'lcc'),
        ('+lat_1=', 'standard_parallel'),
        ('+lat_0=', 'latitude_of_projection_origin'),
        ('+lon_0=', 'longitude_of_central_meridian'),
        ('+x_0=', 'false_easting'),
        ('+y_0=', 'false_northing'),
    ])  # tested with real nc file
    lambert_cylindrical_equal_area =OrderedDict([
        ('+proj=', 'cea'),
        ('+lat_ts=', 'scale_factor_at_projection_origin'),
        ('+lat_ts=', 'standard_parallel'),
        ('+lon_0=', 'longitude_of_projection_origin'),
        ('+x_0=', 'false_easting'),
        ('+y_0=', 'false_northing'),
    ])
    mercator = OrderedDict([
        ('+proj=', 'merc'),
        ('+k_0=', 'scale_factor_at_projection_origin'),
        ('+lat_ts=', 'standard_parallel'),
        ('+lon_0=', 'longitude_of_projection_origin'),
        ('+x_0=', 'false_easting'),
        ('+y_0=', 'false_northing'),
    ])
    orthographic = OrderedDict([
        ('+proj=', 'ortho'),
        ('+lat_0=', 'latitude_of_projection_origin'),
        ('+lon_0=', 'longitude_of_projection_origin'),
        ('+x_0=', 'false_easting'),
        ('+y_0=', 'false_northing'),
    ])
    polar_stereographic = OrderedDict([
        ('+proj=', 'stere'),
        ('+k_0=', 'scale_factor_at_projection_origin'),
        ('+lat_ts=', 'standard_parallel'),
        ('+lat_0=', 'latitude_of_projection_origin'),
        ('+lon_0=', 'straight_vertical_longitude_from_pole'),
        ('+x_0=', 'false_easting'),
        ('+y_0=', 'false_northing'),
    ])
    #rotated_latitude_longitude = {}
    stereographic = OrderedDict([
        ('+proj=', 'stere'),
        ('+lat_0=', 'latitude_of_projection_origin'),
        ('+lon_0=', 'longitude_of_projection_origin'),
        ('+x_0=', 'false_easting'),
        ('+y_0=', 'false_northing'),
    ])
    transverse_mercator = OrderedDict([
        ('+proj=', 'tmerc'),
        ('+k_0=', 'scale_factor_at_projection_origin'),
        ('+lat_0=', 'latitude_of_projection_origin'),
        ('+lon_0=', 'longitude_of_projection_origin'),
        ('+x_0=', 'false_easting'),
        ('+y_0=', 'false_northing'),
    ])
    vertical_perspective = ([
        ('+proj=', 'geos'),
        ('+h=', 'perspective_point_height'),
        ('+lon_0=', 'longitude_of_projection_origin'),
        ('+x_0=', 'false_easting'),
        ('+y_0=', 'false_northing'),
    ])

    cf_convention_proj_info = {
        'albers_conical_equal_area': albers_conical_equal_area,
        'azimuthal_equidistant': azimuthal_equidistant,
        'lambert_azimuthal_equal_area': lambert_azimuthal_equal_area,
        'lambert_conformal_conic': lambert_conformal_conic,
        'lambert_cylindrical_equal_area': lambert_cylindrical_equal_area,
        'mercator': mercator,
        'orthographic': orthographic,
        'polar_stereographic': polar_stereographic,
        #'rotated_latitude_longitude': rotated_latitude_longitude,
        'stereographic': stereographic,
        'transverse_mercator': transverse_mercator,
        'vertical_perspective': vertical_perspective
    }

    # get the projection import string
    for proj_name, proj_para_dict in cf_convention_proj_info.items():
        if re.match(nc_grid_mapping_projection_name, proj_name, re.I):
            proj4_string = ''
            for para_name, para_value in proj_para_dict.items():
                if para_name == '+proj=':
                    proj4_string = proj4_string + '+proj=' + para_value
                elif hasattr(nc_grid_mapping_variable, para_value):
                    if para_name == '+lat_1':
                        value = nc_grid_mapping_variable.standard_parallel.sort()
                        if len(value) == 1:
                            proj4_string = proj4_string + ' +lat_1='+str(value[0])
                        elif len(value) == 2:
                            proj4_string = proj4_string + ' +lat_1='+str(value[0])+' +lat_2='+str(value[1])
                    else:
                        proj4_string = proj4_string + ' ' + para_name + str(getattr(nc_grid_mapping_variable, para_value))
                else:
                    proj4_string = ''
                    break

            if proj4_string != '':
                nc_grid_mapping_projection_import_string = proj4_string

            break

    return nc_grid_mapping_projection_import_string

# Function for Data Variable ##################################################################################
def get_nc_data_variables(nc_dataset):
    """
    (object) -> dict

    Return: the netCDF Data variables
    """

    nc_non_data_variables_namelist = get_nc_coordinate_variable_namelist(nc_dataset)\
                              + get_nc_coordinate_bounds_variable_namelist(nc_dataset)\
                              + get_nc_auxiliary_coordinate_variable_namelist(nc_dataset)
    nc_data_variables = {}
    for var_name, var_obj in nc_dataset.variables.items():
        if (var_name not in nc_non_data_variables_namelist) and (len(var_obj.shape) > 1):
            nc_data_variables[var_name] = var_obj

    return nc_data_variables


def get_nc_data_variable_namelist(nc_dataset):
    """
    (object) -> list

    Return: the netCDF Data variables names
    """

    nc_data_variables = get_nc_data_variables(nc_dataset)
    nc_data_variable_namelist = list(nc_data_variables.keys())

    return nc_data_variable_namelist







