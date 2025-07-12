from rest_framework import serializers
from .models import Friendship
from accounts.serializers import UserSerializer

class FriendshipSerializer(serializers.ModelSerializer):
    from_user = UserSerializer(read_only=True)
    to_user = UserSerializer(read_only=True)

    class Meta:
        model = Friendship
        fields = ('id', 'from_user', 'to_user', 'is_accepted', 'created_at')
