from rest_framework import serializers
from fme.serializers.base import BaseSerializer
from fme.models.facilitator import FacilitatorProfile
from fme.serializers.authentication import UserSerializer
from fme.serializers.authentication import BaseUserSerializer

class FacilitatorInvitationSerializer(BaseUserSerializer):
    specialization = serializers.CharField(max_length=100)
    highest_qualification = serializers.CharField(max_length=100)
    institution = serializers.CharField(max_length=100)
    areas_of_expertise = serializers.CharField()



# class FacilitatorProfileSerializer(serializers.ModelSerializer):
#     user = UserSerializer(read_only=True)
#     rating = serializers.DecimalField(max_digits=3, decimal_places=1, read_only=True)
    
#     class Meta:
#         model = FacilitatorProfile
#         fields = [
#             'user', 'specialization', 'years_of_experience',
#             'highest_qualification', 'institution', 'areas_of_expertise',
#             'students_count', 'completed_sessions', 'rating'
#         ]
#         read_only_fields = ['students_count', 'completed_sessions', 'rating']
