from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import Item
from accounts.models import User, UserCurrency, Currency

class ShopPurchaseNotificationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='shopper@example.com', username='shopper', password='testpassword')
        self.currency = Currency.objects.create(name='Gold', code='G')
        self.user_currency = UserCurrency.objects.create(user=self.user, currency=self.currency, balance=1000)
        self.item = Item.objects.create(name='Sword', base_price=100)
        self.client.force_authenticate(user=self.user)

    def test_purchase_sends_notification(self):
        url = reverse('purchaseitemview')  # Update this to your actual route name if different
        data = {'item_id': self.item.id, 'quantity': 2}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check that the user received a notification
        notifications = self.user.notifications.filter(message__icontains='purchased')
        self.assertTrue(notifications.exists())
