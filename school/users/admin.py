from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.decorators import login_required

from school.users.models import User

admin.site.login = login_required(admin.site.login)
admin.site.register(User, UserAdmin)
