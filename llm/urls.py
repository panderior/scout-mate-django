from django.urls import path
from .views import hello, scout

urlpatterns = [
    path('hello/', hello, name="hello"),
    path('scout/', scout, name="scout"),
]