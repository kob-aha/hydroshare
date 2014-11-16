from __future__ import absolute_import

from django.core.exceptions import PermissionDenied
from django.core import exceptions
from django.contrib.auth.models import User
from hs_core import hydroshare
import json

def get_user(request):
    """
    Determine the user from the request object.

    TODO: Add support for API keys
    :param request: HTTP request object
    :return: Django User object instance representing the user
    """
    user = None
    if request.user.is_authenticated():
        user = User.objects.get(pk=request.user.pk)
    else:
        user = request.user
    return user

def authorize(request, res_id, edit=False, view=False, full=False, superuser=False, raises_exception=True):
    """
    Authorizes the user making this request for the OR of the parameters.  If the user has ANY permission set to True in
    the parameter list, then this returns True else False.
    """
    user = get_user(request)

    res = hydroshare.utils.get_resource_by_shortkey(res_id)

    has_edit = res.edit_users.filter(pk=user.pk).exists()
    has_view = res.view_users.filter(pk=user.pk).exists()
    has_full = res.owners.filter(pk=user.pk).exists()

    authorized = (edit and has_edit) or \
                 (view and (has_view or res.public)) or \
                 (full and has_full) or \
                 (superuser and user.is_superuser)

    if raises_exception and not authorized:
        raise PermissionDenied()
    else:
        return res, authorized, user


def validate_json(js):
    try:
        json.loads(js)
    except ValueError:
        raise exceptions.ValidationError('Invalid JSON')

def create_form(formclass, request):
    try:
        params = formclass(data=json.loads(request.body))
    except ValueError:
        params = formclass(data=request.REQUEST)

    return params
