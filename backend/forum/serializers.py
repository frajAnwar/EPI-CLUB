from rest_framework import serializers
from .models import ForumPost, Comment
from accounts.serializers import UserSerializer

class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'author', 'content', 'created_at')

class ForumPostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = ForumPost
        fields = ('id', 'author', 'title', 'content', 'created_at', 'updated_at', 'comments')
