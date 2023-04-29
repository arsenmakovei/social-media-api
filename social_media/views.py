from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from social_media.models import Profile, Follow, Post, Like, Comment
from social_media.serializers import (
    ProfileSerializer,
    FollowingListSerializer,
    FollowerListSerializer,
    PostSerializer,
    FollowRequestSerializer,
    LikeRequestSerializer,
    LikeListSerializer,
    PostListSerializer,
    CommentSerializer,
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

    @action(
        detail=True, methods=["POST"], serializer_class=FollowRequestSerializer
    )
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

    @action(
        detail=True, methods=["POST"], serializer_class=FollowRequestSerializer
    )
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

    @action(detail=True, methods=["GET"])
    def posts(self, request, pk=None):
        profile = self.get_object()
        posts = Post.objects.filter(author=profile)
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["GET"])
    def following_posts(self, request, pk=None):
        profile = self.get_object()
        followings = profile.followers.all()
        posts = Post.objects.filter(author__following__in=followings)
        serializer = PostListSerializer(posts, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["GET"])
    def liked_posts(self, request, pk=None):
        profile = self.get_object()
        likes = profile.likes.all()
        serializer = LikeListSerializer(likes, many=True)
        return Response(serializer.data)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.select_related("author")
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = self.queryset
        name = self.request.query_params.get("name")

        if name:
            queryset = queryset.filter(name__icontains=name)

        return queryset.distinct()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user.profile)

    def perform_update(self, serializer):
        post = self.get_object()
        if post.author == self.request.user.profile:
            serializer.save(author=self.request.user.profile)
        else:
            raise PermissionDenied(
                "You do not have permission to update this post."
            )

    def perform_destroy(self, instance):
        if instance.author == self.request.user.profile:
            instance.delete()
        else:
            raise PermissionDenied(
                "You do not have permission to delete this post."
            )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "name",
                type=OpenApiTypes.STR,
                description="Filter by post name (ex. ?name=the)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(
        detail=True, methods=["POST"], serializer_class=LikeRequestSerializer
    )
    def like(self, request, pk=None):
        profile = self.request.user.profile
        post = self.get_object()

        like, created = Like.objects.get_or_create(profile=profile, post=post)

        if not created:
            return Response({"detail": "You have already liked this post."})

        return Response({"detail": f"You are liked {post.name} now."})

    @action(
        detail=True, methods=["POST"], serializer_class=LikeRequestSerializer
    )
    def unlike(self, request, pk=None):
        profile = self.request.user.profile
        post = self.get_object()

        like = Like.objects.filter(profile=profile, post=post).first()

        if not like:
            return Response({"detail": "You have not liked this post."})

        like.delete()

        return Response({"detail": f"You have unliked {post.name}."})

    @action(detail=True, methods=["GET"])
    def comments(self, request, pk=None):
        post = self.get_object()
        comments = post.comments.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["POST"], serializer_class=CommentSerializer)
    def add_comment(self, request, pk=None):
        post = self.get_object()
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(profile=request.user.profile, post=post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        detail=True,
        methods=["PUT"],
        url_path="update_comment/(?P<comment_pk>[^/.]+)",
        serializer_class=CommentSerializer,
    )
    def update_comment(self, request, pk=None, comment_pk=None):
        comment = Comment.objects.get(pk=comment_pk)
        serializer = CommentSerializer(
            comment, data=request.data, partial=True
        )

        if comment.profile != self.request.user.profile:
            return Response(status=status.HTTP_403_FORBIDDEN)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        detail=True,
        methods=["DELETE"],
        url_path="delete_comment/(?P<comment_pk>[^/.]+)",
        serializer_class=CommentSerializer,
    )
    def delete_comment(self, request, pk=None, comment_pk=None):
        comment = Comment.objects.get(pk=comment_pk)

        if comment.profile != self.request.user.profile:
            return Response(status=status.HTTP_403_FORBIDDEN)

        comment.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
