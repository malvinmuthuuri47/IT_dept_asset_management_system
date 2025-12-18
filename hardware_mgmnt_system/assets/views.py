from django.contrib.auth import authenticate, login, logout
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

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