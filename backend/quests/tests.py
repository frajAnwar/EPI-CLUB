from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import Quest, UserQuest
from accounts.models import User, Currency, UserCurrency

class QuestAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='testpassword')
        self.client.force_authenticate(user=self.user)
        self.currency = Currency.objects.create(name='Gold')
        self.quest = Quest.objects.create(title='Test Quest', description='Test Description', reward_xp=100, reward_currency=50)
        self.user_quest = UserQuest.objects.create(user=self.user, quest=self.quest)

    def test_complete_quest(self):
        url = reverse('userquest-complete', kwargs={'pk': self.user_quest.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.user_quest.refresh_from_db()
        self.assertEqual(self.user.xp, 100)
        self.assertEqual(self.user_quest.is_completed, True)
        user_currency = UserCurrency.objects.get(user=self.user, currency=self.currency)
        self.assertEqual(user_currency.balance, 50)
