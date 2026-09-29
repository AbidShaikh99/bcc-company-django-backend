from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.contrib.auth import get_user_model
from .serializers import (AdminCreateUserSerializer, AdminUserDetailSerializer,UserDetailRequestSerializer, AdminUserUpdateSerializer, AdminUserDeleteSerializer, LoginSerializer)
from .permissions import IsAdminUser, CanManageUsers
from django.db import transaction

from accounts.tasks import send_user_credentials_email
from utils.response import (
    success_response,
    error_response,
    delete_response,
)
User = get_user_model()

class AdminCreateUserAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
        CanManageUsers,
    ]

    def post(self, request):

        serializer = AdminCreateUserSerializer(
            data=request.data
        )

        if not serializer.is_valid():

            return error_response(
                message="User creation failed.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        user = serializer.save()

        temporary_password = serializer._temporary_password

        transaction.on_commit(
            lambda: send_user_credentials_email.delay(
                user.username,
                user.email,
                temporary_password,
            )
        )

        return success_response(
            message="User created successfully. Login credentials have been sent by email.",
            data={
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "company": user.company_id,
                "node_type_tag": user.node_type_tag_id,
                "role": (
                    user.role.role_code
                    if user.role
                    else None
                ),
            },
            status_code=status.HTTP_201_CREATED,
        )
class LoginAPIView(APIView):

    permission_classes = []

    def post(self, request):

        serializer = LoginSerializer(
            data=request.data
        )

        if not serializer.is_valid():

            return error_response(
                message="Login failed.",
                errors=serializer.errors,
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        user = serializer.validated_data["user"]

        return success_response(
            message="Login successful.",
            data={
                "access": serializer.validated_data["access"],
                "refresh": serializer.validated_data["refresh"],
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "company": user.company_id,
                    "node_type_tag": user.node_type_tag_id,
                    "role": user.role.role_code,
                },
            },
            status_code=status.HTTP_200_OK,
        )
class AdminUserDetailAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsAdminUser,
    ]

    def get(self, request, pk):

        # Validate URL parameter
        request_serializer = UserDetailRequestSerializer(
            data={"id": pk}
        )

        if not request_serializer.is_valid():

            return error_response(
                message="Invalid user ID.",
                errors=request_serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        user_id = request_serializer.validated_data["id"]

        # Check user exists
        try:
            user = User.objects.select_related(
                "company",
                "node_type_tag__node",
                "node_type_tag__node_type",
                "role__node_type",
            ).get(
                pk=user_id
            )

        except User.DoesNotExist:

            return error_response(
                message="User not found.",
                errors={
                    "id": [
                        "User with this ID does not exist."
                    ]
                },
                status_code=status.HTTP_404_NOT_FOUND,
            )

        serializer = AdminUserDetailSerializer(
            user
        )

        return success_response(
            message="User fetched successfully.",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )
class AdminUserUpdateAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsAdminUser,
    ]

    def patch(self, request, pk):

        # ----------------------------
        # Validate user ID
        # ----------------------------

        request_serializer = UserDetailRequestSerializer(
            data={
                "id": pk,
            }
        )

        if not request_serializer.is_valid():

            return error_response(
                message="Invalid user ID.",
                errors=request_serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        user_id = request_serializer.validated_data["id"]

        # ----------------------------
        # Get user
        # ----------------------------

        try:

            user = User.objects.select_related(
                "company",
                "node_type_tag__node",
                "node_type_tag__node_type",
                "role__node_type",
            ).get(
                pk=user_id
            )

        except User.DoesNotExist:

            return error_response(
                message="User not found.",
                errors={
                    "id": [
                        "User with this ID does not exist."
                    ]
                },
                status_code=status.HTTP_404_NOT_FOUND,
            )

        # ----------------------------
        # Validate update data
        # ----------------------------

        serializer = AdminUserUpdateSerializer(
            instance=user,
            data=request.data,
            partial=True,
        )

        if not serializer.is_valid():

            return error_response(
                message="User update failed.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        # ----------------------------
        # Save
        # ----------------------------

        user = serializer.save()

        return success_response(
            message="User updated successfully.",
            data={
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "company": (
                    user.company_id
                    if user.company
                    else None
                ),
                "node_type_tag": (
                    user.node_type_tag_id
                    if user.node_type_tag
                    else None
                ),
                "role": (
                    user.role.role_code
                    if user.role
                    else None
                ),
            },
            status_code=status.HTTP_200_OK,
        )
    def delete(self, request, pk):

        # Validate URL ID
        request_serializer = AdminUserDeleteSerializer(
            data={
                "user_id": pk,
            },
            context={
                "request": request,
            },
        )

        if not request_serializer.is_valid():

            return error_response(
                message="User deletion failed.",
                errors=request_serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        user_id = request_serializer.validated_data[
            "user_id"
        ]

        # Get user
        try:
            user = User.objects.get(
                pk=user_id
            )

        except User.DoesNotExist:

            return error_response(
                message="User not found.",
                errors={
                    "id": [
                        "User with this ID does not exist."
                    ]
                },
                status_code=status.HTTP_404_NOT_FOUND,
            )

        # Delete
        user.delete()

        return delete_response(
            message="delete successfully.",
            
        )