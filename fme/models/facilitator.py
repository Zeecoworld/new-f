from django.db import models
from fme.models.user import User
from fme.models.base import BaseModel

class FacilitatorProfile(BaseModel):
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
