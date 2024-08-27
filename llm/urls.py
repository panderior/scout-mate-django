from django.urls import path
from .views import hello, scout, ScoutDataPersistingAPI

urlpatterns = [
    path('hello/', hello, name="hello"),
    path('scout/', scout, name="scout"),
    path('upload/', ScoutDataPersistingAPI.scout_data_upload, name="data-upload"),
]