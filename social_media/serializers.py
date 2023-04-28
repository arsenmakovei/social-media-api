from rest_framework import serializers

from social_media.models import Profile, Follow


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


class FollowerListSerializer(serializers.ModelSerializer):
    follower = serializers.CharField(
        source="follower.username", read_only=True
    )

    class Meta:
        model = Follow
        fields = ("id", "follower")


class FollowingListSerializer(serializers.ModelSerializer):
    following = serializers.CharField(
        source="following.username", read_only=True
    )

    class Meta:
        model = Follow
        fields = ("id", "following")
