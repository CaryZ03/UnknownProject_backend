from django.urls import path
from .views import *

urlpatterns = [
    path('upload_file', upload_file, name='upload_file'),
    path('download_file', download_file, name='download_file'),
]
