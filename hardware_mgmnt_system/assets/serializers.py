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
    repair_history = ComputerRepairHistorySerializer(many=True, read_only=True)

    class Meta:
        model = Computer
        fields = [
            'computer_name', 'asset_tag', 'status', 'department', 'current_assignment', 'repair_history', 'total_repair_cost'
        ]

        def get_current_assignment(self, obj):
            assignment = ComputerAssignment.objects.filter(
                computer=obj, end_Date__isnull=True
            ).first()

            return {
                'start_Date': assignment.start_Date.isoformat() if assignment else None,
                'employee': str(assignment.employee) if assignment else None
            } if assignment else None
        
        def get_total_repair_cost(self, obj):
            return sum(repair.repair_cost or 0 for repair in obj.computerrepairhistory_set.all())