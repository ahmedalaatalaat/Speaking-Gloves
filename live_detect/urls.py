from django.urls import path
from . import views

app_name = "live_detect"

urlpatterns = [
    path('', views.video_feed, name='video_feed'),
]