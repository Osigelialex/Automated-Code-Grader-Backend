import random
import string
from django.db import models
from account.models import CustomUser


class Course(models.Model):
    """
    Model representing a course
    """
    title = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    lecturer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    course_code = models.CharField(max_length=10, unique=True)
    course_units = models.PositiveIntegerField()
    students = models.ManyToManyField(CustomUser, related_name='courses')
    course_join_code = models.CharField(max_length=10, unique=True)
    course_open = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.title} - {self.course_code}'

    def generate_course_join_code(self):
        """
        Generate a random course join code
        """
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    
    def save(self, *args, **kwargs):
        if not self.course_join_code:
            self.course_join_code = self.generate_course_join_code()
    
        # Ensure that the course join code is unique
        while Course.objects.filter(course_join_code=self.course_join_code).exists():
            self.course_join_code = self.generate_course_join_code()
        
        return super().save(*args, **kwargs)