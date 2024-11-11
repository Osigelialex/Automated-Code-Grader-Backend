from django.contrib import admin
from .models import CustomUser, Student, Token, Lecturer

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Student)
admin.site.register(Token)
admin.site.register(Lecturer)
