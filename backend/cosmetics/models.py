from django.db import models
from django.conf import settings

class ProfileBanner(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='cosmetics/banners/')
    cost = models.PositiveIntegerField(default=0, help_text="Cost in in-game currency")
    is_unlockable = models.BooleanField(default=False, help_text="Can be unlocked via achievements, etc.")

    def __str__(self):
        return self.name

class UserBanner(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='banners')
    banner = models.ForeignKey(ProfileBanner, on_delete=models.CASCADE)
    unlocked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'banner')

    def __str__(self):
        return f"{self.user.username} - {self.banner.name}"
