from django.db import models

class NpsPayment(models.Model):
    merchant_id = models.CharField(max_length=255)
    merchant_name = models.CharField(max_length=255)
    api_username = models.CharField(max_length=255)
    api_password = models.CharField(max_length=255)
    gateway_api_secret_key = models.CharField(max_length=255)

    def __str__(self):
        return self.merchant_name
