from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth import get_user_model

class CustomUser(AbstractUser):
    ROLES = (
        ('teacher', 'Teacher'),
        ('user', 'User')
    )
    role = models.CharField(max_length=10, choices=ROLES, default='user')

class Classroom(models.Model):
    STATUS_CHOICES = (
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('ended', 'Ended')
    )
    name = models.CharField(max_length=255)
    total_seats = models.PositiveIntegerField()
    available_seats = models.PositiveIntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open')
    teacher = models.ForeignKey(CustomUser,on_delete=models.CASCADE, related_name='classrooms')

    def __str__(self):
        return self.name

class Booking(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='bookings')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='bookings')
    booked_on = models.DateTimeField(auto_now_add=True)