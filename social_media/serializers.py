from rest_framework import serializers

from social_media.models import Profile, Follow, Post, Like, Comment


class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)
    date_joined = serializers.DateTimeField(
        source="user.date_joined", read_only=True
    )

    class Meta:
        model = Profile
        fields = (
            "id",
            "username",
            "avatar",
            "date_joined",
            "first_name",
            "last_name",
            "bio",
            "date_of_birth",
            "location",
            "email",
            "phone",
        )


class FollowRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ("id",)


class FollowerListSerializer(serializers.ModelSerializer):
    follower = serializers.CharField(
        source="follower.username", read_only=True
    )

    class Meta:
        model = Follow
        fields = ("follower",)


class FollowingListSerializer(serializers.ModelSerializer):
    following = serializers.CharField(
        source="following.username", read_only=True
    )

    class Meta:
        model = Follow
        fields = ("following",)


class PostSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source="author.username", read_only=True)

    class Meta:
        model = Post
        fields = ("id", "name", "author", "created_at", "image", "content")


class PostListSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source="author.username", read_only=True)

    class Meta:
        model = Post
        fields = ("name", "author")


class LikeRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ("id",)


class LikeListSerializer(serializers.ModelSerializer):
    profile = serializers.CharField(source="profile.username", read_only=True)
    post = serializers.CharField(source="post.name", read_only=True)

    class Meta:
        model = Like
        fields = ("profile", "post")


class CommentSerializer(serializers.ModelSerializer):
    profile = serializers.CharField(source="profile.username", read_only=True)
    post = serializers.CharField(source="post.name", read_only=True)

    class Meta:
        model = Comment
        fields = ("id", "post", "profile", "text", "created_at")
