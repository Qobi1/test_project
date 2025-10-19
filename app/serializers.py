from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=False)
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "middle_name",
            "email",
            "password",
            "confirm_password",
            "role",
            "is_active",
        ]
        read_only_fields = ["id", "is_active"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        confirm_password = validated_data.pop("confirm_password", None)

        if confirm_password and password != confirm_password:
            raise serializers.ValidationError({"password": "Passwords do not match"})

        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        confirm_password = validated_data.pop("confirm_password", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            if confirm_password and password != confirm_password:
                raise serializers.ValidationError({"password": "Passwords do not match"})
            instance.set_password(password)

        instance.save()
        return instance

    def get_role(self, obj) -> str:
        # Example: derive from groups
        return obj.groups.first().name if obj.groups.exists() else "user"


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True)
