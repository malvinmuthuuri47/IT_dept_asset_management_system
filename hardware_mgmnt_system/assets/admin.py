from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Employee, Department, Computer, ComputerInfo, Role, ComputerAssignment, ComputerRepairHistory
from django.contrib.auth.models import User
from django.contrib import messages

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

    def has_add_permission(self, request):
        return False

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    inlines = [RoleInline]
    list_display = ['name']

    def has_add_permission(self, request):
        return False

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['user', 'department', 'role']
    list_filter = ['department', 'role']
    raw_id_fields = ['user']

    def has_add_permission(self, request):
        return False

class ComputerInfoInline(admin.StackedInline):
    model = ComputerInfo
    fields = ['brand', 'name', 'screen_type', 'screen_aspect_ratio', 'memory_size', 'storage_size', 'storage_type']
    extra = 1

class ComputerAssignmentInline(admin.TabularInline):
    model = ComputerAssignment
    fields = ['employee', 'start_date', 'end_date']
    # readonly_fields = ['start_date']
    extra = 1
    raw_id_fields = ['employee']
    can_delete=True

    def delete_queryset(self, request, queryset):
        '''Instead of deleting, set end_date to now'''
        from django.utils import timezone
        now = timezone.now().date()
        updated = queryset.update(end_date=now)
        self.message_user(
            request,
            f'{updated} assignments(s) ended on {now}',
            messages.SUCCESS
        )

class ComputerRepairHistoryInline(admin.TabularInline):
    model = ComputerRepairHistory
    fields = ['repaired_component', 'date_of_repair', 'repair_cost', 'comments']
    # readonly_fields = ['date_of_repair', 'date_of_repair', 'repair_cost', 'comments']
    list_display = ['repaired_component', 'date_of_repair', 'repair_cost']
    extra = 1
    can_delete = False

    def get_readonly_fields(self, request, obj=None):
        '''All fields readonly EXCEPT for New Entries'''
        if obj and obj.pk:
            return self.fields
        return []
    
    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        '''Show all history, but readonly'''
        qs = super().get_queryset(request)
        return qs.select_related('computer')

    # def has_add_permission(self, request, obj):
    #     return True

    # def has_change_permission(self, request, obj=None):
    #     return obj is None # only new objects editable

    

    

# @admin.register(ComputerRepairHistory)
# class ComputerRepairHistoryAdmin(admin.ModelAdmin):
#     list_display = ['computer', 'repaired_component', 'date_of_repair', 'repair_cost']
#     list_filter = ['date_of_repair', 'repaired_component']
#     raw_id_fields = ['computer']
#     search_fields = ['computer__computer_name', 'computer__asset_tag', 'comments']
#     date_hierarchy = 'date_of_repair'

@admin.register(Computer)
class ComputerAdmin(admin.ModelAdmin):
    inlines = [ComputerInfoInline, ComputerAssignmentInline, ComputerRepairHistoryInline]
    list_display = ['computer_name', 'asset_tag', 'department', 'current_user', 'status']
    list_filter = ['department']
    # raw_id_fields = ['current_user']
    # search_fields = ['computer_name', 'asset_tag']
    readonly_fields = ['asset_tag']
    fields = ['computer_name', 'department', 'asset_tag', 'status']

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        
        if obj.current_user:
            obj.status = 'Issued'
        elif not obj.current_user and not ComputerAssignment.objects.filter(
            computer=obj, end_date__isnull=True
        ).exists():
            obj.status = 'Inventory'
    
    def save_formset(self, request, form, formset, change):
        '''After inline changes, refresh computer status'''
        super().save_formset(request, form, formset, change)
        if formset.model == ComputerAssignment:
            form.instance.save()