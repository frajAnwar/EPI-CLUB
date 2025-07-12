from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import Event
from accounts.models import User

class EventAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)
        self.event = Event.objects.create(name='Test Event', description='Test Description', created_by=self.user)

    def test_get_events(self):
        url = reverse('event-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], self.event.name)

    def test_create_event(self):
        url = reverse('event-list')
        data = {'name': 'New Event', 'description': 'A new event'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Event.objects.count(), 2)

    def test_get_single_event(self):
        url = reverse('event-detail', kwargs={'pk': self.event.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.event.name)

    def test_update_event(self):
        url = reverse('event-detail', kwargs={'pk': self.event.pk})
        data = {'name': 'Updated Event'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.event.refresh_from_db()
        self.assertEqual(self.event.name, 'Updated Event')

    def test_delete_event(self):
        url = reverse('event-detail', kwargs={'pk': self.event.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Event.objects.count(), 0)

class TournamentAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)
        self.game = Game.objects.create(name='Test Game', team_size=5)
        self.team1 = Team.objects.create(name='Team 1', game=self.game, created_by=self.user)
        self.team2 = Team.objects.create(name='Team 2', game=self.game, created_by=self.user)
        self.tournament = Tournament.objects.create(name='Test Tournament', game=self.game, organizer=self.user, reward_currency=1000)
        self.round = Round.objects.create(tournament=self.tournament, round_number=1)
        self.match = Match.objects.create(round=self.round, team1=self.team1, team2=self.team2)

    def test_set_match_winner_and_grant_rewards(self):
        url = reverse('match-set-result', kwargs={'pk': self.match.pk})
        data = {'winner_id': self.team1.pk, 'score': '2-0'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.tournament.refresh_from_db()
        self.assertEqual(self.tournament.winner, self.team1)
        primary_currency = Currency.objects.first()
        if primary_currency:
            for member in self.team1.members.all():
                user_currency = UserCurrency.objects.get(user=member, currency=primary_currency)
                self.assertEqual(user_currency.balance, 1000)
