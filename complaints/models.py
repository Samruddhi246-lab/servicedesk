from django.db import models
from django.contrib.auth.models import User

class Complaint(models.Model):

    STATUS_CHOICES = [
        ('Pending','Pending'),
        ('In Progress','In Progress'),
        ('Resolved','Resolved')
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")

    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.title