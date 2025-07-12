from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import Achievement, UserAchievement
from accounts.models import User

class AchievementAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='testuser@example.com', username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)
        self.achievement = Achievement.objects.create(name='Test Achievement', description='Test Description', unlock_condition='test')
        self.user_achievement = UserAchievement.objects.create(user=self.user, achievement=self.achievement)

    def test_get_achievements(self):
        url = reverse('achievement-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], self.achievement.name)

    def test_get_user_achievements(self):
        url = reverse('userachievement-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['achievement']['name'], self.achievement.name)
