from django.urls import path
from .views import *

urlpatterns = [
    path('upload_file', upload_file, name='upload_file'),
    path('download_file', download_file, name='download_file'),
    path('upload_saved_document', upload_saved_document, name='upload_saved_document'),
    path('create_document', create_document, name='create_document'),
    path('download_saved_document', download_saved_document, name='download_saved_document'),
]
