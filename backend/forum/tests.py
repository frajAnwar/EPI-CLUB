from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import ForumPost, Comment
from accounts.models import User

class ForumAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='testuser@example.com', username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)
        self.post = ForumPost.objects.create(author=self.user, title='Test Post', content='Test Content')

    def test_get_posts(self):
        url = reverse('post-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_create_post(self):
        url = reverse('post-list')
        data = {'title': 'New Post', 'content': 'Some content'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ForumPost.objects.count(), 2)

    def test_get_single_post(self):
        url = reverse('post-detail', kwargs={'pk': self.post.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.post.title)

    def test_create_comment(self):
        url = reverse('post-comments-list', kwargs={'post_pk': self.post.pk})
        data = {'content': 'A comment'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 1)

    def test_get_comments_for_post(self):
        Comment.objects.create(post=self.post, author=self.user, content='A comment')
        url = reverse('post-comments-list', kwargs={'post_pk': self.post.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_mention_notification(self):
        mentioned_user = User.objects.create_user(email='mention@example.com', username='mention', password='testpassword')
        url = reverse('post-comments-list', kwargs={'post_pk': self.post.pk})
        data = {'content': 'Hello @mention!'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Check that the mentioned user received a notification
        notifications = mentioned_user.notifications.filter(message__icontains='mentioned')
        self.assertTrue(notifications.exists())
