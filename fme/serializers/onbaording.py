from rest_framework import serializers
from fme.serializers.base import BaseSerializer
from fme.models.nin import NinVerificationProcess

class NinVerificationSerializer(BaseSerializer):
    nin = serializers.CharField()

    def validate_nin(self, value):
        if not value.isdigit() or len(value) != 11:
            raise serializers.ValidationError("Invalid nin supplied")
        return value
    
class NinFinalizeSerializer(BaseSerializer):
    verification_id = serializers.UUIDField()
    token = serializers.CharField()

    def validate_token(self, value):
        if not value.isdigit() or len(value) != 5:
            raise serializers.ValidationError("Invalid token supplied")
        return value

class NinTokenResendSerializer(BaseSerializer):
    verification_id = serializers.UUIDField()

class NinDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = NinVerificationProcess
        fields = ['nin_detail']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        nin_detail = data.pop('nin_detail')
        nin_detail.pop('nin')
        nin_detail.pop('date_of_birth')
        return nin_detail
