from django.conf.urls import patterns, url
from hs_app_tools_netcdf import views


urlpatterns = patterns('',

    # url for netcdf tools landing page
    url(r'^nc_tools/index/$', views.index),

)
