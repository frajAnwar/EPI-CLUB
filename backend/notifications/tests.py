from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from .models import Notification

User = get_user_model()

class NotificationAPITests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.notification1 = Notification.objects.create(recipient=self.user, message='Test 1', read=False)
        self.notification2 = Notification.objects.create(recipient=self.user, message='Test 2', read=True)

    def test_mark_as_unread(self):
        url = reverse('notification-mark-as-unread', args=[self.notification2.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.notification2.refresh_from_db()
        self.assertFalse(self.notification2.read)

    def test_filter_read_notifications(self):
        url = reverse('notification-list') + '?read=true'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        ids = [n['id'] for n in response.data]
        self.assertIn(self.notification2.id, ids)
        self.assertNotIn(self.notification1.id, ids)

    def test_filter_unread_notifications(self):
        url = reverse('notification-list') + '?read=false'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        ids = [n['id'] for n in response.data]
        self.assertIn(self.notification1.id, ids)
        self.assertNotIn(self.notification2.id, ids)
