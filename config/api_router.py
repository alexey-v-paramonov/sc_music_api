from django.urls import path
from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

# from streaming_center_music_api.users.api.views import UserViewSet
from streaming_center_music_api.music.views import MusicAPI

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

# router.register("users", UserViewSet)
# router.register("music", MusicAPI.as_view())


app_name = "api"
urlpatterns = [
    path('music/', MusicAPI.as_view()),
]
