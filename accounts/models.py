from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLE_ADMIN = 'admin'
    ROLE_ENGINEER = 'engineer'
    ROLE_SUPERVISOR = 'supervisor'
    
    ROLE_CHOICES = (
        (ROLE_ADMIN, 'Administrator'),
        (ROLE_ENGINEER, 'Engineer'),
        (ROLE_SUPERVISOR, 'Supervisor'),
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_ENGINEER)
    
    def is_admin_role(self):
        return self.role == self.ROLE_ADMIN or self.is_superuser
        
    def is_engineer_role(self):
        return self.role == self.ROLE_ENGINEER
        
    def is_supervisor_role(self):
        return self.role in [self.ROLE_SUPERVISOR, self.ROLE_ADMIN] or self.is_superuser
        
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
