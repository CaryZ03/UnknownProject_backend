from django.urls import path
from .views import *

urlpatterns = [
    path('upload_file', upload_file, name='upload_file'),
    path('download_file', download_file, name='download_file'),
    path('upload_saved_document', upload_saved_document, name='upload_saved_document'),
    path('create_document', create_document, name='create_document'),
    path('download_saved_document', download_saved_document, name='download_saved_document'),
    path('delete_document_all', delete_document_all, name='delete_document_all'),
    path('callback_document', callback_document, name='callback_document'),
    path('show_save', show_save, name='show_save'),
    path('search_save', search_save, name='search_save'),
]
