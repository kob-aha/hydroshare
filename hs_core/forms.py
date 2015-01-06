__author__ = 'pabitra'


from models import *
from django.forms import ModelForm, BaseFormSet, DateInput
from django.forms.models import inlineformset_factory, modelformset_factory, formset_factory
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, HTML
from crispy_forms.bootstrap import *
from django.forms.extras.widgets import SelectDateWidget

ModalDialogLayoutAddCreator = Layout(
                            HTML('<div class="modal fade" id="add-creator-dialog" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">'
                                    '<div class="modal-dialog">'
                                        '<div class="modal-content">'
                                            '<form action="{{ add_creator_modal_form.action }}" method="POST" enctype="multipart/form-data"> '
                                            '<div class="modal-header">'
                                                '<button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>'
                                                '<h4 class="modal-title" id="myModalLabel">Add Creator</h4>'
                                            '</div>'
                                            '<div class="modal-body">'
                                                '{% csrf_token %}'
                                                '<div class="form-group">'
                                                    '{% load crispy_forms_tags %} '
                                                    '{% crispy add_creator_modal_form %} '
                                                    '{% for link_form in add_creator_modal_form.profile_link_formset.forms %} '
                                                     '<div class="item_link" '
                                                     '{% crispy link_form %} '
                                                     '</div> {% endfor %} '
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

ModalDialogLayoutAddContributor = Layout(
                            HTML('<div class="modal fade" id="add-contributor-dialog" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">'
                                    '<div class="modal-dialog">'
                                        '<div class="modal-content">'
                                            '<form action="{{ add_contributor_modal_form.action }}" method="POST" enctype="multipart/form-data"> '
                                            '<div class="modal-header">'
                                                '<button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>'
                                                '<h4 class="modal-title" id="myModalLabel">Add Contributor</h4>'
                                            '</div>'
                                            '<div class="modal-body">'
                                                '{% csrf_token %}'
                                                '<div class="form-group">'
                                                    '{% load crispy_forms_tags %} '
                                                    '{% crispy add_contributor_modal_form %} '
                                                    '{% for link_form in add_creator_modal_form.profile_link_formset.forms %} '
                                                    '<div class="item_link" '
                                                    '{% crispy link_form %} '
                                                    '</div> {% endfor %} '
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

ModalDialogLayoutAddRelation = Layout(
                                HTML('<div class="modal fade" id="add-relation-dialog" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">'
                                        '<div class="modal-dialog">'
                                            '<div class="modal-content">'
                                                '<form action="{{ add_relation_modal_form.action }}" method="POST" enctype="multipart/form-data"> '
                                                '<div class="modal-header">'
                                                    '<button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>'
                                                    '<h4 class="modal-title" id="myModalLabel">Add Relation</h4>'
                                                '</div>'
                                                '<div class="modal-body">'
                                                    '{% csrf_token %}'
                                                    '<div class="form-group">'
                                                        '{% load crispy_forms_tags %} '
                                                        '{% crispy add_relation_modal_form %} '
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

ModalDialogLayoutAddSource = Layout(
                                HTML('<div class="modal fade" id="add-source-dialog" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">'
                                        '<div class="modal-dialog">'
                                            '<div class="modal-content">'
                                                '<form action="{{ add_source_modal_form.action }}" method="POST" enctype="multipart/form-data"> '
                                                '<div class="modal-header">'
                                                    '<button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>'
                                                    '<h4 class="modal-title" id="myModalLabel">Add Source</h4>'
                                                '</div>'
                                                '<div class="modal-body">'
                                                    '{% csrf_token %}'
                                                    '<div class="form-group">'
                                                        '{% load crispy_forms_tags %} '
                                                        '{% crispy add_source_modal_form %} '
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

CreatorLayoutNew = Layout(
                            HTML('{% load crispy_forms_tags %} '
                                 '{% for form in creator_formset.forms %} '
                                     '<div class="item"> '
                                     '{% crispy form %} '
                                     '{{ form.profile_link_formset.management_form }} '
                                     '{% for link_form in form.profile_link_formset.forms %} '
                                        '<div class="item_link"> '
                                            '{% crispy link_form %} '
                                        '</div> '
                                     '{% endfor %} '
                                     '<div style="margin-top:10px"><a id="addLinkCreator" class="btn btn-success" href="#"><i class="fa fa-plus"></i>Add another link</a></div>'
                                     '<div style="margin-top:10px"><input class="delete-creator btn-danger btn btn-md" type="button" value="Delete creator"></div>'
                                     '</div> '
                                 '{% endfor %}'
                                ),
                            HTML('<div style="margin-top:10px"><a id="addCreator" class="btn btn-success" href="#"><i class="fa fa-plus"></i>Add another creator</a></div>'),
                        )

CreatorLayoutEdit = Layout(
                            HTML('{% load crispy_forms_tags %} '
                                 '{% for form in creator_formset.forms %} '
                                     '<div class="item form-group"> '
                                         '<form action="{{ form.action }}" method="POST" enctype="multipart/form-data"> '
                                         '{% crispy form %} '
                                            '{{ form.profile_link_formset.management_form }} '
                                            '{% for link_form in form.profile_link_formset.forms %} '
                                                '<div class="item_link"> '
                                                    '{% crispy link_form %} '
                                                '</div>'
                                            '{% endfor %} '
                                        '<div style="margin-top:10px"><a id="addLinkCreator" class="btn btn-success" disabled="disabled" href="#"><i class="fa fa-plus"></i>Add another link</a></div>'
                                        '<div class="row" style="margin-top:10px">'
                                            '<div class="col-md-10">'
                                                '<input class="btn-danger btn btn-md" type="button" data-toggle="modal" data-target="#delete-creator-element-dialog_{{ form.number }}" value="Delete creator">'
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
                                 '<p><a id="add-creator" class="btn btn-success" data-toggle="modal" data-target="#add-creator-dialog">'
                                 '<i class="fa fa-plus"></i>Add another creator</a>'
                                 '</div>'
                            ),
                    )

ContributorLayoutNew = Layout(
                            HTML('{% load crispy_forms_tags %} '
                                 '{% for form in contributor_formset.forms %} '
                                     '<div class="item"> '
                                     '{% crispy form %} '
                                     '{{ form.profile_link_formset.management_form }} '
                                     '{% for link_form in form.profile_link_formset.forms %} '
                                        '<div class="item_link"> '
                                            '{% crispy link_form %} '
                                        '</div> '
                                     '{% endfor %} '
                                     '<div style="margin-top:10px"><a id="addLinkContributor" class="btn btn-success" href="#"><i class="fa fa-plus"></i>Add another link</a></div>'
                                     '<div style="margin-top:10px"><input class="delete-creator btn-danger btn btn-md" type="button" value="Delete contributor"></div>'
                                     '</div> '
                                 '{% endfor %}'
                                ),
                            HTML('<div style="margin-top:10px"><a id="addContributor" class="btn btn-success" href="#"><i class="fa fa-plus"></i>Add another contributor</a></div>'),
                        )

ContributorLayoutEdit = Layout(
                            HTML('{% load crispy_forms_tags %} '
                                 '{% for form in contributor_formset.forms %} '
                                     '<div class="item form-group"> '
                                         '<form action="{{ form.action }}" method="POST" enctype="multipart/form-data"> '
                                         '{% crispy form %} '
                                            '{{ form.profile_link_formset.management_form }} '
                                            '{% for link_form in form.profile_link_formset.forms %} '
                                                '<div class="item_link"> '
                                                    '{% crispy link_form %} '
                                                '</div>'
                                            '{% endfor %} '
                                        '<div style="margin-top:10px"><a id="addLinkContributor" class="btn btn-success" disabled="disabled" href="#"><i class="fa fa-plus"></i>Add another link</a></div>'
                                        '<div class="row" style="margin-top:10px">'
                                            '<div class="col-md-10">'
                                                '<input class="btn-danger btn btn-md" type="button" data-toggle="modal" data-target="#delete-contributor-element-dialog_{{ form.number }}" value="Delete contributor">'
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
                                 '<p><a id="add-creator" class="btn btn-success" data-toggle="modal" data-target="#add-contributor-dialog">'
                                 '<i class="fa fa-plus"></i>Add another contributor</a>'
                                 '</div>'
                            ),
                    )


RelationLayoutNew = Layout(
                            HTML('{% load crispy_forms_tags %} '
                                 '{% for form in relation_formset.forms %} '
                                     '<div class="item"> '
                                     '{% crispy form %} '
                                     '<div style="margin-top:10px"><input class="delete-relation btn-danger btn btn-md" type="button" value="Delete relation"></div>'
                                     '</div> '
                                 '{% endfor %}'
                                ),
                            HTML('<div style="margin-top:10px"><a id="addRelation" class="btn btn-success" href="#"><i class="fa fa-plus"></i>Add another relation</a></div>'),
                        )


RelationLayoutEdit = Layout(
                            HTML('{% load crispy_forms_tags %} '
                                 '{% for form in relation_formset.forms %} '
                                     '<div class="item form-group"> '
                                         '<form action="{{ form.action }}" method="POST" enctype="multipart/form-data"> '
                                         '{% crispy form %} '
                                         '<div class="row" style="margin-top:10px">'
                                            '<div class="col-md-10">'
                                                '<input class="btn-danger btn btn-md" type="button" data-toggle="modal" data-target="#delete-relation-element-dialog_{{ form.number }}" value="Delete relation">'
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
                                 '<p><a id="add-relation" class="btn btn-success" data-toggle="modal" data-target="#add-relation-dialog">'
                                 '<i class="fa fa-plus"></i>Add another relation</a>'
                                 '</div>'
                            ),
                    )


SourceLayoutNew = Layout(
                            HTML('{% load crispy_forms_tags %} '
                                 '{% for form in source_formset.forms %} '
                                     '<div class="item"> '
                                     '{% crispy form %} '
                                     '<div style="margin-top:10px"><input class="delete-source btn-danger btn btn-md" type="button" value="Delete source"></div>'
                                     '</div> '
                                 '{% endfor %}'
                                ),
                            HTML('<div style="margin-top:10px"><a id="addSource" class="btn btn-success" href="#"><i class="fa fa-plus"></i>Add another source</a></div>'),
                        )


SourceLayoutEdit = Layout(
                            HTML('{% load crispy_forms_tags %} '
                                 '{% for form in source_formset.forms %} '
                                     '<div class="item form-group"> '
                                         '<form action="{{ form.action }}" method="POST" enctype="multipart/form-data"> '
                                         '{% crispy form %} '
                                         '<div class="row" style="margin-top:10px">'
                                            '<div class="col-md-10">'
                                                '<input class="btn-danger btn btn-md" type="button" data-toggle="modal" data-target="#delete-source-element-dialog_{{ form.number }}" value="Delete source">'
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
                                 '<p><a id="add-source" class="btn btn-success" data-toggle="modal" data-target="#add-source-dialog">'
                                 '<i class="fa fa-plus"></i>Add another source</a>'
                                 '</div>'
                            ),
                    )

IdentifierLayoutEdit = Layout(
                            HTML('{% load crispy_forms_tags %} '
                                 '{% for form in identifier_formset.forms %} '
                                    '{% crispy form %} '
                                '{% endfor %}'
                            ),
                    )

FormatLayoutEdit = Layout(
                            HTML('{% load crispy_forms_tags %} '
                                 '{% for form in format_formset.forms %} '
                                    '{% crispy form %} '
                                '{% endfor %}'
                            ),
                    )


# the 1st and the 3rd HTML layout objects get replaced in MetaDataElementDeleteForm class
def _get_modal_confirm_delete_matadata_element():
    layout = Layout(
                    HTML('<div class="modal fade" id="delete-metadata-element-dialog" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">'),
                            HTML('<div class="modal-dialog">'
                                '<div class="modal-content">'
                                    '<div class="modal-header">'
                                        '<button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>'
                                        '<h4 class="modal-title" id="myModalLabel">Delete metadata element</h4>'
                                    '</div>'
                                    '<div class="modal-body">'
                                        '<strong>Are you sure you want to delete this metadata element?</strong>'

                                    '</div>'
                                    '<div class="modal-footer">'
                                        '<button type="button" class="btn btn-default" data-dismiss="modal">Cancel</button>'),
                                        HTML('<a type="button" class="btn btn-danger" href="">Delete</a>'),
                                    HTML('</div>'
                                '</div>'
                            '</div>'
                        '</div>'),
                    )
    return layout


class MetaDataElementDeleteForm(forms.Form):
    def __init__(self, res_short_id, element_name, element_id , *args, **kwargs):
        super(MetaDataElementDeleteForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.delete_element_action = '"/hsapi/_internal/%s/%s/%s/delete-metadata/"' % (res_short_id, element_name, element_id)
        self.helper.layout = _get_modal_confirm_delete_matadata_element()
        self.helper.layout[0] = HTML('<div class="modal fade" id="delete-%s-element-dialog_%s" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">' % (element_name, element_id))
        self.helper.layout[2] = HTML('<a type="button" class="btn btn-danger" href=%s>Delete</a>' % self.delete_element_action)
        self.helper.form_tag = False


class MetaDataForm(forms.Form):
    def __init__(self, resource_mode='new', extended_metadata_layout=None, *args, **kwargs):
        super(MetaDataForm, self).__init__(*args, **kwargs)
        if not extended_metadata_layout:
            extended_metadata_layout = HTML('<h3>No extended metadata for this resource.</h3>')

        if resource_mode == 'new':
            creator_layout = CreatorLayoutNew
            contributor_layout = ContributorLayoutNew
            relation_layout = RelationLayoutNew
            source_layout = SourceLayoutNew
            # no UI for identifier when creating a resource as identifier elements are created automatically by the system
            identifier_layout = Layout()
            format_layout = Layout()
            #source_form = SourceForm()
            modal_dialog_add_creator = Layout()
            modal_dialog_add_contributor = Layout()
            modal_dialog_add_relation = Layout()
            modal_dialog_add_source = Layout()
        else:
            creator_layout = CreatorLayoutEdit
            contributor_layout = ContributorLayoutEdit
            relation_layout = RelationLayoutEdit
            source_layout = SourceLayoutEdit
            identifier_layout = IdentifierLayoutEdit
            format_layout = FormatLayoutEdit
            modal_dialog_add_creator = ModalDialogLayoutAddCreator
            modal_dialog_add_contributor = ModalDialogLayoutAddContributor
            modal_dialog_add_relation = ModalDialogLayoutAddRelation
            modal_dialog_add_source = ModalDialogLayoutAddSource

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_action = "/hsapi/_internal/create-resource/"
        self.helper.form_tag = False

        if resource_mode == 'new':
            layout = Layout(
                TabHolder(
                    Tab("Core Metadata",
                        HTML('<div class="form-group">'
                             '<label for="" control-label">Title</label>'
                             '<input type="text" class="form-control input-sm" name="title" id="" placeholder="Title" value="{{ title }}">'
                             '</div>'),

                        HTML('<div class="form-group">'
                             '<label for="" control-label">Abstract</label>'
                             '<textarea class="mceEditor charfield" cols="40" id="" name="abstract" rows="10" placeholder="Abstract">{{ abstract }}</textarea>'
                             '</div>'),

                        HTML('<div class="form-group">'
                             '<label for="" control-label">Keywords</label>'
                             '<input type="text" class="form-control" id="" name="keywords" placeholder="Keywords">'
                             '</div>'),
                        Accordion(
                            AccordionGroup('Rights (required)',
                                HTML('<div class="form-group" id="source"> '
                                        '{% load crispy_forms_tags %} '
                                        '{% crispy rights_form %} '
                                     '</div>'),
                            ),
                            AccordionGroup('Creators (required)',
                                HTML("<div class='form-group' id='creator'>"),
                                HTML("{{ creator_formset.management_form }}"),
                                creator_layout,
                                HTML("</div>"),
                            ),
                            AccordionGroup('Contributors (optional)',
                                HTML("<div class='form-group' id='contributor'>"),
                                HTML("{{ contributor_formset.management_form }}"),
                                contributor_layout,
                                HTML("</div>"),
                            ),
                            AccordionGroup('Relations (optional)',
                                HTML("<div class='form-group' id='relation'>"),
                                HTML("{{ relation_formset.management_form }}"),
                                relation_layout,
                                HTML("</div>"),
                            ),
                            AccordionGroup('Sources (optional)',
                                HTML("<div class='form-group' id='source'>"),
                                HTML("{{ source_formset.management_form }}"),
                                source_layout,
                                HTML("</div>"),
                            ),

                            AccordionGroup('Language (optional)',
                                HTML('<div class="form-group" id="language"> '
                                        '{% load crispy_forms_tags %} '
                                        '{% crispy language_form %} '
                                     '</div>'),
                            ),
                            AccordionGroup('Valid date (optional)',
                                HTML('<div class="form-group" id="validdate"> '
                                        '{% load crispy_forms_tags %} '
                                        '{% crispy valid_date_form %} '
                                     '</div>'),
                            ),
                        ),
                    ),

                    # Specific resource type app needs to provide the crispy form Layout object: extended_metadata_layout
                    Tab("Extended Metadata",
                        extended_metadata_layout,
                    ),
                ),
                modal_dialog_add_creator,
                modal_dialog_add_contributor,
                modal_dialog_add_relation,
                modal_dialog_add_source,
            )
        else:
            layout = Layout(
                TabHolder(
                    Tab("Core Metadata",
                        HTML('<div class="form-group">'
                             '<label for="" control-label">Title</label>'
                             '<input type="text" class="form-control input-sm" name="title" id="" placeholder="Title" value="{{ title }}">'
                             '</div>'),

                        HTML('<div class="form-group">'
                             '<label for="" control-label">Abstract</label>'
                             '<textarea class="mceEditor charfield" cols="40" id="" name="abstract" rows="10" placeholder="Abstract">{{ abstract }}</textarea>'
                             '</div>'),

                        HTML('<div class="form-group">'
                             '<label for="" control-label">Keywords</label>'
                             '<input type="text" class="form-control" id="" name="keywords" placeholder="Keywords">'
                             '</div>'),
                        Accordion(
                            AccordionGroup('Rights (required)',
                                HTML('<div class="form-group" id="source"> '
                                        '{% load crispy_forms_tags %} '
                                        '{% crispy rights_form %} '
                                     '</div>'),
                            ),
                            AccordionGroup('Creators (required)',
                                HTML("<div class='form-group' id='creator'>"),
                                HTML("{{ creator_formset.management_form }}"),
                                creator_layout,
                                HTML("</div>"),
                            ),
                            AccordionGroup('Contributors (optional)',
                                HTML("<div class='form-group' id='contributor'>"),
                                HTML("{{ contributor_formset.management_form }}"),
                                contributor_layout,
                                HTML("</div>"),
                            ),
                            AccordionGroup('Relations (optional)',
                                HTML("<div class='form-group' id='relation'>"),
                                HTML("{{ relation_formset.management_form }}"),
                                relation_layout,
                                HTML("</div>"),
                            ),
                            AccordionGroup('Sources (optional)',
                                HTML("<div class='form-group' id='source'>"),
                                HTML("{{ source_formset.management_form }}"),
                                source_layout,
                                HTML("</div>"),
                            ),
                            AccordionGroup('Identifiers (required)',
                                HTML("<div class='form-group' id='identifier'>"),
                                HTML("{{ identifier_formset.management_form }}"),
                                identifier_layout,
                                HTML("</div>"),
                            ),

                            AccordionGroup('Language (optional)',
                                HTML('<div class="form-group" id="language"> '
                                        '{% load crispy_forms_tags %} '
                                        '{% crispy language_form %} '
                                     '</div>'),
                            ),
                            AccordionGroup('Valid date (optional)',
                                HTML('<div class="form-group" id="validdate"> '
                                        '{% load crispy_forms_tags %} '
                                        '{% crispy valid_date_form %} '
                                     '</div>'),
                            ),
                            AccordionGroup('Formats/MIME Types (optional)',
                                HTML("<div class='form-group' id='format'>"),
                                HTML("{{ format_formset.management_form }}"),
                                format_layout,
                                HTML("</div>"),
                            ),
                        ),
                    ),

                    # Specific resource type app needs to provide the crispy form Layout object: extended_metadata_layout
                    Tab("Extended Metadata",
                        extended_metadata_layout,
                    ),
                ),
                modal_dialog_add_creator,
                modal_dialog_add_contributor,
                modal_dialog_add_relation,
                modal_dialog_add_source,
            )

        self.helper.layout = layout


class ProfileLinksFormSetHelper(FormHelper):
    def __init__(self, link_for, *args, **kwargs):
        super(ProfileLinksFormSetHelper, self).__init__(*args, **kwargs)

        # the order in which the model fields are listed for the FieldSet is the order these fields will be displayed
        field_width = 'form-control input-sm'
        self.form_tag = False
        if link_for == 'creator':
            self.delete_btn_class = 'btn-danger delete-link-creator'
        else:
            self.delete_btn_class = 'btn-danger delete-link-contributor'

        link_delete_button = StrictButton('Delete Link', css_class=self.delete_btn_class)

        self.layout = Layout(
            Fieldset('External Profile Link',
                     Field('type', css_class=field_width),
                     Field('url', css_class=field_width),
                     HTML('<div style="margin-top:10px"></div>')
                     ),
            ButtonHolder(
                link_delete_button,
            )
        )


class ProfileLinksForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProfileLinksForm, self).__init__(*args, **kwargs)
        self.helper = ProfileLinksFormSetHelper(link_for='creator')

    class Meta:
        model = ExternalProfileLink
        fields = ['type', 'url']


class BaseProfileLinkFormSet(BaseFormSet):
    def get_metadata(self):
        links_data = []
        for form in self.forms:
            link_data = {k: v for k, v in form.cleaned_data.iteritems()}
            if len(link_data) > 0:
                links_data.append(link_data)

        return {'profile_links': links_data}


ProfileLinksFormset = formset_factory(ProfileLinksForm, formset=BaseProfileLinkFormSet)


class CreatorFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(CreatorFormSetHelper, self).__init__(*args, **kwargs)
        # the order in which the model fields are listed for the FieldSet is the order these fields will be displayed
        field_width = 'form-control input-sm'
        self.form_tag = False
        self.form_show_errors = True
        self.error_text_inline = True
        self.html5_required = True
        self.layout = Layout(
            Fieldset('Creator',
                     Field('name', css_class=field_width),
                     Field('description', css_class=field_width),
                     Field('organization', css_class=field_width),
                     Field('email', css_class=field_width),
                     Field('address', css_class=field_width),
                     Field('phone', css_class=field_width),
                     Field('homepage', css_class=field_width),
                     Field('order', css_class=field_width),
                     ),
        )

class PartyForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(PartyForm, self).__init__(*args, **kwargs)
        self.profile_link_formset = None
        self.number = 0

    class Meta:
        model = Party
        # fields that will be displayed are specified here - but not necessarily in the same order
        fields = ['name', 'description', 'organization', 'email', 'address', 'phone', 'homepage']

        # TODO: field labels and widgets types to be specified


class CreatorForm(PartyForm):
    def __init__(self, res_short_id=None, element_id=None, *args, **kwargs):
        super(CreatorForm, self).__init__(*args, **kwargs)
        self.helper = CreatorFormSetHelper()
        self.profile_link_formset = ProfileLinksFormset(prefix='creator_links')
        self.delete_modal_form = None
        if res_short_id:
            self.action = "/hsapi/_internal/%s/creator/add-metadata/" % res_short_id
        else:
            self.action = ""

    class Meta:
        model = Creator
        fields = PartyForm.Meta.fields
        fields.append("order")


class PartyValidationForm(forms.Form):
    description = forms.URLField(required=False)
    name = forms.CharField(max_length=100)
    organization = forms.CharField(max_length=200, required=False)
    email = forms.EmailField(required=False)
    address = forms.CharField(max_length=250, required=False)
    phone = forms.CharField(max_length=25, required=False)
    homepage = forms.URLField(required=False)


class CreatorValidationForm(PartyValidationForm):
    order = forms.IntegerField()


class ContributorValidationForm(PartyValidationForm):
    pass


class BaseCreatorFormSet(BaseFormSet):
    def add_fields(self, form, index):
        super(BaseCreatorFormSet, self).add_fields(form, index)

        # create the nested profile link formset
        form.profile_link_formset = ProfileLinksFormset(prefix='creator_links-%s' % index)

    def get_metadata(self):
        creators_data = []
        for form in self.forms:
            creator_data = {k: v for k, v in form.cleaned_data.iteritems()}
            if form.profile_link_formset.is_valid():
                profile_link_dict = form.profile_link_formset.get_metadata()
                if len(profile_link_dict['profile_links']) > 0:
                    creator_data['profile_links'] = profile_link_dict['profile_links']

            creators_data.append({'creator': creator_data})

        return creators_data

CreatorFormSet = formset_factory(CreatorForm, formset=BaseCreatorFormSet, extra=0)


class ContributorFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(ContributorFormSetHelper, self).__init__(*args, **kwargs)
        # the order in which the model fields are listed for the FieldSet is the order these fields will be displayed
        field_width = 'form-control input-sm'
        self.form_tag = False
        self.layout = Layout(
            Fieldset('Contributor',
                     Field('name', css_class=field_width),
                     Field('description', css_class=field_width),
                     Field('organization', css_class=field_width),
                     Field('email', css_class=field_width),
                     Field('address', css_class=field_width),
                     Field('phone', css_class=field_width),
                     Field('homepage', css_class=field_width),
                     ),
        )

        self.render_required_fields = True,


class ContributorForm(PartyForm):
    def __init__(self, res_short_id=None, element_id=None, *args, **kwargs):
        super(ContributorForm, self).__init__(*args, **kwargs)
        self.helper = ContributorFormSetHelper()
        self.profile_link_formset = ProfileLinksFormset(prefix='contributor_links')
        self.delete_modal_form = None
        if res_short_id:
            self.action = "/hsapi/_internal/%s/contributor/add-metadata/" % res_short_id
        else:
            self.action = ""

    class Meta:
        model = Contributor
        fields = PartyForm.Meta.fields
        if 'order' in fields:
            fields.remove('order')


class BaseContributorFormSet(BaseFormSet):

    # def clean(self):
    #     super(BaseContributorFormSet, self).clean()
    #     form_counter = 0
    #     for form in self.forms:
    #         if not form.is_valid() and len(form.cleaned_data) == 0:
    #             del self.errors[form_counter]
    #         form_counter +=1

    def add_fields(self, form, index):
        super(BaseContributorFormSet, self).add_fields(form, index)

        # create the nested profile link formset
        form.profile_link_formset = ProfileLinksFormset(prefix='contributor_links-%s' % index)

    def get_metadata(self):
        contributors_data = []
        for form in self.forms:
            contributor_data = {k: v for k, v in form.cleaned_data.iteritems()}
            if len(contributor_data) > 0:
                if form.profile_link_formset.is_valid():
                    profile_link_dict = form.profile_link_formset.get_metadata()
                    if len(profile_link_dict['profile_links']) > 0:
                        contributor_data['profile_links'] = profile_link_dict['profile_links']

                contributors_data.append({'contributor': contributor_data})

        return contributors_data


ContributorFormSet = formset_factory(ContributorForm, formset=BaseContributorFormSet)


class RelationFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(RelationFormSetHelper, self).__init__(*args, **kwargs)
        # the order in which the model fields are listed for the FieldSet is the order these fields will be displayed
        field_width = 'form-control input-sm'
        self.form_tag = False
        self.form_show_errors = True
        self.error_text_inline = True
        self.html5_required = False
        self.layout = Layout(
            Fieldset('Relation',
                     Field('type', css_class=field_width),
                     Field('value', css_class=field_width),
                     ),
        )


class BaseRelationFormSet(BaseFormSet):
    def get_metadata(self):
        relations_data = []
        for form in self.forms:
            relation_data = {k: v for k, v in form.cleaned_data.iteritems()}
            if len(relation_data) > 0:
                relations_data.append({'relation': relation_data})

        return relations_data


class RelationForm(ModelForm):
    def __init__(self, res_short_id=None, *args, **kwargs):
        super(RelationForm, self).__init__(*args, **kwargs)
        self.helper = RelationFormSetHelper()
        self.number = 0
        self.delete_modal_form = None
        if res_short_id:
            self.action = "/hsapi/_internal/%s/relation/add-metadata/" % res_short_id
        else:
            self.action = ""

    class Meta:
        model = Relation
        # fields that will be displayed are specified here - but not necessarily in the same order
        fields = ['type', 'value']
        labels = {'type': 'Relation type', 'value': 'Related to'}

        # TODO: field labels and widgets types to be specified


class RelationValidationForm(forms.Form):
    type = forms.CharField(max_length=100)
    value = forms.CharField(max_length=500)

RelationFormSet = formset_factory(RelationForm, formset=BaseRelationFormSet)


class SourceFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(SourceFormSetHelper, self).__init__(*args, **kwargs)
        # the order in which the model fields are listed for the FieldSet is the order these fields will be displayed
        field_width = 'form-control input-sm'
        self.form_tag = False
        self.form_show_errors = True
        self.error_text_inline = True
        self.html5_required = False
        self.layout = Layout(
            Fieldset('Source',
                     Field('derived_from', css_class=field_width),
                     ),
        )


class BaseSourceFormSet(BaseFormSet):
    def get_metadata(self):
        sources_data = []
        for form in self.forms:
            source_data = {k: v for k, v in form.cleaned_data.iteritems()}
            if len(source_data) > 0:
                sources_data.append({'source': source_data})

        return sources_data


class SourceForm(ModelForm):
    def __init__(self, res_short_id=None, *args, **kwargs):
        super(SourceForm, self).__init__(*args, **kwargs)
        self.helper = SourceFormSetHelper()
        self.number = 0
        self.delete_modal_form = None
        if res_short_id:
            self.action = "/hsapi/_internal/%s/source/add-metadata/" % res_short_id
        else:
            self.action = ""

    class Meta:
        model = Source
        # fields that will be displayed are specified here - but not necessarily in the same order
        fields = ['derived_from']

        # TODO: field labels and widgets types to be specified


class SourceValidationForm(forms.Form):
    derived_from = forms.CharField(max_length=300)


SourceFormSet = formset_factory(SourceForm, formset=BaseSourceFormSet)


class IdentifierFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(IdentifierFormSetHelper, self).__init__(*args, **kwargs)
        # the order in which the model fields are listed for the FieldSet is the order these fields will be displayed
        field_width = 'form-control input-sm'
        self.form_tag = False
        self.form_show_errors = True
        self.error_text_inline = True
        self.html5_required = True
        self.layout = Layout(
            Fieldset('Identifier',
                     Field('name', css_class=field_width),
                     Field('url', css_class=field_width),
                     ),
        )


class BaseIdentifierFormSet(BaseFormSet):
    def get_metadata(self):
        identifiers_data = []
        for form in self.forms:
            identifier_data = {k: v for k, v in form.cleaned_data.iteritems()}
            identifiers_data.append({'identifier': identifier_data})

        return identifiers_data


class IdentifierForm(ModelForm):
    def __init__(self, res_short_id=None, *args, **kwargs):
        super(IdentifierForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['readonly'] = True
        self.fields['url'].widget.attrs['readonly'] = True
        
        self.helper = IdentifierFormSetHelper()
        self.number = 0
        self.delete_modal_form = None
        if res_short_id:
            self.action = "/hsapi/_internal/%s/identifier/add-metadata/" % res_short_id
        else:
            self.action = ""

    class Meta:
        model = Identifier
        # fields that will be displayed are specified here - but not necessarily in the same order
        fields = ['name', 'url']

        # TODO: field labels and widgets types to be specified

IdentifierFormSet = formset_factory(IdentifierForm, formset=BaseIdentifierFormSet)


class FormatFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(FormatFormSetHelper, self).__init__(*args, **kwargs)
        # the order in which the model fields are listed for the FieldSet is the order these fields will be displayed
        field_width = 'form-control input-sm'
        self.form_tag = False
        self.form_show_errors = True
        self.error_text_inline = True
        self.html5_required = True
        self.layout = Layout(
            Fieldset('Format/MIME Type',
                     Field('value', css_class=field_width),
                     ),
        )


class BaseFormatFormSet(BaseFormSet):
    def get_metadata(self):
        formats_data = []
        for form in self.forms:
            format_data = {k: v for k, v in form.cleaned_data.iteritems()}
            formats_data.append({'format': format_data})

        return formats_data


class FormatForm(ModelForm):
    def __init__(self, res_short_id=None, *args, **kwargs):
        super(FormatForm, self).__init__(*args, **kwargs)
        self.fields['value'].widget.attrs['readonly'] = True

        self.helper = FormatFormSetHelper()
        self.number = 0
        self.delete_modal_form = None
        if res_short_id:
            self.action = "/hsapi/_internal/%s/format/add-metadata/" % res_short_id
        else:
            self.action = ""

    class Meta:
        model = Format
        # fields that will be displayed are specified here - but not necessarily in the same order
        fields = ['value']
        labels = {'value': 'Mime type'}

        # TODO: field labels and widgets types to be specified

FormatFormSet = formset_factory(FormatForm, formset=BaseFormatFormSet)


# Non repeatable element related forms
class BaseFormHelper(FormHelper):
    def __init__(self, res_short_id=None, element_id=None, element_name=None, element_layout=None,  *args, **kwargs):
        super(BaseFormHelper, self).__init__(*args, **kwargs)

        if res_short_id:
            self.form_method = 'post'
            self.form_tag = True
            if element_id:
                self.form_action = "/hsapi/_internal/%s/%s/%s/update-metadata/" % (res_short_id, element_name.lower(), element_id)
            else:
                self.form_action = "/hsapi/_internal/%s/%s/add-metadata/" % (res_short_id, element_name)
        else:
            self.form_tag = False

        # change the first character to uppercase of the element name
        element_name = element_name.title()

        if res_short_id:
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


class RightsFormHelper(BaseFormHelper):
    def __init__(self, res_short_id=None, element_id=None, element_name=None,  *args, **kwargs):

        # the order in which the model fields are listed for the FieldSet is the order these fields will be displayed
        field_width = 'form-control input-sm'
        layout = Layout(
                        Field('statement', css_class=field_width),
                        Field('url', css_class=field_width),
                 )

        super(RightsFormHelper, self).__init__(res_short_id, element_id, element_name, layout,  *args, **kwargs)


class RightsForm(ModelForm):
    def __init__(self, res_short_id=None, element_id=None, *args, **kwargs):
        super(RightsForm, self).__init__(*args, **kwargs)
        self.helper = RightsFormHelper(res_short_id, element_id, element_name='rights')

    class Meta:
        model = Rights
        fields = ['statement', 'url']
        exclude = ['content_object']


class RightsValidationForm(forms.Form):
    statement = forms.CharField(required=False)
    url = forms.URLField(required=False)

    def get_metadata(self):
        return {'rights': self.cleaned_data}


class LanguageFormHelper(BaseFormHelper):
    def __init__(self, res_short_id=None, element_id=None, element_name=None,  *args, **kwargs):

        # the order in which the model fields are listed for the FieldSet is the order these fields will be displayed
        field_width = 'form-control input-sm'
        layout = Layout(
                        Field('code', css_class=field_width),
                 )

        super(LanguageFormHelper, self).__init__(res_short_id, element_id, element_name, layout,  *args, **kwargs)


class LanguageForm(ModelForm):
    def __init__(self, res_short_id=None, element_id=None, *args, **kwargs):
        super(LanguageForm, self).__init__(*args, **kwargs)
        self.helper = LanguageFormHelper(res_short_id, element_id, element_name='language')
        self.initial['code'] = 'eng'

    class Meta:
        model = Language
        fields = ['code']
        exclude = ['content_object']
        labels = {'code': 'Language name'}

class LanguageValidationForm(forms.Form):
    code = forms.CharField(max_length=3)

    def get_metadata(self):
        return {'language': self.cleaned_data}


class ValidDateFormHelper(BaseFormHelper):
    def __init__(self, res_short_id=None, element_id=None, element_name=None,  *args, **kwargs):

        # the order in which the model fields are listed for the FieldSet is the order these fields will be displayed
        field_width = 'form-control input-sm'
        layout = Layout(
                        Field('start_date', css_class=field_width),
                        Field('end_date', css_class=field_width),
                 )

        super(ValidDateFormHelper, self).__init__(res_short_id, element_id, element_name, layout,  *args, **kwargs)


class ValidDateForm(ModelForm):
    def __init__(self, res_short_id=None, element_id=None, *args, **kwargs):
        super(ValidDateForm, self).__init__(*args, **kwargs)
        self.helper = ValidDateFormHelper(res_short_id, element_id, element_name='date')

    class Meta:
        model = Date
        fields = ['start_date', 'end_date']
        exclude = ['content_object']
        labels = {'start_date': 'Start date', 'end_date': 'End date'}
        widgets = {'start_date': DateInput(), 'end_date': DateInput()}


class ValidDateValidationForm(forms.Form):
    start_date = forms.DateField()
    end_date = forms.DateField()

    def clean(self):
        cleaned_data = super(ValidDateValidationForm, self).clean()
        start_date = cleaned_data.get('start_date', None)
        end_date = cleaned_data.get('end_date', None)
        if start_date and not end_date:
            self._errors['end_date'] = ["End date is missing"]

        if end_date and not start_date:
            self._errors['start_date'] = ["Start date is missing"]

        if not start_date and not end_date:
            del self._errors['start_date']
            del self._errors['end_date']

        if start_date and end_date:
            self.cleaned_data['type'] = 'valid'

        return self.cleaned_data

    def get_metadata(self):
        if len(self.cleaned_data) > 0:
            self.cleaned_data['type'] = 'valid'
            return {'date': self.cleaned_data}
        else:
            return []