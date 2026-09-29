import secrets
import string
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from rest_framework import serializers

from nodes.models import (
    Company,
    NodeTypeTag,
    Role,
)

User = get_user_model()


def generate_temporary_password(length=12):
    characters = (
        string.ascii_letters
        + string.digits
        + "@#$%&*"
    )

    return "".join(
        secrets.choice(characters)
        for _ in range(length)
    )


class AdminCreateUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "company",
            "node_type_tag",
            "role",
        ]
        read_only_fields = ["id"]

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError(
                "Username already exists."
            )

        return value

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "Email already exists."
            )

        return value

    def validate(self, attrs):
        company = attrs.get("company")
        node_type_tag = attrs.get("node_type_tag")
        role = attrs.get("role")

        if node_type_tag:
            node = node_type_tag.node

            if company and node.company_id != company.id:
                raise serializers.ValidationError({
                    "node_type_tag": (
                        "Selected node type tag does not belong "
                        "to the selected company."
                    )
                })

            if node.status != "ACTIVE":
                raise serializers.ValidationError({
                    "node_type_tag": (
                        "User can only be assigned to an active node."
                    )
                })

            if role:
                if role.node_type_id != node_type_tag.node_type_id:
                    raise serializers.ValidationError({
                        "role": (
                            "Selected role does not belong "
                            "to the selected node type."
                        )
                    })

        return attrs

    def create(self, validated_data):
        temporary_password = generate_temporary_password()

        user = User(
            **validated_data
        )

        user.set_password(temporary_password)
        user.save()

        self._temporary_password = temporary_password

        return user


class LoginSerializer(serializers.Serializer):

    username = serializers.CharField(
        required=True,
        trim_whitespace=True,
    )

    password = serializers.CharField(
        required=True,
        write_only=True,
    )

    def validate(self, attrs):

        username = attrs["username"]
        password = attrs["password"]

        user = authenticate(
            username=username,
            password=password,
        )

        if user is None:
            raise serializers.ValidationError(
                "Invalid username or password."
            )

        if not user.is_active:
            raise serializers.ValidationError(
                "This user account is inactive."
            )

        if not user.role:
            raise serializers.ValidationError(
                "User does not have an assigned role."
            )

        refresh = RefreshToken.for_user(user)

        return {
            "user": user,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }

class AdminUserDetailSerializer(serializers.ModelSerializer):

    company = serializers.SerializerMethodField()
    node_type_tag = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "company",
            "node_type_tag",
            "role",
        ]

    def validate(self, attrs):
        user = self.instance

        if not user:
            raise serializers.ValidationError(
                "User does not exist."
            )

        return attrs

    def get_company(self, obj):

        if not obj.company:
            return None

        return {
            "id": obj.company.id,
            "name": obj.company.name,
        }

    def get_node_type_tag(self, obj):

        if not obj.node_type_tag:
            return None

        node_type_tag = obj.node_type_tag

        if not node_type_tag.node:
            raise serializers.ValidationError(
                "User's node type tag has no node."
            )

        if not node_type_tag.node_type:
            raise serializers.ValidationError(
                "User's node type tag has no node type."
            )

        return {
            "id": node_type_tag.id,
            "node": {
                "id": node_type_tag.node.id,
                "name": node_type_tag.node.node_name,
                "status": node_type_tag.node.status,
            },
            "type": {
                "id": node_type_tag.node_type.id,
                "code": node_type_tag.node_type.type_code,
                "name": node_type_tag.node_type.type_name,
            },
        }

    def get_role(self, obj):

        if not obj.role:
            return None

        return {
            "id": obj.role.id,
            "code": obj.role.role_code,
            "name": obj.role.role_name,
        }
class UserDetailRequestSerializer(serializers.Serializer):

    id = serializers.IntegerField(
        min_value=1
    )
class AdminUserUpdateSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True,
        required=False,
        min_length=8,
    )

    class Meta:
        model = User

        fields = [
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
            "company",
            "node_type_tag",
            "role",
        ]

    def validate_username(self, value):

        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Username cannot be empty."
            )

        queryset = User.objects.filter(
            username__iexact=value
        )

        # Don't compare the user with himself
        if self.instance:
            queryset = queryset.exclude(
                pk=self.instance.pk
            )

        if queryset.exists():
            raise serializers.ValidationError(
                "Username already exists."
            )

        return value

    def validate_email(self, value):

        value = value.strip().lower()

        if not value:
            raise serializers.ValidationError(
                "Email cannot be empty."
            )

        queryset = User.objects.filter(
            email__iexact=value
        )

        if self.instance:
            queryset = queryset.exclude(
                pk=self.instance.pk
            )

        if queryset.exists():
            raise serializers.ValidationError(
                "Email already exists."
            )

        return value

    def validate_password(self, value):

        if not value.strip():
            raise serializers.ValidationError(
                "Password cannot be empty."
            )

        if len(value) < 8:
            raise serializers.ValidationError(
                "Password must contain at least 8 characters."
            )

        return value

    def validate(self, attrs):

        # Existing values
        company = attrs.get(
            "company",
            self.instance.company,
        )

        node_type_tag = attrs.get(
            "node_type_tag",
            self.instance.node_type_tag,
        )

        role = attrs.get(
            "role",
            self.instance.role,
        )

        # --------------------------------
        # Company + NodeTypeTag validation
        # --------------------------------

        if node_type_tag:

            node = node_type_tag.node

            if not node:
                raise serializers.ValidationError({
                    "node_type_tag": (
                        "Selected node type tag has no node."
                    )
                })

            if company and node.company_id != company.id:
                raise serializers.ValidationError({
                    "node_type_tag": (
                        "Selected node type tag does not "
                        "belong to the selected company."
                    )
                })

            # ----------------------------
            # Node must be ACTIVE
            # ----------------------------

            if node.status != node.ACTIVE:
                raise serializers.ValidationError({
                    "node_type_tag": (
                        "Users can only be assigned "
                        "to an active node."
                    )
                })

        # ----------------------------
        # Role validation
        # ----------------------------

        if role and node_type_tag:

            node_type = node_type_tag.node_type

            if not node_type:
                raise serializers.ValidationError({
                    "node_type_tag": (
                        "Selected node type tag has "
                        "no node type."
                    )
                })

            if role.node_type_id != node_type.id:
                raise serializers.ValidationError({
                    "role": (
                        "Selected role does not belong "
                        "to the selected node type."
                    )
                })

        return attrs

    def update(self, instance, validated_data):

        password = validated_data.pop(
            "password",
            None,
        )

        for field, value in validated_data.items():
            setattr(
                instance,
                field,
                value,
            )

        if password:
            instance.set_password(password)

        instance.save()

        return instance

class AdminUserDeleteSerializer(serializers.Serializer):

    user_id = serializers.IntegerField(
        min_value=1
    )

    def validate_user_id(self, value):

        try:
            user = User.objects.get(
                pk=value
            )
        except User.DoesNotExist:
            raise serializers.ValidationError(
                "User with this ID does not exist."
            )

        request = self.context.get("request")

        # Don't allow Admin to delete himself
        if request and request.user.id == user.id:
            raise serializers.ValidationError(
                "You cannot delete your own account."
            )

        # Don't allow deleting an ADMIN user
        if user.role and user.role.role_code == "ADMIN":
            raise serializers.ValidationError(
                "Admin users cannot be deleted."
            )

        return value