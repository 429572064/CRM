from django.contrib import admin

# Register your models here.
from employee.models import *


admin.site.register(ClassList)
admin.site.register(Customer)
admin.site.register(Campuses)