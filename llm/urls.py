from django.urls import path
from .views import ScoutDataPersistingAPI, ScoutResultsAPI

urlpatterns = [
    path('', ScoutDataPersistingAPI.get_home_page, name="home"),
    path('scout/', ScoutResultsAPI.get_scout_page, name="scout"),
    path('upload/', ScoutDataPersistingAPI.scout_data_upload, name="data-upload"),
]