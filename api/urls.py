from django.urls import path

from .views import search_events, upload_archive

urlpatterns = [
    path('upload/', upload_archive, name='upload_archive'),
    path('search/', search_events, name='search_events'),
]
