from django.conf.urls import patterns, url

from .views import AnnouncementListView
from .views import AnnouncementUpdateView
from .views import AnnouncementCreateView
from .views import AnnouncementDeleteView
from .views import AnnouncementDetailView

urlpatterns = patterns('',
    url('^$',                               AnnouncementListView.as_view(),         name='announcements_announcement_list'),
    url('^create/$',                        AnnouncementCreateView.as_view(),       name='announcements_announcement_create'),
    url('^(?P<pk>\d+)/update/$',            AnnouncementUpdateView.as_view(),       name='announcements_announcement_update'),
    url('^(?P<pk>\d+)/delete/$',            AnnouncementDeleteView.as_view(),       name='announcements_announcement_delete'),
    url('^(?P<pk>\d+)/$',                   AnnouncementDetailView.as_view(),       name='announcements_announcement_detail'),
)