from django.urls import path
from .views import UserCreateView, UserUpdateView

urlpatterns = [
    path('users/', UserCreateView.as_view(), name='user-create'),
    path('users/<int:pk>/', UserUpdateView.as_view(), name='user-update-delete'),
]
