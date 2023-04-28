from django.urls import path, include
from rest_framework import routers

from social_media.views import ProfileViewSet

router = routers.DefaultRouter()
router.register("profiles", ProfileViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path(
        "profiles/<int:pk>/follow/",
        ProfileViewSet.as_view({"post": "follow"}),
        name="follow-user",
    ),
    path(
        "profiles/<int:pk>/unfollow/",
        ProfileViewSet.as_view({"post": "unfollow"}),
        name="unfollow-user",
    ),
]

app_name = "social_media"
