from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager


class UserRoles(models.TextChoices):
    ADMIN = "admin"
    USER = "user"


class RegistrationTypes(models.TextChoices):
    PHONE = "phone"
    GOOGLE = "google"


class UserManager(BaseUserManager):
    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError('The Phone field must be set')

        user = self.model(phone=phone, **extra_fields)

        if password:
            user.set_password(password)
        else:
            raise ValueError('Password must be set')

        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_active') is not True:
            raise ValueError('Superuser must have is_active=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(phone, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.BigAutoField(primary_key=True)
    phone = models.CharField(max_length=100, unique=True)
    full_name = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    role = models.CharField(max_length=20, choices=UserRoles.choices)
    device_tokens = models.JSONField(blank=True, null=True, default=list)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    type_registration = models.CharField(
        max_length=20,
        choices=RegistrationTypes.choices,
        default=RegistrationTypes.PHONE
    )

    objects = UserManager()

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['role']

    def __str__(self):
        return self.phone

    class Meta:
        verbose_name_plural = '1-Users'

