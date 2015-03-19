# Create your views here.
from django.contrib.auth.models import User
from django.views.generic import TemplateView
from hs_core.hydroshare import get_resource_types

from mezzanine.accounts.forms import LoginForm
from django.contrib.messages import info
from mezzanine.utils.urls import login_redirect
from mezzanine.utils.views import render
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import (authenticate, login as auth_login)
from django.conf import settings
from django.contrib.auth.decorators import login_required
from mezzanine.accounts import get_profile_form
from django.shortcuts import redirect
from django.core.urlresolvers import NoReverseMatch
from mezzanine.generic.views import initial_validation
from django.http import HttpResponse
from theme.forms import ThreadedCommentForm
from theme.forms import RatingForm
from mezzanine.utils.views import set_cookie, is_spam
from mezzanine.utils.cache import add_cache_bypass
from json import dumps

def login(request, template="accounts/account_login.html"):
    """
    Login form.
    """
    form = LoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        authenticated_user = form.save()
        info(request, _("Successfully logged in"))
        pwd = form.cleaned_data['password']
        auth_login(request, authenticated_user)

        if getattr(settings, 'USE_IRODS', False):
            if not getattr(settings, 'IRODS_GLOBAL_SESSION', False): # only create user session when IRODS_GLOBAL_SESSION is set to FALSE
                user = request.user
                if not user.is_superuser: # only create user session when the logged in user is not superuser
                    from hs_core.models import irods_storage
                    if irods_storage.session and irods_storage.environment:
                        try:
                            irods_storage.session.run('iexit full', None, irods_storage.environment.auth)
                        except:
                            pass # try to remove session if there is one, pass without error out if the previous session cannot be removed

                    irods_storage.set_user_session(username=user.get_username(), password=pwd, userid=user.id)

        return login_redirect(request)
    context = {"form": form, "title": _("Log in")}
    return render(request, template, context)

@login_required
def profile_update(request, template="accounts/account_profile_update.html"):
    """
    Profile update form.
    """
    profile_form = get_profile_form()
    form = profile_form(request.POST or None, request.FILES or None,
                        instance=request.user)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        # change corresponding iRODS account password accordingly when USE_IRODS is true but IRODS_GLOBAL_SESSION is FALSE and the user is not superuser
        if getattr(settings, 'USE_IRODS', False) and not getattr(settings, 'IRODS_GLOBAL_SESSION', False) and not request.user.is_superuser:
            newpwd = form.cleaned_data.get("password1")
            if newpwd:
                # change password for the corresponding iRODS account accordingly upon success
                from django_irods import account
                irods_account = account.IrodsAccount()
                uname = form.cleaned_data.get("username")
                irods_account.setPassward(uname, newpwd)
                # also needs to create a user session corresponding to the user just created to get ready for resource creation
                from hs_core.models import irods_storage
                if irods_storage.session and irods_storage.environment:
                    try:
                        irods_storage.session.run('iexit full', None, irods_storage.environment.auth)
                    except:
                        pass # try to remove session if there is one, pass without error out if the previous session cannot be removed

                irods_storage.set_user_session(username=uname, password=newpwd, userid=request.user.id)

        info(request, _("Profile updated"))
        try:
            return redirect("profile", username=user.username)
        except NoReverseMatch:
            return redirect("profile_update")
    context = {"form": form, "title": _("Update Profile")}
    return render(request, template, context)

class UserProfileView(TemplateView):
    template_name='accounts/profile.html'

    def get_context_data(self, **kwargs):
        if 'user' in kwargs:
            try:
                u = User.objects.get(pk=int(kwargs['user']))
            except:
                u = User.objects.get(username=kwargs['user'])

        else:
            try:
                u = User.objects.get(pk=int(self.request.GET['user']))
            except:
                u = User.objects.get(username=self.request.GET['user'])

        resource_types = get_resource_types()
        res = []
        for Resource in resource_types:
            res.extend([r for r in Resource.objects.filter(user=u)])

        return {
            'u' : u,
            'resources' :  res
        }

# added by Hong Yi to address issue #186 to customize Mezzanine-based commenting form and view
def comment(request, template="generic/comments.html"):
    """
    Handle a ``ThreadedCommentForm`` submission and redirect back to its
    related object.
    """
    response = initial_validation(request, "comment")
    if isinstance(response, HttpResponse):
        return response
    obj, post_data = response
    form = ThreadedCommentForm(request, obj, post_data)
    if form.is_valid():
        url = obj.get_absolute_url()
        if is_spam(request, form, url):
            return redirect(url)
        comment = form.save(request)
        response = redirect(add_cache_bypass(comment.get_absolute_url()))
        # Store commenter's details in a cookie for 90 days.
        # for field in ThreadedCommentForm.cookie_fields:
        #     cookie_name = ThreadedCommentForm.cookie_prefix + field
        #     cookie_value = post_data.get(field, "")
        #     set_cookie(response, cookie_name, cookie_value)
        return response
    elif request.is_ajax() and form.errors:
        return HttpResponse(dumps({"errors": form.errors}))
    # Show errors with stand-alone comment form.
    context = {"obj": obj, "posted_comment_form": form}
    response = render(request, template, context)
    return response

# added by Hong Yi to address issue #186 to customize Mezzanine-based rating form and view
def rating(request):
    """
    Handle a ``RatingForm`` submission and redirect back to its
    related object.
    """
    response = initial_validation(request, "rating")
    if isinstance(response, HttpResponse):
        return response
    obj, post_data = response
    url = add_cache_bypass(obj.get_absolute_url().split("#")[0])
    response = redirect(url + "#rating-%s" % obj.id)
    rating_form = RatingForm(request, obj, post_data)
    if rating_form.is_valid():
        rating_form.save()
        if request.is_ajax():
            # Reload the object and return the rating fields as json.
            obj = obj.__class__.objects.get(id=obj.id)
            rating_name = obj.get_ratingfield_name()
            json = {}
            for f in ("average", "count", "sum"):
                json["rating_" + f] = getattr(obj, "%s_%s" % (rating_name, f))
            response = HttpResponse(dumps(json))
        ratings = ",".join(rating_form.previous + [rating_form.current])
        set_cookie(response, "mezzanine-rating", ratings)
    return response
