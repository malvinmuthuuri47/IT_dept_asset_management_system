from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Employee, Department, Computer
from django.contrib.auth.models import User

# Register your models here.
# admin.site.register(Employee)
class EmployeeInline(admin.StackedInline):
    model = Employee
    fields = ['department', 'date_of_birth', 'gender', 'role']
    extra = 0

# extend User admin to show Employee Inline
class CustomUserAdmin(UserAdmin):
    inlines = [EmployeeInline]

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['user', 'department', 'role']
    list_filter = ['department', 'role']
    raw_id_fields = ['user']

@admin.register(Computer)
class ComputerAdmin(admin.ModelAdmin):
    list_display = ['comp_name', 'asset_tag', 'department', 'current_user', 'status']
    list_filter = ['department']
    # raw_id_fields = ['current_user']
    # search_fields = ['computer_name', 'asset_tag']
    readonly_fields = ['asset_tag']
    fields = ['comp_name', 'department', 'asset_tag', 'status']