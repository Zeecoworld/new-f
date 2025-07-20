from django.db import models
from fme.models.user import User
from fme.models.base import BaseModel

class MentorProfile(BaseModel):
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
