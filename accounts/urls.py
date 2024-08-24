from django.contrib.auth.views import LogoutView
from django.urls import path

from .views import (
    ChangeEmailView,
    ConfirmEmailView,
    CustomPasswordChangeView,
    DeleteView,
    LoginView,
    RegView,
)

app_name = "accounts"


urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("registration/", RegView.as_view(), name="registration"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("change-email/", ChangeEmailView.as_view(), name="change_email"),
    path(
        "change-password/", CustomPasswordChangeView.as_view(), name="change_password"
    ),
    path("delete/", DeleteView.as_view(), name="delete"),
    path(
        "confirm-email/<uidb64>/<token>/",
        ConfirmEmailView.as_view(),
        name="confirm_email",
    ),
]
