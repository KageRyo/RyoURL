from django.urls import path
from .views import redirectShortUrl

urlpatterns = [
    path('', redirectShortUrl, name='redirectShortUrl'),
]