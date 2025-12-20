from rest_framework import serializers
from django.contrib.auth.models import User
from .models import ComputerRepairHistory, Computer, ComputerAssignment

class ComputerRepairHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ComputerRepairHistory
        fields = ['computer', 'repaired_component', 'date_of_repair', 'repair_cost', 'comments']
        read_only_fields = ['date_of_repair']

class UserComputerSerializer(serializers.ModelSerializer):
    current_assignment = serializers.SerializerMethodField()
    total_repair_cost = serializers.SerializerMethodField()
    repair_history = ComputerRepairHistorySerializer(source='repairs', many=True, read_only=True)

    class Meta:
        model = Computer
        fields = [
            'computer_name', 'asset_tag', 'status', 'department', 'current_assignment', 'repair_history', 'total_repair_cost'
        ]

    def get_current_assignment(self, obj):
        assignment = ComputerAssignment.objects.filter(
            computer=obj, end_date__isnull=True
        ).first()

        return {
            'start_Date': assignment.start_date.isoformat() if assignment else None,
            'employee': str(assignment.employee) if assignment else None
        } if assignment else None
    
    def get_total_repair_cost(self, obj):
        return sum(repair.repair_cost or 0 for repair in obj.repairs.all())

class ComputerAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComputerAssignment
        fields = ['computer', 'employee']

    def validate_computer(self, value):
        if value.status == 'faulty':
            raise serializers.ValidationError("Faulty computers cannot be assigned")
        return value