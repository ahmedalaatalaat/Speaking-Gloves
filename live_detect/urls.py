from django.urls import path
from . import views

app_name = "live_detect"

urlpatterns = [
    path('', views.video_feed, name='video_feed'),
    path('h/', views.home, name='home'),
    path('index/', views.index, name="index"),
    path("index/<str:room_name>/", views.room, name="room"),
]