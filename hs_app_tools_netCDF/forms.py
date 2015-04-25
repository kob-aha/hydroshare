from django import forms


# Forms for File Process:
class FileProcess(forms.Form):
    FILE_PROCESS = (
        ('new_ver_res', "Create a new version of the existing resource with edited netcdf file."),
        ('new_res', "Create a new resource with edited netcdf file."),
    )

    file_process = forms.ChoiceField(widget=forms.RadioSelect(), #forms.CheckboxSelectMultiple
                                     choices=FILE_PROCESS,
                                     label='Select the Action after Tool Processing is Finished (Requird)',
                                    )

# Forms for Meta Edit Tool
class MetaElementsForm(forms.Form):
    """
    class for creating the multiple choice form for the core and extended metadata
    """
    META_ELEMENTS = (
        ('title', 'Title'),
        ('creator', 'Creator'),
        ('contributor', 'Contributor'),
        ('description', 'Abstract'),
        ('subjects', 'Keyword'),
        ('spatial_coverage', 'Spatial Coverage'),
        ('temporal_coverage', 'Temporal Coverage'),
        ('rights', 'Right'),
        ('source', 'Source'),
        ('publisher', 'Publisher'),
        ('identifier', 'Permanent Link'),
        ('relation', 'Relation:cites'),
        ('variable', 'Variable'),
    )

    meta_elements = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                              choices=META_ELEMENTS,
                                              label='Select Meta Elements to Write to NetCDF File (Required)'
                                            )


# Forms for Data Subset Tool:
class DimensionForm(forms.Form):
    dim_name = forms.CharField(max_length=100,
                               widget=forms.TextInput(attrs={'readonly':'readonly'}))

    dim_subset_value = forms.CharField(max_length=100)


class VariableNamesForm(forms.Form):
    variable_names = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                              label='Select the Data Variable Names for Data Subset (Required)',
                                            )
