from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

# Create your models here.
class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Role(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='roles')
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        unique_together = ['department', 'name']
    
    def __str__(self):
        return f"{self.department.name} - {self.name}"

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
    role = models.ForeignKey(Role, on_delete=models.PROTECT, related_name="employees")

    def __str__(self):
        return self.user.get_username()

class Computer(models.Model):
    STATUS_CHOICES = [
        ('Issued', 'In Use'),
        ('In Repair', 'In Repair'),
        ('Inventory', 'In Inventory'),
        ('Faulty', 'Faulty')
    ]
    computer_name = models.CharField(max_length=100, null=True)
    asset_tag = models.CharField(max_length=100, unique=True, editable=False,)
    current_user = models.OneToOneField(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name="computer")
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name="computers")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, blank=False, default='Inventory')

    def generate_asset_tag(self):
        if self.computer_name and self.department:
            name_slug = slugify(self.computer_name).upper()
            dept_slug = slugify(self.department.name).upper()

            base_tag = f"{name_slug}-{dept_slug}"
            max_num = Computer.objects.filter(
                asset_tag__startswith=base_tag
            ).aggregate(models.Max('asset_tag'))['asset_tag__max']

            if max_num:
                try:
                    last_num = int(max_num.split('-')[-1])
                    next_num = last_num + 1
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
    ASPECT_CHOICES = [
        ('16:9', '16:9'),
        ('16:10', '16:10'),
        ('5:4', '5:4'),
        ('4:3', '4:3'),
    ]

    SCREEN_CHOICES = [
        ('TN', 'TN'),
        ('VA', 'VA'),
        ('IPS', 'IPS'),
        ('OLED', 'OLED'),
        ('Mini-LED', 'Mini-LED'),
        ('QLED', 'QLED'),
        ('LCD', 'LCD'),
    ]

    MEMORY_CHOICES = [
        (4, "4 GB"),
        (8, "8 GB"),
        (12, "12 GB"),
        (16, "16 GB"),
        (24, "24 GB"),
        (32, "32 GB"),
        (64, "64 GB"),
        (96, "96 GB"),
        (128, "128 GB"),
    ]
    
    STORAGE_TYPE_CHOICES = [
        ('HDD', 'Hard Disk Storage (HDD)'),
        ('SSD', 'Solid State Storage (SSD)')
    ]

    STORAGE_SIZE_CHOICES = [
        ('256 GB', '256 GB'),
        ('512 GB', '512 GB'),
        ('1 TB', '1 TB'),
        ('2 TB', '2 TB'),
    ]
    computer = models.OneToOneField(Computer, on_delete=models.CASCADE, primary_key=True, related_name="info")
    brand = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    screen_type = models.CharField(max_length=12, choices=SCREEN_CHOICES)
    screen_aspect_ratio = models.CharField(max_length=10, choices=ASPECT_CHOICES)
    memory_size = models.PositiveIntegerField(help_text="RAM in GB", choices=MEMORY_CHOICES)
    storage_type = models.CharField(max_length=50, choices=STORAGE_TYPE_CHOICES)
    storage_size = models.CharField(max_length=50, choices=STORAGE_SIZE_CHOICES)

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