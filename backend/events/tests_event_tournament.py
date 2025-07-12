from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from accounts.models import User, Game
from teams.models import Team
from events.models import Event, Tournament, Participant, TournamentAttendanceReward

class EventTournamentFlowTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(email='admin@example.com', username='admin', password='admin', is_admin=True)
        self.leader = User.objects.create_user(email='leader@example.com', username='leader', password='leader')
        self.member = User.objects.create_user(email='member@example.com', username='member', password='member')
        self.game = Game.objects.create(name='CSGO', team_size=2)
        self.event = Event.objects.create(name='LAN Party', description='Fun event', start_time='2030-01-01T10:00', end_time='2030-01-01T20:00', created_by=self.admin)
        self.tournament = Tournament.objects.create(name='CSGO Cup', event=self.event, game=self.game, start_date='2030-01-01', end_date='2030-01-01', organizer=self.admin)
        self.team = Team.objects.create(name='TeamA', created_by=self.leader, game=self.game)
        self.team.members.add(self.leader, self.member)

    def test_event_creation_and_tournament_linking(self):
        self.assertEqual(self.tournament.event, self.event)
        self.assertEqual(self.tournament.game, self.game)

    def test_team_application_leader_only_and_team_size(self):
        url = reverse('tournament-apply', args=[self.tournament.id])
        # Not leader
        self.client.force_authenticate(user=self.member)
        resp = self.client.post(url, {'team_id': self.team.id})
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        # Wrong team size
        self.team.members.remove(self.member)
        self.client.force_authenticate(user=self.leader)
        resp = self.client.post(url, {'team_id': self.team.id})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        # Correct
        self.team.members.add(self.member)
        resp = self.client.post(url, {'team_id': self.team.id})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(Participant.objects.filter(tournament=self.tournament, team=self.team).exists())

    def test_admin_approve_reject_team(self):
        # Apply first
        self.team.members.add(self.member)
        self.client.force_authenticate(user=self.leader)
        self.client.post(reverse('tournament-apply', args=[self.tournament.id]), {'team_id': self.team.id})
        participant = Participant.objects.get(tournament=self.tournament, team=self.team)
        # Approve
        self.client.force_authenticate(user=self.admin)
        resp = self.client.post(reverse('tournament-approve-application', args=[self.tournament.id, participant.id]))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        participant.refresh_from_db()
        self.assertTrue(participant.is_approved)

    def test_attendance_and_per_member_reward(self):
        # Apply and approve
        self.team.members.add(self.member)
        self.client.force_authenticate(user=self.leader)
        self.client.post(reverse('tournament-apply', args=[self.tournament.id]), {'team_id': self.team.id})
        participant = Participant.objects.get(tournament=self.tournament, team=self.team)
        self.client.force_authenticate(user=self.admin)
        self.client.post(reverse('tournament-approve-application', args=[self.tournament.id, participant.id]))
        # Grant reward to member
        resp = self.client.post(reverse('tournament-grant-reward', args=[self.tournament.id, participant.id]), {'member_id': self.member.id, 'reward_xp': 100, 'reward_currency': 50})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(TournamentAttendanceReward.objects.filter(tournament=self.tournament, user=self.member).exists())
