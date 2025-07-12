from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import Conversation, DirectMessage
from accounts.models import User

class MessagingAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(email='user1@example.com', username='user1', password='testpassword')
        self.user2 = User.objects.create_user(email='user2@example.com', username='user2', password='testpassword')
        self.client.force_authenticate(user=self.user1)
        self.conversation = Conversation.objects.create()
        self.conversation.participants.add(self.user1, self.user2)

    def test_get_conversations(self):
        url = reverse('conversation-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_get_messages_in_conversation(self):
        DirectMessage.objects.create(conversation=self.conversation, sender=self.user1, content='Hello')
        url = reverse('message-list') + f'?conversation_id={self.conversation.id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_send_message(self):
        url = reverse('message-list')
        data = {'conversation_id': self.conversation.id, 'content': 'Hi there'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DirectMessage.objects.count(), 1)

    def test_message_notification(self):
        url = reverse('message-list')
        data = {'conversation_id': self.conversation.id, 'content': 'Hello user2!'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Check that user2 received a notification
        notifications = self.user2.notifications.filter(message__icontains='New message')
        self.assertTrue(notifications.exists())
