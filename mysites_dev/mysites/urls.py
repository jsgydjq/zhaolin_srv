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
    url(r'^getNearbyPeople/', 'zhaolin.views.get_nearby_people'),
    url(r'^getUserDetail/', 'zhaolin.views.get_user_detail'),
    url(r'^postFollow/', 'zhaolin.views.post_follow_one'),
    url(r'^postNewAction/', 'zhaolin.views.post_new_action'),
    url(r'^postNewStatus/', 'zhaolin.views.post_new_status'),
    url(r'^postNewMessage/', 'zhaolin.views.post_new_message'),
    url(r'^postNewComment/', 'zhaolin.views.post_new_comment'),
    url(r'^getActionBriefList/', 'zhaolin.views.get_action_brief_list'),
    url(r'^getActionDetail/', 'zhaolin.views.get_action_detail'),
    url(r'^getStatusDetail/', 'zhaolin.views.get_status_detail'),
    url(r'^getAppComments/', 'zhaolin.views.get_app_comments'),
    url(r'^postNewAction/', 'zhaolin.views.post_new_action'),
    url(r'^getUserNewsfeedList/', 'zhaolin.views.get_user_newsfeed_list'),
    url(r'^postUpDownAction/', 'zhaolin.views.post_updown_action'),
    url(r'^postUpDownApp/', 'zhaolin.views.post_updown_app'),
)

urlpatterns += patterns('',
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root':settings.MEDIA_ROOT}),
)
