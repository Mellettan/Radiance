from django.urls import path

from posts.views import HomeView

app_name = 'posts'


urlpatterns = [
    path('<int:pk>/', HomeView.as_view(), name='home'),
]
