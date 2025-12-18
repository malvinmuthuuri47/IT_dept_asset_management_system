from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

# Create your models here.
class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Employee(models.Model):
    GENDER_CHOICES = [
        ('', '-------'),
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="employee_profile")
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name="employees")
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=False)
    role = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.user.get_username()

class Computer(models.Model):
    STATUS_CHOICES = [
        ('Issued', 'In Use'),
        ('In Repair', 'In Repair'),
        ('Spare', 'In Inventory'),
        ('Faulty', 'Faulty')
    ]
    comp_name = models.CharField(max_length=100, null=True)
    asset_tag = models.CharField(max_length=100, unique=True, editable=False)
    current_user = models.OneToOneField(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name="computer")
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name="computers")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, blank=False)

    def generate_asset_tag(self):
        if self.comp_name and self.department:
            name_slug = slugify(self.comp_name).upper()
            dept_slug = slugify(self.department.name).upper()

            base_tag = f"{name_slug}-{dept_slug}"
            max_num = Computer.objects.filter(
                asset_tag__startswith=base_tag
            ).aggregate(models.Max('asset_tag'))['asset_tag__max']

            if max_num:
                try:
                    last_num = int(max_num.split('-')[-1])
                    nex_num = last_num + 1
                except (ValueError, IndexError):
                    next_num = 1
            else:
                next_num = 1
            
            return f"{base_tag}-{next_num:02d}"
        return ""
    
    def save(self, *args, **kwargs):
        if not self.asset_tag:
            self.asset_tag = self.generate_asset_tag()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.asset_tag


class ComputerInfo(models.Model):
    computer = models.OneToOneField(Computer, on_delete=models.CASCADE, primary_key=True, related_name="info")
    brand = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    screen_type = models.CharField(max_length=50)
    memory_size = models.PositiveIntegerField(help_text="RAM in GB")
    storage_type = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.brand} {self.name} ({self.computer.asset_tag})"

class ComputerAssignment(models.Model):
    computer = models.ForeignKey(Computer, on_delete=models.CASCADE, related_name="assignments")
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="computer_assignments")
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-start_date']
    
    def __str__(self):
        end = self.end_date or "present"
        return f"{self.computer.asset_tag} -> {self.employee.user.username} ({self.start_date} - {end})"

class ComputerRepairHistory(models.Model):
    computer = models.ForeignKey(Computer, on_delete=models.CASCADE, related_name="repairs")
    repaired_component = models.CharField(max_length=100)
    repair_cost = models.DecimalField(max_digits=10, decimal_places=2)
    date_of_repair = models.DateField()
    comments = models.TextField(blank=True)

    class Meta:
        ordering = ["-date_of_repair"]

    def __str__(self):
        return f"{self.computer.asset_tag} reapir on {self.date_of_repair}"