from mezzanine.pages.page_processors import processor_for
from hs_core.models import GenericResource

def get_user(request):
    """authorize user based on API key if it was passed, otherwise just use the request's user.

    :param request:
    :return: django.contrib.auth.User
    """

    from tastypie.models import ApiKey

    if 'api_key' in request.REQUEST:
        api_key = ApiKey.objects.get(key=request.REQUEST['api_key'])
        return api_key.user
    elif request.user.is_authenticated():
        return User.objects.get(pk=request.user.pk)
    else:
        return request.user

# this should be used as the page processor for anything with pagepermissionsmixin
# page_processor_for(MyPage)(ga_resources.views.page_permissions_page_processor)
def page_permissions_page_processor(request, page):
    page = page.get_content_model()
    user = get_user(request)

    return {
        "edit_groups": set(page.edit_groups.all()),
        "view_groups": set(page.view_groups.all()),
        "edit_users": set(page.edit_users.all()),
        "view_users": set(page.view_users.all()),
        "can_edit": (user in set(page.edit_users.all())) \
                    or (len(set(page.edit_groups.all()).intersection(set(user.groups.all()))) > 0)
    }

