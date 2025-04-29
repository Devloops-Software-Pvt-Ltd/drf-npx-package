from django.db import models

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    published = models.DateField()

    def __str__(self):
        return self.title
