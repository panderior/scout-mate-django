from django.urls import path
from .views import ScoutDataPersistingAPI, ScoutResultsAPI, chat_response

urlpatterns = [
    path('', ScoutDataPersistingAPI.get_home_page, name="home"),
    path('scout/<int:id>/', ScoutResultsAPI.get_scout_page, name="scout"),
    path('upload/', ScoutDataPersistingAPI.scout_data_upload, name="data-upload"),
    path('chat_msg/', ScoutResultsAPI.scouty_chat, name="scouty-chat"),
    path('scout/chat/', chat_response, name="chat_response"),
]