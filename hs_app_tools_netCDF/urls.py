from django.conf.urls import patterns, url
from hs_app_tools_netCDF import views


urlpatterns = patterns('',

    # url for netcdf tools landing page
    url(r'^nc_tools/index/(?P<shortkey>[A-z0-9]+)/(?P<state>initial|processing)/$', views.index_view, name='index'),
    url(r'^nc_tools/meta_edit/(?P<shortkey>[A-z0-9]+)/$', views.meta_edit_view, name='meta_edit'),
)
