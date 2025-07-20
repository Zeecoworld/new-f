import uuid
from django.db import models
from fme.models.user import User
from django.conf import settings
from django.utils import timezone
from fme.models.base import BaseModel
from django.core.mail import send_mail


class Invitation(BaseModel):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        ACCEPTED = 'ACCEPTED', 'Accepted'
        EXPIRED = 'EXPIRED', 'Expired'
    
    email = models.EmailField()
    expires_at = models.DateTimeField()
    role = models.CharField(max_length=20, choices=User.Role.choices)
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_invitations')
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(days=settings.INVITATION_TTL)  # 7-day expiry
        super().save(*args, **kwargs)
    
    def send_invitation_email(self):
        subject = 'Invitation to Join Our Platform'
        invite_url = f"{settings.FRONTEND_URL}/accept-invite?token={self.token}"
        message = f"""
        Hello,
        
        You have been invited to join skill for tech as a {self.role}.
        Please click the link below to accept the invitation:
        {invite_url}
        
        This invitation expires on {self.expires_at}.
        
        Regards,
        The Team Admin
        """
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [self.email],
            fail_silently=False,
        )
