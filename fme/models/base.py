import uuid
from django.db import models

class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="created_at", db_index=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name="updated_at", db_index=True)

    class Meta:
        abstract = True
        ordering = ("-updated_at",)
        app_label = "fme"
