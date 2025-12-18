from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Employee, Department, Computer, ComputerInfo, Role
from django.contrib.auth.models import User

# Register your models here.
# admin.site.register(Employee)
class EmployeeInline(admin.StackedInline):
    model = Employee
    fields = ['department', 'date_of_birth', 'gender', 'role']
    autocomplete_fields = ['role']
    extra = 0

# extend User admin to show Employee Inline
class CustomUserAdmin(UserAdmin):
    inlines = [EmployeeInline]

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

class RoleInline(admin.TabularInline):
    model = Role
    extra = 1

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'department']
    list_filter = ['department']
    search_fields = ['name']

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    inlines = [RoleInline]
    list_display = ['name']

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['user', 'department', 'role']
    list_filter = ['department', 'role']
    raw_id_fields = ['user']

class ComputerInfoInline(admin.StackedInline):
    model = ComputerInfo
    fields = ['brand', 'name', 'screen_type', 'screen_aspect_ratio', 'memory_size', 'storage_size', 'storage_type']
    extra = 1

@admin.register(Computer)
class ComputerAdmin(admin.ModelAdmin):
    inlines = [ComputerInfoInline]
    list_display = ['computer_name', 'asset_tag', 'department', 'current_user', 'status']
    list_filter = ['department']
    # raw_id_fields = ['current_user']
    # search_fields = ['computer_name', 'asset_tag']
    readonly_fields = ['asset_tag']
    fields = ['computer_name', 'department', 'asset_tag', 'status']