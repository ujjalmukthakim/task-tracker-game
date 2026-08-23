from django.contrib import admin
from .models import Profile, Task, Completion
admin.site.register([Profile, Task, Completion])
