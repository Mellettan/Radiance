from django.urls import path

from .views import UserInfoView

app_name = "userinfo"


urlpatterns = [
    path("", UserInfoView.as_view(), name="userinfo"),
]
