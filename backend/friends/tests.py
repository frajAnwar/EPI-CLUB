from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import Friendship
from accounts.models import User

class FriendshipAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(email='user1@example.com', username='user1', password='testpassword')
        self.user2 = User.objects.create_user(email='user2@example.com', username='user2', password='testpassword')
        self.client.force_authenticate(user=self.user1)

    def test_send_friend_request(self):
        url = reverse('friends:friendship-list')
        data = {'to_user': self.user2.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Friendship.objects.count(), 1)

    def test_accept_friend_request(self):
        friend_request = Friendship.objects.create(from_user=self.user1, to_user=self.user2)
        self.client.force_authenticate(user=self.user2)
        url = reverse('friends:friendship-accept', kwargs={'pk': friend_request.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        friend_request.refresh_from_db()
        self.assertTrue(friend_request.is_accepted)

    def test_decline_friend_request(self):
        friend_request = Friendship.objects.create(from_user=self.user1, to_user=self.user2)
        self.client.force_authenticate(user=self.user2)
        url = reverse('friends:friendship-decline', kwargs={'pk': friend_request.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Friendship.objects.count(), 0)

    def test_get_friends_list(self):
        Friendship.objects.create(from_user=self.user1, to_user=self.user2, is_accepted=True)
        url = reverse('friends:friendship-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_get_friend_requests(self):
        Friendship.objects.create(from_user=self.user1, to_user=self.user2)
        self.client.force_authenticate(user=self.user2)
        url = reverse('friends:friendship-requests')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
