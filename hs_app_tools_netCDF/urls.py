from django.conf.urls import patterns, url
from hs_app_tools_netCDF import views


urlpatterns = patterns('',

    # url for netcdf tools landing page
    url(r'^nc_tools/index/(?P<shortkey>[A-z0-9]+)/(?P<state>initial|processing)/$', views.index_view, name='index'),

    # url for meta edit button (view)
    url(r'^nc_tools/meta_edit/(?P<shortkey>[A-z0-9]+)/$', views.meta_edit_view, name='meta_edit'),

    # url for create ncdump button(view)
    url(r'^nc_tools/create_ncdump/(?P<shortkey>[A-z0-9]+)/$', views.create_ncdump_view, name='create_ncdump'),

    # url for data inspector button(view)
    url(r'^nc_tools/data_inspector/(?P<shortkey>[A-z0-9]+)/$', views.data_inspector_view, name='data_inspector'),

    # url for data subset button(view)
    url(r'^nc_tools/data_subset/(?P<shortkey>[A-z0-9]+)/$', views.data_subset_view, name='data_subset'),
)
