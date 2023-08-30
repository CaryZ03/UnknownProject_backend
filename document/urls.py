from django.urls import path
from .views import *

urlpatterns = [
    path('upload_file', upload_file, name='upload_file'),
    path('download_file', download_file, name='download_file'),
    path('upload_saved_document', upload_saved_document, name='upload_saved_document'),
    path('create_document', create_document, name='create_document'),
    path('download_saved_document', download_saved_document, name='download_saved_document'),
    path('show_document_list', show_document_list, name='show_document_list'),
    path('delete_document', delete_document, name='delete_document'),
    path('callback_document', callback_document, name='callback_document'),
    path('show_save', show_save, name='show_save'),
    path('search_save', search_save, name='search_save'),
    path('show_prototype_list', show_prototype_list, name='show_prototype_list'),
    path('upload_prototype', upload_prototype, name='upload_prototype'),
    path('create_prototype', create_prototype, name='create_prototype'),
    path('delete_prototype', delete_prototype, name='delete_prototype'),
    path('search_prototype', search_prototype, name='search_prototype'),
    path('change_prototype', change_prototype, name='change_prototype'),
    path('change_document', change_document, name='change_document'),
]
