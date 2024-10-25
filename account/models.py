from django.db import models
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser, BaseUserManager


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.password = make_password(password)
        user.is_active = False
        user.save(using=self._db)
        return user

    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = 'STUDENT', 'Student'
        LECTURER = 'LECTURER', 'Lecturer'

    username = None
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    role = models.CharField(max_length=10, choices=Role.choices, default='student')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'department' 'role']

    objects = CustomUserManager()


class Student(models.Model):
    LEVEL_CHOICES = [
        (100, '100'),
        (200, '200'),
        (300, '300'),
        (400, '400'),
    ]

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='student_profile')
    matric = models.CharField(max_length=10, unique=True)
    level = models.IntegerField(choices=LEVEL_CHOICES, default=100)

    def __str__(self):
        return f"{self.user.email} - {self.matric}"


class Lecturer(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='lecturer_profile')
    staff_id = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return f"{self.user.email} - {self.staff_id}"


class Token(models.Model):
    key = models.CharField(max_length=150, primary_key=True)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.key
