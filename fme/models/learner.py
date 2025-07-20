from django.db import models
from fme.helpers import options
from fme.models.user import User
from fme.models.base import BaseModel
from django.db import IntegrityError, transaction

class LearnerProfile(BaseModel):
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

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='learner_profile')
    account_type = models.CharField(max_length=20, choices=AccountType.choices)
    learning_track = models.CharField(max_length=100)
    skill_cluster = models.CharField(max_length=100)
    work_type = models.CharField(max_length=20, choices=WorkType.choices)
    industrial_prefrence = models.CharField(max_length=100)
    portfolio_link = models.URLField(blank=True, null=True)
    state = models.CharField(max_length=25, choices=options.STATE)
    gender = models.CharField(max_length=20, choices=Gender.choices)
    resume = models.CharField(max_length=200, blank=True, null=True)
    # resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    
    # Progress tracking
    # current_pathway = models.ForeignKey('Pathway', on_delete=models.SET_NULL, null=True, blank=True)
    progress = models.PositiveIntegerField(default=0)  # Percentage
    
    def __str__(self):
        return f"{self.user.get_full_name()} (Learner)"

    @classmethod
    def create_profile(cls, payload):
        profile = None
        try:
            with transaction.atomic():
                user_instance = User.objects.create(**payload['user'])
                profile = cls.objects.create(user=user_instance, **payload['profile'])
        except IntegrityError:
            print('An IntegrityError occured while creating user and learner')
        except Exception as e:
            print('An error occur while trying to create learner profile: reason', e)
        return profile
