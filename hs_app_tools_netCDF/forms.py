from django import forms


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

    FILE_PROCESS = (
        ('new_ver_res', "Create new version of resource with edited netcdf file."),
        ('download_file', "Download the edited netcdf file to local computer."),
    )

    meta_elements = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                              choices=META_ELEMENTS,
                                              label='Select Meta Elements to Write to NetCDF File'
                                            )

    file_process = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                             choices=FILE_PROCESS,
                                             label='Select Actions after NetCDF File Meta Editing'
                                            )