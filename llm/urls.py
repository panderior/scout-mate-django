from django.urls import path
from .views import hello, scout, chat_response

urlpatterns = [
    path('hello/', hello, name="hello"),
    path('scout/', scout, name="scout"),
]