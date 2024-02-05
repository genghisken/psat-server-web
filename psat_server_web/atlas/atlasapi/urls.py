from django.urls import include, path
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token
from . import views

urlpatterns = [
    path('api/cone/',                  views.ConeView.as_view()),
    path('api/objects/',               views.ObjectsView.as_view()),
    path('api/objectlist/',            views.ObjectListView.as_view()),
    path('api/vraprobabilities/',      views.VRAProbabilitiesView.as_view()),
    path('api/auth-token/',            obtain_auth_token, name='auth_token'),
]
