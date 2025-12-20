from django.contrib.auth import authenticate, login, logout
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, generics
from .models import Computer, ComputerAssignment, ComputerRepairHistory
from .serializers import UserComputerSerializer
from django.shortcuts import get_object_or_404
from django.utils import timezone

# Create your views here.
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"detail": "Username and password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response(
                {"detail": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        
        # create a session
        login(request, user)

        return Response(
            {
                "detail": "Logged in successfully.",
                "username": user.username,
                "is_staff": user.is_staff,
                "is_superuser": user.is_superuser,
            }
        )

class LogoutView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        logout(request)
        return Response(
            {"message": "Logged out successfully"},
            status=status.HTTP_200_OK
        )

class UserComputerView(generics.RetrieveAPIView):
    serializer_class = UserComputerSerializer
    permission_clases = [permissions.IsAuthenticated]

    def get_object(self):
        assignment = ComputerAssignment.objects.filter(
            employee__user=self.request.user,
            end_date__isnull=True
        ).select_related('computer__current_user__user', 'computer__department').first()

        if not assignment:
            return Response(
                {"detail": "No computer assigned to you currently."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return assignment.computer