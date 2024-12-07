from django.contrib import admin
from .models import Assignment, TestCase, Submission, Feedback

# Register your models here.
admin.site.register(Assignment)
admin.site.register(TestCase)
admin.site.register(Submission)
admin.site.register(Feedback)