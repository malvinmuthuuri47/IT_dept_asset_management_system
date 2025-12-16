from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="employee_profile")
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name="employees")
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, blank=True)
    role = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.user.get_username()

class Computer(models.Model):
    asset_tag = models.CharField(max_length=100, unique=True, help_text="Company-wide unique device ID or tag")
    current_user = models.OneToOneField(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name="computer")
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name="computers")
    status = models.CharField(max_length=20, help_text="e.g. in_use, in_repair, spare, retired")

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