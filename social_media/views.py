from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from social_media.models import Profile, Follow
from social_media.serializers import (
    ProfileSerializer,
    FollowingListSerializer,
    FollowerListSerializer,
)


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.select_related("user")
    serializer_class = ProfileSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = self.queryset
        username = self.request.query_params.get("username")

        if username:
            queryset = queryset.filter(username__icontains=username)

        return queryset.distinct()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        if instance.user == self.request.user:
            instance.delete()
        else:
            raise PermissionDenied(
                "You do not have permission to delete this profile."
            )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "username",
                type=OpenApiTypes.STR,
                description="Filter by user username (ex. ?username=dicaprio)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(detail=True, methods=["POST"])
    def follow(self, request, pk=None):
        follower = self.request.user.profile
        following = self.get_object()

        if follower == following:
            return Response({"detail": "You cannot follow yourself."})

        follow, created = Follow.objects.get_or_create(
            follower=follower, following=following
        )

        if not created:
            return Response({"detail": "You are already following this user."})

        return Response(
            {"detail": f"You are now following {following.full_name}."}
        )

    @action(detail=True, methods=["POST"])
    def unfollow(self, request, pk=None):
        follower = self.request.user.profile
        following = self.get_object()

        follow = Follow.objects.filter(
            follower=follower, following=following
        ).first()

        if follower == following:
            return Response({"detail": "You cannot unfollow yourself."})

        if not follow:
            return Response({"detail": "You are not following this user."})

        follow.delete()

        return Response(
            {"detail": f"You have unfollowed {following.full_name}."}
        )

    @action(detail=True, methods=["GET"])
    def followers(self, request, pk=None):
        profile = self.get_object()
        serializer = FollowerListSerializer(profile.followers.all(), many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["GET"])
    def following(self, request, pk=None):
        profile = self.get_object()
        serializer = FollowingListSerializer(
            profile.following.all(), many=True
        )
        return Response(serializer.data)
