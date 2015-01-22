from django.forms import ModelForm, Textarea, BaseFormSet
from django import forms
from crispy_forms.layout import *
from crispy_forms.helper import FormHelper
from crispy_forms.bootstrap import *
from hs_app_netCDF.models import *
from django.forms.models import formset_factory

# Keep this one unchanged
class BaseFormHelper(FormHelper):
    def __init__(self, res_short_id=None, element_id=None, element_name=None, element_layout=None,  *args, **kwargs):
        super(BaseFormHelper, self).__init__(*args, **kwargs)

        if res_short_id:
            self.form_method = 'post'
            if element_id:
                self.form_tag = True
                self.form_action = "/hsapi/_internal/%s/%s/%s/update-metadata/" % (res_short_id,element_name, element_id)
            else:
                self.form_action = "/hsapi/_internal/%s/%s/add-metadata/" % (res_short_id, element_name)
                self.form_tag = False
        else:
            self.form_tag = False

        # change the first character to uppercase of the element name
        element_name = element_name.title()

        if res_short_id and element_id:
            self.layout = Layout(
                            Fieldset(element_name,
                                     element_layout,
                                     HTML('<div style="margin-top:10px">'),
                                     HTML('<button type="submit" class="btn btn-primary">Save changes</button>'),
                                     HTML('</div>')
                            ),
                         )
        else:
            self.layout = Layout(
                            Fieldset(element_name,
                                     element_layout,
                            ),
                          )


# The following 3 classes need to have the "field" same as the fields defined in "Variable" table in models.py
class VariableFormHelper(BaseFormHelper):
    def __init__(self, res_short_id=None, element_id=None, element_name=None, *args, **kwargs):
        field_width = 'form-control input-sm'
        # change the fields name here
        layout = Layout(
                     Field('name', css_class=field_width),
                     Field('unit', css_class=field_width),
                     Field('type', css_class=field_width),
                     Field('shape', css_class=field_width),
                     Field('descriptive_name', css_class=field_width),
                     Field('method', css_class=field_width),
                     Field('missing_value', css_class=field_width)
                )

        super(VariableFormHelper, self).__init__(res_short_id, element_id, element_name, layout,  *args, **kwargs)


class VariableForm(ModelForm):
    def __init__(self, res_short_id=None, element_id=None, *args, **kwargs):
        super(VariableForm, self).__init__(*args, **kwargs)
        self.helper = VariableFormHelper(res_short_id, element_id, element_name='Variable')
        self.delete_modal_form = None
        self.number = 0
        if res_short_id:
            self.action = "/hsapi/_internal/%s/variable/add-metadata/" % res_short_id
        else:
            self.action = ""

    class Meta:
        model = Variable
        # change the fields same here
        fields = ['name', 'unit', 'type', 'shape', 'descriptive_name', 'method', 'missing_value']
        exclude = ['content_object']


class VariableValidationForm(forms.Form):
    name = forms.CharField(max_length=20)
    unit = forms.CharField(max_length=100)
    type = forms.CharField(max_length=100)
    shape = forms.CharField(max_length=100)
    descriptive_name = forms.CharField(max_length=100, required=False)
    method = forms.CharField(max_length=300, required=False)
    missing_value = forms.CharField(max_length=50, required=False)


class BaseVariableFormSet(BaseFormSet):
    def add_fields(self, form, index):
        super(BaseVariableFormSet, self).add_fields(form, index)


    def get_metadata_dict(self):
        variables_data = []
        for form in self.forms:
            variable_data = {k: v for k, v in form.cleaned_data.iteritems()}

            variables_data.append({'variable': variable_data})

        return variables_data

VariableFormSet = formset_factory(VariableForm, formset=BaseVariableFormSet, extra=0)


ModalDialogLayoutAddVariable = Layout(
                            HTML('<div class="modal fade" id="add-variable-dialog" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">'
                                    '<div class="modal-dialog">'
                                        '<div class="modal-content">'
                                            '<form action="{{ add_variable_modal_form.action }}" method="POST" enctype="multipart/form-data"> '
                                            '<div class="modal-header">'
                                                '<button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>'
                                                '<h4 class="modal-title" id="myModalLabel">Add Variable</h4>'
                                            '</div>'
                                            '<div class="modal-body">'
                                                '{% csrf_token %}'
                                                '<div class="form-group">'
                                                    '{% load crispy_forms_tags %} '
                                                    '{% crispy add_variable_modal_form %} '
                                                '</div>'
                                            '</div>'
                                            '<div class="modal-footer">'
                                                '<button type="button" class="btn btn-default" data-dismiss="modal">Close</button>'
                                                '<button type="submit" class="btn btn-primary">Save changes</button>'
                                            '</div>'
                                            '</form>'
                                        '</div>'
                                    '</div>'
                                '</div>'
                            )
                        )

VariableLayoutNew = Layout(
                            HTML('{% load crispy_forms_tags %} '
                                 '{% for form in variable_formset.forms %} '
                                     '<div class="item"> '
                                     '{% crispy form %} '
                                     '<div style="margin-top:10px"><input class="delete-creator btn-danger btn btn-md" type="button" value="Delete creator"></div>'
                                     '</div> '
                                 '{% endfor %}'
                                ),
                            HTML('<div style="margin-top:10px"><a id="addCreator" class="btn btn-success" href="#"><i class="fa fa-plus"></i>Add another creator</a></div>'),
                        )

VariableLayoutEdit = Layout(
                            HTML('{% load crispy_forms_tags %} '
                                 '{% for form in variable_formset.forms %} '
                                     '<div class="item form-group"> '
                                     '<form action="{{ form.action }}" method="POST" enctype="multipart/form-data"> '
                                     '{% crispy form %} '
                                    '<div class="row" style="margin-top:10px">'
                                        '<div class="col-md-10">'
                                            '<input class="btn-danger btn btn-md" type="button" data-toggle="modal" data-target="#delete-variable-element-dialog_{{ form.number }}" value="Delete variable">'
                                        '</div>'
                                        '<div class="col-md-2">'
                                            '<button type="submit" class="btn btn-primary">Save Changes</button>'
                                        '</div>'
                                    '</div>'
                                    '{% crispy form.delete_modal_form %} '
                                    '</form> '
                                    '</div> '
                                '{% endfor %}'
                            ),
                            HTML('<div style="margin-top:10px">'
                                 '<p><a id="add-creator" class="btn btn-success" data-toggle="modal" data-target="#add-variable-dialog">'
                                 '<i class="fa fa-plus"></i>Add another variable</a>'
                                 '</div>'
                            ),
                    )