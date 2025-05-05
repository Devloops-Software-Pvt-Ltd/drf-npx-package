from django.db import models
from django.utils.translation import gettext_lazy as _

class NpsPayment(models.Model):
    merchant_id = models.CharField(max_length=100)
    merchant_name = models.CharField(max_length=255)
    api_username = models.CharField(max_length=100)
    api_password = models.CharField(max_length=100)
    gateway_api_secret_key = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.merchant_name} ({self.merchant_id})"


