from django.db import models
from django.conf import settings

class Quest(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    reward_xp = models.PositiveIntegerField(default=0)
    reward_currency = models.PositiveIntegerField(default=0)
    is_real_world = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class UserQuest(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    quest = models.ForeignKey(Quest, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    steps_completed = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'{self.user.username} - {self.quest.title}'
