from django.db import models
from django.contrib.auth import get_user_model

class Permission(models.Model):
    codename = models.CharField(max_length=100, unique=True, help_text="e.g., can_edit_news")
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)
    permissions = models.ManyToManyField(Permission, blank=True)

    def __str__(self):
        return self.name

# Add a many-to-many relationship from User to Role
User = get_user_model()
User.add_to_class('roles', models.ManyToManyField(Role, blank=True, related_name='users'))

# Helper function to check permissions
def has_permission(user, codename):
    if user.is_superuser or user.is_admin:
        return True
    return user.roles.filter(permissions__codename=codename).exists()
