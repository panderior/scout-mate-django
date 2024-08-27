from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat, name='chat'),
    path('chat_response/', views.chat_response, name='chat_response')
]