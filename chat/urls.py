from django.urls import path

from .views import ChatView

app_name = "chat"

urlpatterns = [
    path("<int:user_id>/", ChatView.as_view(), name="chat"),
]
