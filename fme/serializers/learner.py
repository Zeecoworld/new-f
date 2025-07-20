from fme.helpers import options
from fme.models.user import  User
from rest_framework import serializers
from fme.models.learner import LearnerProfile
from fme.serializers.base import BaseSerializer
from fme.helpers.upload import upload_file_to_s3
from fme.serializers.authentication import UserSerializer
from fme.serializers.authentication import BaseUserSerializer

class CreateLearnerQueryParamSerializer(BaseSerializer):
    verification_id = serializers.UUIDField()

class CreateLearnerSerializer(BaseUserSerializer):
    account_type = serializers.ChoiceField(choices=LearnerProfile.AccountType.choices)
    learning_track = serializers.CharField(max_length=100)
    skill_cluster = serializers.CharField(max_length=100)
    work_type = serializers.ChoiceField(choices=LearnerProfile.WorkType.choices)
    industrial_prefrence = serializers.CharField(max_length=100)
    portfolio_link = serializers.CharField(max_length=100)
    state = serializers.ChoiceField(choices=options.STATE)
    gender = serializers.ChoiceField(choices=LearnerProfile.Gender.choices)
    resume = serializers.FileField(write_only=True, allow_null=True, required=False)
    resume_url = serializers.CharField(read_only=True)

    def to_internal_value(self, data):
        validated_data = super().to_internal_value(data)
        resume_file = data.get('resume')
        if resume_file:
            file_name = f"resume/{resume_file.name}"
            resume_url = upload_file_to_s3(resume_file, file_name)
            validated_data['resume_url'] = resume_url
        else:
            validated_data['resume_url'] = None
        return validated_data

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return {
            'user':{
                'first_name':data['first_name'],
                'last_name':data['last_name'],
                'email':data['email'],
                'phone_number':data['phone_number'],
                'role':User.Role.LEARNER,
                'status':User.Status.ACTIVE,
                'is_active': True
            },
            'profile':{
                'account_type':data['account_type'],
                'learning_track':data['learning_track'],
                'skill_cluster':data['skill_cluster'],
                'work_type':data['work_type'],
                'industrial_prefrence':data['industrial_prefrence'],
                'portfolio_link':data['portfolio_link'],
                'state':data['state'],
                'gender':data['gender'],
                'resume':data.get('resume_url')
            }
        }

class LearnerProfileSerializer(serializers.ModelSerializer):
    account_type = serializers.CharField(source='get_account_type_display')
    work_type = serializers.CharField(source='get_work_type_display')
    gender = serializers.CharField(source='get_gender_display')
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = LearnerProfile
        fields = [
            'user', 'account_type', 'learning_track', 'skill_cluster',
            'work_type', 'industrial_prefrence', 'portfolio_link',
            'state', 'gender', 'resume', 'progress', #'current_pathway',
        ]
