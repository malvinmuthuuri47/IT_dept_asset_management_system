from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.auth.models import User
from .models import Employee, ComputerAssignment, ComputerRepairHistory


@receiver(post_save, sender=User)
def create_employee_profile(sender, instance, created, **kwargs):
    if created and not hasattr(instance, 'employee_profile'):
        Employee.objects.create(user=instance)

@receiver(post_delete, sender=User)
def update_computer_status_on_user_delete(sender, instance, **kwargs):
    '''
    When a user is deleted, end their sctive assingments and update computers
    '''
    assignments = ComputerAssignment.objects.filter(
        employee__user=instance,
        end_date__isnull=True
    )

    for assignment in assignments:
        assignment.end_date = timezone.now().date()
        assignment.save()

@receiver(post_save, sender=ComputerAssignment)
def update_computer_on_assignment_change(sender, instance, **kwargs):
    '''When assignment changes, update the computer status'''
    if instance.computer:
        instance.computer.save()

@receiver(post_delete, sender=ComputerAssignment)
def update_computer_on_assignment_delete(sender, instance, **kwargs):
    '''When assignment deleted, refresh computer status'''
    if instance.computer:
        instance.computer.save()

@receiver(post_save, sender=ComputerRepairHistory)
def log_repair_on_assignment(sender, instance, **kwargs):
    '''Log repair activity'''
    if instance.computer:
        instance.computer.save()