import uuid
from django.db import models
from fme.helpers import options
from django.contrib.auth.models import AbstractUser

class NinVerificationProcess(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date_created = models.DateTimeField(auto_now_add=True, verbose_name="date_created", db_index=True)
    date_updated = models.DateTimeField(auto_now=True, verbose_name="date_updated", db_index=True)
    nin = models.CharField(max_length=20, null=True, blank=True, db_index=True, unique=True)
    nin_detail = models.JSONField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, db_index=True)
    verification_token = models.CharField(max_length=10, db_index=True)

    class Meta:
        ordering = ("-date_updated",)
        app_label = "fme"


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrator'
        LEARNER = 'LEARNER', 'Learner'
        MENTOR = 'MENTOR', 'Mentor'
        FACILITATOR = 'FACILITATOR', 'Facilitator'
    
    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        INACTIVE = 'INACTIVE', 'Inactive'
        DISABLED = 'DISABLED', 'Disabled'
    
    # date fields
    date_created = models.DateTimeField(auto_now_add=True, verbose_name="date_created", db_index=True)
    date_updated = models.DateTimeField(auto_now=True, verbose_name="date_updated", db_index=True)

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



class LearnerProfile(models.Model):
    class AccountType(models.TextChoices):
        STUDENT = 'STUDENT', 'Student'
        PROFESSIONAL = 'PROFESSIONAL', 'Professional'
    
    class WorkType(models.TextChoices):
        ALL = 'ALL', 'All'
        ONSITE = 'ONSITE', 'Onsite'
        REMOTE = 'REMOTE', 'Remote'
    
    class Gender(models.TextChoices):
        MALE = 'MALE', 'Male'
        FEMALE = 'FEMALE', 'Female'
        
    date_created = models.DateTimeField(auto_now_add=True, verbose_name="date_created", db_index=True)
    date_updated = models.DateTimeField(auto_now=True, verbose_name="date_updated", db_index=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='learner_profile')
    account_type = models.CharField(max_length=20, choices=AccountType.choices)
    learning_track = models.CharField(max_length=100)
    skill_cluster = models.CharField(max_length=100)
    work_type = models.CharField(max_length=20, choices=WorkType.choices)
    industrial_preference = models.CharField(max_length=100)
    portfolio_link = models.URLField(blank=True, null=True)
    state = models.CharField(max_length=25, choices=options.STATE)
    gender = models.CharField(max_length=20, choices=Gender.choices)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    
    # Progress tracking
    # current_pathway = models.ForeignKey('Pathway', on_delete=models.SET_NULL, null=True, blank=True)
    progress = models.PositiveIntegerField(default=0)  # Percentage
    
    def __str__(self):
        return f"{self.user.get_full_name()} (Learner)"
    

class MentorProfile(models.Model):
    date_created = models.DateTimeField(auto_now_add=True, verbose_name="date_created", db_index=True)
    date_updated = models.DateTimeField(auto_now=True, verbose_name="date_updated", db_index=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='mentor_profile')
    # company = models.CharField(max_length=100) # may  be is institution
    role_at_company = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100)
    highest_qualification = models.CharField(max_length=100)
    institution = models.CharField(max_length=100)
    areas_of_expertise = models.TextField()
    
    # Mentorship stats
    current_mentees_count = models.PositiveIntegerField(default=0)
    overall_mentees_count = models.PositiveIntegerField(default=0)
    completed_sessions = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    
    def __str__(self):
        return f"{self.user.get_full_name()} (Mentor)"


class FacilitatorProfile(models.Model):
    date_created = models.DateTimeField(auto_now_add=True, verbose_name="date_created", db_index=True)
    date_updated = models.DateTimeField(auto_now=True, verbose_name="date_updated", db_index=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='facilitator_profile')
    specialization = models.CharField(max_length=100)
    years_of_experience = models.PositiveIntegerField()
    highest_qualification = models.CharField(max_length=100)
    institution = models.CharField(max_length=100)
    areas_of_expertise = models.TextField()
    
    # Teaching stats
    students_count = models.PositiveIntegerField(default=0)
    completed_sessions = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    
    def __str__(self):
        return f"{self.user.get_full_name()} (Facilitator)"
