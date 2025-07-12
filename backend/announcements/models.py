from django.db import models
from accounts.models import User

class Announcement(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    image_url = models.URLField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='announcements_created')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
