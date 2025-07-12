from django.utils import timezone
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Quest, UserQuest
from .serializers import QuestSerializer, UserQuestSerializer

from notifications.utils import send_user_notification
from accounts.models import Currency, UserCurrency

class QuestViewSet(viewsets.ModelViewSet):
    queryset = Quest.objects.all().order_by('id')
    serializer_class = QuestSerializer

    @action(detail=False, methods=['get'], url_path='user-quests')
    def user_quests(self, request):
        user_quests = UserQuest.objects.filter(user=request.user)
        serializer = UserQuestSerializer(user_quests, many=True)
        return Response(serializer.data)

class UserQuestViewSet(viewsets.ModelViewSet):
    serializer_class = UserQuestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserQuest.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'], url_path='onboarding')
    def onboarding(self, request):
        onboarding_quest = Quest.objects.get(id=1) # Assuming onboarding quest has id=1
        user_quest, created = UserQuest.objects.get_or_create(user=request.user, quest=onboarding_quest)
        serializer = self.get_serializer(user_quest)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        user_quest = self.get_object()
        if user_quest.is_completed:
            return Response({'error': 'Quest already completed.'}, status=400)

        user_quest.is_completed = True
        user_quest.completed_at = timezone.now()
        user_quest.save()

        # Grant rewards
        user = request.user
        user.xp += user_quest.quest.reward_xp
        user.save()

        # Assume first currency is the primary one
        primary_currency = Currency.objects.first()
        if primary_currency:
            user_currency, created = UserCurrency.objects.get_or_create(
                user=user,
                currency=primary_currency
            )
            user_currency.balance += user_quest.quest.reward_currency
            user_currency.save()

        message = f"You have completed the quest '{user_quest.quest.title}' and earned {user_quest.quest.reward_xp} XP and {user_quest.quest.reward_currency} {primary_currency.name}!"
        send_user_notification(user, message)

        return Response(self.get_serializer(user_quest).data)
