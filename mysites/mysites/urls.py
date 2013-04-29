from django.conf.urls import patterns, include, url
from django.conf import settings

#from zhaolin import views
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mysites.views.home', name='home'),
    # url(r'^mysites/', include('mysites.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/$', include(admin.site.urls)),
    url(r'^updateUser/', 'zhaolin.views.update_user'),
    url(r'^updateLocation/', 'zhaolin.views.update_location'),
    url(r'^shareApps/', 'zhaolin.views.share_apps'),
    url(r'^collectApp/', 'zhaolin.views.collect_app'),
    url(r'^getFriendApps/', 'zhaolin.views.get_friend_apps'),
    url(r'^getNearbyApps/', 'zhaolin.views.get_nearby_apps'),
)

urlpatterns += patterns('',
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root':settings.MEDIA_ROOT}),
)
