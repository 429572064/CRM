from django.contrib import admin

# Register your models here.
from rbac.models import *


admin.site.register(Role)
admin.site.register(User)
admin.site.register(Permission)