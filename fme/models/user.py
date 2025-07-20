from django.db import models
from fme.models.base import BaseModel
from django.contrib.auth.models import AbstractUser

class User(AbstractUser, BaseModel):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrator'
        SCHOOL_ADMIN = 'SCHOOL_ADMIN', 'School Administrator'
        LEARNER = 'LEARNER', 'Learner'
        MENTOR = 'MENTOR', 'Mentor'
        FACILITATOR = 'FACILITATOR', 'Facilitator'
    
    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        INACTIVE = 'INACTIVE', 'Inactive'
        DISABLED = 'DISABLED', 'Disabled'
    
    # # date fields
    # date_created = models.DateTimeField(auto_now_add=True, verbose_name="date_created", db_index=True)
    # date_updated = models.DateTimeField(auto_now=True, verbose_name="date_updated", db_index=True)

    # Common fields
    role = models.CharField(max_length=20, choices=Role.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DISABLED)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    last_active = models.DateTimeField(auto_now=True)
    
    # Remove unused fields from AbstractUser
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)

    # Set email as the username field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        indexes = [
            models.Index(fields=['role']),
            models.Index(fields=['status']),
            models.Index(fields=['last_active']),
        ]

    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"
    
    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN
    
    @property
    def is_learner(self):
        return self.role == self.Role.LEARNER
    
    @property
    def is_mentor(self):
        return self.role == self.Role.MENTOR
    
    @property
    def is_facilitator(self):
        return self.role == self.Role.FACILITATOR
