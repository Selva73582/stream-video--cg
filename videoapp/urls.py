from django.urls import path
from . import views

urlpatterns = [
    path('', views.video_list, name='video_list'),  # List all videos
    path('upload/', views.upload_video, name='upload'),  # Upload a new video
    path('video/<int:video_id>/', views.play_video, name='play_video'),  # Play a specific video
]
