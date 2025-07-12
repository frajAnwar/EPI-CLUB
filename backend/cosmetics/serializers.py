from rest_framework import serializers
from .models import ProfileBanner, UserBanner

class ProfileBannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileBanner
        fields = ('id', 'name', 'description', 'image', 'cost', 'is_unlockable')

class UserBannerSerializer(serializers.ModelSerializer):
    banner = ProfileBannerSerializer(read_only=True)

    class Meta:
        model = UserBanner
        fields = ('banner', 'unlocked_at')
