from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from .models import User
from .permissions import HasAccessPermission
from .serializers import UserSerializer, LogoutSerializer


class UserCreateView(APIView):
    """POST: create new user"""
    permission_classes = [permissions.AllowAny]
    serializer_class = UserSerializer

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserUpdateView(APIView):
    """PUT/PATCH: update existing user"""
    parser_classes = [JSONParser]
    renderer_classes = [JSONRenderer]
    permission_classes = [HasAccessPermission]
    serializer_class = UserSerializer
    business_element = "users"

    def put(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        user.is_active = False
        user.save()
        return Response({"detail": "User deactivated successfully"}, status=status.HTTP_200_OK)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=LogoutSerializer,
        responses={
            205: OpenApiResponse(description="Successfully logged out."),
            400: OpenApiResponse(description="Invalid or expired token."),
        },
        description="Logout user by blacklisting the given refresh token (and optionally all active tokens).",
        summary="User Logout"
    )
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        refresh_token = serializer.validated_data["refresh"]

        try:
            # blacklist the refresh token itself
            token = RefreshToken(refresh_token)
            token.blacklist()

            # Optional: also blacklist all outstanding tokens for this user
            for outstanding in OutstandingToken.objects.filter(user=request.user):
                BlacklistedToken.objects.get_or_create(token=outstanding)

            return Response(
                {"detail": "Successfully logged out."},
                status=status.HTTP_205_RESET_CONTENT
            )

        except TokenError:
            return Response(
                {"error": "Invalid or expired token."},
                status=status.HTTP_400_BAD_REQUEST
            )


class ProductsView(APIView):
    permission_classes = [HasAccessPermission]
    serializer_class = LogoutSerializer
    business_element = "products"

    def get(self, request):
        data = [{"id": 1, "name": "Product A"}, {"id": 2, "name": "Product B"}]
        return Response(data)

