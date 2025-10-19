from django.urls import path

from app.views import UserCreateView, UserUpdateView, ProductsView

urlpatterns = [
    # User management
    path('users/', UserCreateView.as_view(), name='user-create'),
    path('users/<int:pk>/', UserUpdateView.as_view(), name='user-update'),
    path('product/', ProductsView.as_view(), name='product-get')
]

