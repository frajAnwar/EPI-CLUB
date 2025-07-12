from rest_framework import viewsets, permissions
from .models import ForumPost, Comment
from .serializers import ForumPostSerializer, CommentSerializer

class ForumPostViewSet(viewsets.ModelViewSet):
    queryset = ForumPost.objects.all().order_by('id')
    serializer_class = ForumPostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Comment.objects.filter(post_id=self.kwargs['post_pk'])

    def perform_create(self, serializer):
        from notifications.utils import send_user_notification
        comment = serializer.save(author=self.request.user, post_id=self.kwargs['post_pk'])
        post_author = comment.post.author
        if post_author != self.request.user:
            message = f"{self.request.user.username} replied to your forum post: '{comment.post.title}'"
            send_user_notification(post_author, message)
        # Mention notifications for @username in comment text
        import re
        from accounts.models import User
        mentioned_usernames = set(re.findall(r'@([\w-]+)', comment.content or ''))
        for username in mentioned_usernames:
            try:
                mentioned_user = User.objects.get(username=username)
                if mentioned_user != self.request.user and mentioned_user != post_author:
                    mention_message = f"You were mentioned by {self.request.user.username} in a comment on '{comment.post.title}'."
                    send_user_notification(mentioned_user, mention_message)
            except User.DoesNotExist:
                continue
