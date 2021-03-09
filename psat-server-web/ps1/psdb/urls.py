# 2016-07-07 KWS New format for Django 1.10
from django.conf.urls import url, include
from django.contrib import admin
from psdb import views
admin.autodiscover()

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),

    # 2016-07-07 KWS Add the authentication URLs
    url(r'^accounts/login/', views.login, name="login"),
    url(r'^accounts/logout/', views.logout, name="logout"),
    url(r'^accounts/auth/', views.authView, name="auth"),
    url(r'^accounts/loggedin/', views.loggedin, name="loggedin"),
    url(r'^accounts/invalid/', views.invalidLogin, name="invalid"),

    url(r'^$', views.redirectedHomepage, name='redirectedhome'),
    url(r'^psdb/$', views.homepage2, name='home2'),

    # 2020-09-30 KWS New error page.
    url(r'^error/$', views.errorpage, name='error'),

#    url(r'^psdb/test/$', views.homepage2, name='home2'),

    url(r'^psdb/temporary/$', views.temporaryHomepage),
    url(r'^psdb/followup_old/$', views.followup),
    url(r'^psdb/dss2/(?P<tcs_transient_objects_id>\d+)/$', views.dss2),
    url(r'^psdb/type/(?P<objectType>\d+)/$', views.renderObjectType),
    url(r'^psdb/followup_old/(?P<listNumber>\d+)/$', views.followupList),
    url(r'^psdb/lightcurves/(?P<tcs_transient_objects_id>\d+)/$', views.lightcurves),
# 2011-07-06 KWS Add TEXT version of the light curve
    url(r'^psdb/lightcurve/(?P<tcs_transient_objects_id>\d+)/$', views.lightcurveplain),
    url(r'^psdb/lightcurveforced/(?P<tcs_transient_objects_id>\d+)/$', views.lightcurveforcedplain),
# 2013-02-08 KWS Add TEXT version of the colour plot
    url(r'^psdb/colour/(?P<tcs_transient_objects_id>\d+)/$', views.colourdataplain),
# 2012-07-18 KWS Experimental Flot lightcurves
    url(r'^psdb/candidate/(?P<tcs_transient_objects_id>\d+)/$', views.candidateflot, name="candidate"),
    url(r'^psdb/astronote/(?P<tcs_transient_objects_id>\d+)/$', views.astronote, name='astronote'),

# NEW format Followup Lists
    url(r'^psdb/followup/$', views.followupAllNew, name="followuplistall"),

    url(r'^psdb/followup/(?P<listNumber>\d+)/$', views.followupListNew, name="followuplist"),
    url(r'^psdb/followup_quickview/(?P<listNumber>\d+)/$', views.followupQuickView, name='followupquickview'),
    url(r'^psdb/followup_quickview/$', views.followupAllQuickView),

# Geojson view of the supernovae
    url(r'^snejson/$', views.jsonSNe, name='snejson'),

# PUBLIC release pages
    url(r'^psdb/public/$', views.followupAllPublic, name="followuplistallpublic"),
    url(r'^psdb/public_quickview/$', views.followupAllPublicQuickView, name="public_quickview"),
    url(r'^psdb/public_textonly/$', views.followupAllPublicTextOnly),

# 2011-04-14 KWS Add new User Defined Lists URL
    url(r'^psdb/userlist/$', views.userDefinedListDefinitions, name="userlists"),
    url(r'^psdb/userlist/(?P<userDefinedListNumber>\d+)/$', views.userDefinedLists, name='userdefinedlists'),

    url(r'^psdb/userlist_quickview/(?P<userDefinedListNumber>\d+)/$', views.userDefinedListsQuickview),
    url(r'^psdb/userlistcat/(?P<userDefinedListNumber>\d+)/$', views.obsCatalogue),
    url(r'^psdb/userlistwiki/(?P<userDefinedListNumber>\d+)/$', views.obsMediaWiki),
    url(r'^psdb/userlist_atel_discovery/(?P<userDefinedListNumber>\d+)/$', views.atelsDiscovery),
    url(r'^psdb/userlist_gcn/(?P<userDefinedListNumber>\d+)/$', views.gcn),
    url(r'^psdb/userlist_gcn_latex/(?P<userDefinedListNumber>\d+)/$', views.gcnlatex),

# 2014-07-23 KWS Added New CSV lists
    url(r'^psdb/followupcsv/(?P<listNumber>\d+)/$', views.followupCsv),

# 2011-05-08 KWS Add new Reports directory
    url(r'^psdb/reports/$', views.reportspage),

    url(r'^psdb/crossmatchcfatoipp/$', views.displayCfAtoIPPCrossmatches),
    url(r'^psdb/crossmatchipptocfa/$', views.displayIPPtoCfACrossmatches),

# 2013-10-21 KWS Add new External Crossmatch page
    url(r'^psdb/externalcrossmatches/$', views.displayExternalCrossmatches),

# 2016-08-27 KWS Search Results URL
    url(r'^searchresults/$', views.searchResults, name='searchresults'),
]

