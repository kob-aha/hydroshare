from django import forms


# Forms for Meta Edit Tool
class MetaElementsForm(forms.Form):
    """
    class for creating the multiple choice form for the core and extended metadata
    """
    meta_elements = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple)
