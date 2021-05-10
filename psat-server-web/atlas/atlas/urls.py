from django.conf.urls import url
from django.urls import path, include
from django.contrib import admin
from atlas import views
from django.conf import settings
from django.conf.urls.static import static

admin.autodiscover()


urlpatterns = [
    # 2016-02-24 KWS Introduced the Django Admin URL
    path('admin/', admin.site.urls),
    # 2016-02-26 KWS Add the authentication URLs
    url(r'^accounts/login/', views.login, name="login"),
    url(r'^accounts/logout/', views.logout, name="logout"),
    url(r'^accounts/auth/', views.authView, name="auth"),
    url(r'^accounts/loggedin/', views.loggedin, name="loggedin"),
    url(r'^accounts/invalid/', views.invalidLogin, name="invalid"),

    url(r'^$', views.homepage, name='home'),

    # 2019-09-28 KWS New error page.
    url(r'^error/$', views.errorpage, name='error'),

    # 2017-06-16 KWS New ddc detections
#    url(r'^lightcurve/(?P<tcs_transient_objects_id>\d+)/$', views.lightcurveplain, name='lightcurveplain'),
    url(r'^lightcurve/(?P<tcs_transient_objects_id>\d+)/$', views.lightcurveplainddc, name='lightcurveplain'),
    url(r'^lightcurveforced/(?P<tcs_transient_objects_id>\d+)/$', views.lightcurveforcedplain, name='lightcurveforcedplain'),
    url(r'^atel/(?P<tcs_transient_objects_id>\d+)/$', views.atel, name='atel'),

    # 2017-06-16 KWS New ddc detections
#    url(r'^candidate/(?P<atlas_diff_objects_id>\d+)/$', views.candidate, name='candidate'),
    url(r'^candidate/(?P<atlas_diff_objects_id>\d+)/$', views.candidateddc, {'template_name':'candidate_plotly.html'}, name='candidate'),
    url(r'^candidate_bs/(?P<atlas_diff_objects_id>\d+)/$', views.candidateddc, {'template_name':'candidate_plotly.html'}, name='candidate_bs'),
    url(r'^candidate_old/(?P<atlas_diff_objects_id>\d+)/$', views.candidateddc, {'template_name':'candidate.html'}, name='candidate_old'),

    url(r'^userlist_atel_discovery/(?P<userDefinedListNumber>\d+)/$', views.atelsDiscovery, name='ateldiscovery'),
    url(r'^userlist_atel_fast/(?P<userDefinedListNumber>\d+)/$', views.atelsFast, name='atelfast'),
    url(r'^userlist_visibility/(?P<userDefinedListNumber>\d+)/$', views.visibility, name='visibility'),
    url(r'^userlist_iobserve/(?P<userDefinedListNumber>\d+)/$', views.iobserve, name='iobserve'),


    url(r'^externalcrossmatches/$', views.displayExternalCrossmatches, name='externalcrossmatches'),

    url(r'^followup/(?P<listNumber>\d+)/$', views.followupList, name='followup'),
    url(r'^followuptxt/(?P<listNumber>\d+)/$', views.followuptxt, name='followuptxt'),
    url(r'^followupsubsettxt/(?P<listNumber>\d+)/$', views.followupsubsettxt, name='followupsubsettxt'),
    url(r'^pesstosummary/$', views.pesstosummary, name='pesstosummary'),
#    url(r'^pesstorecurrences/$', views.pesstorecurrences, name='pesstorecurrences'),
    url(r'^pesstorecurrences/$', views.pesstorecurrencesddc, name='pesstorecurrences'),

    url(r'^summarycsv/(?P<listNumber>\d+)/$', views.summarycsv, name='summarycsv'),

#    url(r'^followup2/(?P<listNumber>\d+)/$', views.followupList2, name='followup2'),

    url(r'^followup3/(?P<listNumber>\d+)/$', views.followupList3, name='followup3'),

    # Experiment!
    url(r'^followup_bypass_django_tables/(?P<listNumber>\d+)/$', views.followup_bypass_django_tables, name='followup_bypass_django_tables'),

    url(r'^userlist/$', views.userDefinedListDefinitions, name='userdefinedlistdefs'),
    url(r'^userlist/(?P<userDefinedListNumber>\d+)/$', views.userDefinedLists, name='userdefinedlists'),

# 2016-06-15 KWS Added quickview URLs.
    url(r'^followup_quickview/(?P<listNumber>\d+)/$', views.followupQuickView, name='followupquickview'),
    url(r'^followup_quickview_bs/(?P<listNumber>\d+)/$', views.followupQuickViewBootstrapPlotly, name='followupquickviewbootstrapplotly'),
    url(r'^followup_quickview/$', views.followupAllQuickView, name='followupallquickview'),
    url(r'^userlist_quickview/(?P<userDefinedListNumber>\d+)/$', views.userDefinedListsQuickview, name='userdefinedlistsquickview'),

# 2016-08-27 KWS Search Results URL
    url(r'^searchresults/$', views.searchResults, name='searchresults'),
    url(r'^snejson/$', views.jsonSNe, name='snejson'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
