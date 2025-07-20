from fme.models.user import User
from rest_framework import serializers
from fme.models.mentor import MentorProfile
from fme.serializers.authentication import UserSerializer, UserCreateSerializer

class MentorProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    rating = serializers.DecimalField(max_digits=3, decimal_places=1, read_only=True)
    
    class Meta:
        model = MentorProfile
        fields = [
            'user', 'company', 'role_at_company', 'country', 'state',
            'specialization', 'highest_qualification', 'institution',
            'areas_of_expertise', 'current_mentees_count',
            'overall_mentees_count', 'completed_sessions', 'rating'
        ]
        read_only_fields = [
            'current_mentees_count', 'overall_mentees_count',
            'completed_sessions', 'rating'
        ]

class MentorWithProfileCreateSerializer(serializers.Serializer):
    user = UserCreateSerializer()
    company = serializers.CharField(max_length=100)
    role_at_company = serializers.CharField(max_length=100)
    country = serializers.CharField(max_length=100)
    state = serializers.CharField(max_length=100)
    specialization = serializers.CharField(max_length=100)
    highest_qualification = serializers.CharField(max_length=100)
    institution = serializers.CharField(max_length=100)
    areas_of_expertise = serializers.CharField()
    
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user_serializer = UserCreateSerializer(data=user_data)
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save(role=User.Role.MENTOR)
        
        return MentorProfile.objects.create(
            user=user,
            **validated_data,
            current_mentees_count=0,
            overall_mentees_count=0,
            completed_sessions=0,
            rating=0.0
        )
