from django.urls import path
from .views import LoginView, UserComputerView, LogoutView

urlpatterns = [
    path('login/', LoginView.as_view(), name='api_login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('my_computer/', UserComputerView.as_view(), name='my-computer'),
]