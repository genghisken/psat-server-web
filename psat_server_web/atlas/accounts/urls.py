from django.urls import include, path, re_path
from django.contrib.auth import views as auth_views

from accounts import views

urlpatterns = [
    re_path(r'^login/', views.loginView, name="login"),
    re_path(r'^register/', views.register_user, name="register"),
    re_path(r'^logout/', views.logoutView, name="logout"),
    re_path(r'^auth/', views.authView, name="auth"),
    re_path(r'^loggedin/', views.loggedin, name="loggedin"),
    re_path(r'^invalid/', views.invalidLogin, name="invalid"),
    re_path(
        r'^change_password/$',
        views.AtlasPasswordChangeView.as_view(),
        name="change_password"
    ),
    re_path(
        r'^password_change_done/$',
        auth_views.PasswordChangeDoneView.as_view(
            template_name="password_change_done.html"
        ),
        name="password_change_done"
    ),
    path("", include("django_registration.backends.activation.urls")),
]
