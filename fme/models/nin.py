import re
from django.db import models
from fme.models.user import User
from fme.models.base import BaseModel

class NinVerificationProcess(BaseModel):
    nin = models.CharField(max_length=20, null=True, blank=True, db_index=True, unique=True)
    nin_detail = models.JSONField(null=True, blank=True)
    nin_is_verified = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=20, db_index=True)
    verification_token = models.CharField(max_length=10, db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)


    @staticmethod
    def format_phone_number(phone_number):
        if len(phone_number) == 11:
            phone_number = re.sub('^0', '234', phone_number)
        return phone_number
    
    @property
    def formated_phone_number(self):
        return NinVerificationProcess.format_phone_number(self.phone_number)
