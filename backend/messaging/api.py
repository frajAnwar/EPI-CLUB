from rest_framework import viewsets, permissions
from .models import Conversation, DirectMessage
from .serializers import ConversationSerializer, DirectMessageSerializer

class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.request.user.conversations.all()

class DirectMessageViewSet(viewsets.ModelViewSet):
    serializer_class = DirectMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return DirectMessage.objects.filter(conversation__participants=self.request.user)

    def perform_create(self, serializer):
        from notifications.utils import send_user_notification
        conversation = Conversation.objects.get(id=self.request.data['conversation_id'])
        message = serializer.save(sender=self.request.user, conversation=conversation)
        # Notify all participants except the sender
        for participant in conversation.participants.exclude(id=self.request.user.id):
            notif_message = f"New message from {self.request.user.username} in your conversation."
            send_user_notification(participant, notif_message)
