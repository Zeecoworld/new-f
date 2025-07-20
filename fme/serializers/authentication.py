import re
from fme.models.user import User
from rest_framework import serializers
from fme.serializers.base import BaseSerializer

class BaseUserSerializer(BaseSerializer):
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    phone_number = serializers.CharField(max_length=100)

    def validate_phone_number(value):
        rule = re.compile(r'(^[+0-9]{1,3})*([0-9]{10,11}$)')
        if not rule.search(value):
            raise serializers.ValidationError("Invalid phone number supplied")
        return value

class UserStatusSerializer(BaseSerializer):
    user_id = serializers.CharField(max_length=100)
    status = serializers.ChoiceField(choices=User.Status.choices)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.pop('user_id')
        if data['status'] == User.Status.DISABLED:
            data['is_active'] = False
        return data

class AuthenticateSerialize(BaseSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=100)





class UserSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source='get_role_display')
    status = serializers.CharField(source='get_status_display')
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'phone_number',
            'last_active', 'role', 'status'
        ]
        read_only_fields = ['last_active']
        # extra_kwargs = {
        #     'password': {'write_only': True},
        #     'username': {'write_only': True},
        #     'is_active': {'write_only': True}
        # }

class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'email', 'first_name', 'last_name', 'phone_number',
            'password', 'role'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def create(self, validated_data):
        # password = validated_data.pop('password')
        user = User(**validated_data)
        # user.set_password(password)
        user.save()
        return user

# class DetailedUserSerializer(UserSerializer):
#     learner_profile = LearnerProfileSerializer(read_only=True)
#     mentor_profile = MentorProfileSerializer(read_only=True)
#     facilitator_profile = FacilitatorProfileSerializer(read_only=True)
    
#     class Meta(UserSerializer.Meta):
#         fields = UserSerializer.Meta.fields + [
#             'learner_profile', 'mentor_profile', 'facilitator_profile'
#         ]