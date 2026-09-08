from django.urls import include, path
from rest_framework import routers
from . import views

urlpatterns = [
    path('api/cone/',                  views.ConeView.as_view()),
    path('api/objectlist/',            views.ObjectListView.as_view()),
    path('api/objectgroups/',          views.TcsObjectGroupsView.as_view()),
    path('api/auth-token/',            views.ObtainExpiringAuthToken.as_view(), name='auth_token'),
]
