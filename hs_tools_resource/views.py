from __future__ import absolute_import
from django.contrib.auth.decorators import login_required
from django import forms
from django.shortcuts import redirect
from hs_core import hydroshare
import urllib

class GoForToolsForm(forms.Form):
    my_str = forms.CharField(required=False, min_length=0) # reserving this in case I need something

@login_required
def go_for_tools(request, shortkey, user, tooltype, *args, **kwargs):
    frm = GoForToolsForm(request.POST)

    if frm.is_valid():
        my_string = frm.cleaned_data.get('my_str')
        url_base = "https://google.com" # TODO change eventually...
        res = hydroshare.get_resource(shortkey)
        f_url = str(res.files.first().resource_file)
        f_name = f_url.split("/")[-1]  # choose the last part of the url for the file, which is it's name

        myParameters = { "res_id" : shortkey, "user" : user, "tool_type" : tooltype, "file_name": f_name }
        myURL = "%s?%s" % (url_base, urllib.urlencode(myParameters))
        return redirect(myURL)
