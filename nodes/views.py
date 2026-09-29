from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from utils.response import (
    success_response,
    error_response,
)
from nodes.models import Node,NodeTypeTag
from accounts.permissions import IsAdminUser

from .serializers import (CompanySerializer, NodeCreateSerializer, NodeActivateSerializer,RoleCreateSerializer,AdminNodeDetailSerializer,AdminNodeDetailRequestSerializer,
AdminNodeUpdateSerializer,AdminNodeTypeTagCreateSerializer,AdminNodeTypeTagDeleteSerializer,AdminNodeDeleteSerializer)


class AdminCompanyCreateAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsAdminUser,
    ]

    def post(self, request):

        serializer = CompanySerializer(
            data=request.data
        )

        if not serializer.is_valid():

            return error_response(
                message="Company creation failed.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        company = serializer.save()

        return success_response(
            message="Company created successfully.",
            data=CompanySerializer(company).data,
            status_code=status.HTTP_201_CREATED,
        )

class AdminNodeCreateAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsAdminUser,
    ]

    def post(self, request):

        serializer = NodeCreateSerializer(
            data=request.data
        )

        if not serializer.is_valid():

            return error_response(
                message="Node creation failed.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        node = serializer.save()

        return success_response(
            message="Node created successfully.",
            data={
                "id": node.id,
                "company": node.company_id,
                "node_name": node.node_name,
                "address": node.address,
                "email": node.email,
                "mobile_number": node.mobile_number,
                "status": node.status,
                "type_tags": list(
                    node.type_tags.values_list(
                        "node_type__type_code",
                        flat=True,
                    )
                ),
            },
            status_code=status.HTTP_201_CREATED,
        )
class AdminNodeActivateAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsAdminUser,
    ]

    def post(self, request, pk):

        try:
            node = Node.objects.get(pk=pk)

        except Node.DoesNotExist:
            return error_response(
                message="Node not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        # Check whether node has at least one type tag
        if not node.type_tags.exists():
            return error_response(
                message="Node cannot be activated without a type tag.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        # Already active
        if node.status == Node.ACTIVE:
            return error_response(
                message="Node is already active.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        node.status = Node.ACTIVE
        node.save(update_fields=["status", "updated_at"])

        return success_response(
            message="Node activated successfully.",
            data={
                "id": node.id,
                "node_name": node.node_name,
                "status": node.status,
                "type_tags": list(
                    node.type_tags.values_list(
                        "node_type__type_code",
                        flat=True,
                    )
                ),
            },
            status_code=status.HTTP_200_OK,
        )
class AdminNodeActivateAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsAdminUser,
    ]

    def post(self, request, pk):

        # Find node
        try:
            node = Node.objects.get(pk=pk)

        except Node.DoesNotExist:
            return error_response(
                message="Node not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        # Serializer validation
        serializer = NodeActivateSerializer(
            data={},
            context={
                "node": node,
            },
        )

        if not serializer.is_valid():

            return error_response(
                message="Node activation failed.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        # Activate node
        node.status = Node.ACTIVE

        node.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        return success_response(
            message="Node activated successfully.",
            data={
                "id": node.id,
                "company": node.company_id,
                "node_name": node.node_name,
                "status": node.status,
                "type_tags": list(
                    node.type_tags.values_list(
                        "node_type__type_code",
                        flat=True,
                    )
                ),
            },
            status_code=status.HTTP_200_OK,
        )
    
class AdminRoleCreateAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsAdminUser,
    ]

    def post(self, request):

        serializer = RoleCreateSerializer(
            data=request.data
        )

        if not serializer.is_valid():

            return error_response(
                message="Role creation failed.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        role = serializer.save()

        return success_response(
            message="Role created successfully.",
            data={
                "id": role.id,
                "role_code": role.role_code,
                "role_name": role.role_name,
                "node_type": role.node_type_id,
            },
            status_code=status.HTTP_201_CREATED,
        )

class AdminNodeDetailAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsAdminUser,
    ]

    def get(self, request, pk):

        # ----------------------------
        # Validate node ID
        # ----------------------------

        if pk < 1:

            return error_response(
                message="Invalid node ID.",
                errors={
                    "id": [
                        "Node ID must be greater than 0."
                    ]
                },
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        # ----------------------------
        # Get node
        # ----------------------------

        try:

            node = Node.objects.select_related(
                "company"
            ).prefetch_related(
                "type_tags__node_type"
            ).get(
                pk=pk
            )

        except Node.DoesNotExist:

            return error_response(
                message="Node not found.",
                errors={
                    "id": [
                        "Node with this ID does not exist."
                    ]
                },
                status_code=status.HTTP_404_NOT_FOUND,
            )

        # ----------------------------
        # Serialize
        # ----------------------------

        serializer = AdminNodeDetailSerializer(
            node
        )

        # ----------------------------
        # Response
        # ----------------------------

        return success_response(
            message="Node fetched successfully.",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )

    def patch(self, request, pk):

        # ----------------------------
        # Validate Node ID
        # ----------------------------

        request_serializer = AdminNodeDetailRequestSerializer(
            data={
                "node_id": pk,
            }
        )

        if not request_serializer.is_valid():

            return error_response(
                message="Invalid node ID.",
                errors=request_serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        node_id = request_serializer.validated_data[
            "node_id"
        ]

        # ----------------------------
        # Get Node
        # ----------------------------

        try:

            node = Node.objects.get(
                pk=node_id
            )

        except Node.DoesNotExist:

            return error_response(
                message="Node not found.",
                errors={
                    "node_id": [
                        "Node with this ID does not exist."
                    ]
                },
                status_code=status.HTTP_404_NOT_FOUND,
            )

        # ----------------------------
        # Validate update data
        # ----------------------------

        serializer = AdminNodeUpdateSerializer(
            instance=node,
            data=request.data,
            partial=True,
        )

        if not serializer.is_valid():

            return error_response(
                message="Invalid node data.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        # ----------------------------
        # Update
        # ----------------------------

        node = serializer.save()

        # ----------------------------
        # Response
        # ----------------------------

        response_serializer = AdminNodeDetailSerializer(
            node
        )

        return success_response(
            message="Node updated successfully.",
            data=response_serializer.data,
            status_code=status.HTTP_200_OK,
        )
    def delete(self, request, pk):

        # ----------------------------
        # Validate Node ID
        # ----------------------------

        serializer = AdminNodeDeleteSerializer(
            data={
                "node_id": pk,
            }
        )

        if not serializer.is_valid():

            return error_response(
                message="Invalid node.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        node_id = serializer.validated_data[
            "node_id"
        ]

        # ----------------------------
        # Get Node
        # ----------------------------

        try:
            node = Node.objects.get(
                pk=node_id
            )
        except Node.DoesNotExist:

            return error_response(
                message="Node not found.",
                errors={
                    "node_id": [
                        "Node with this ID does not exist."
                    ]
                },
                status_code=status.HTTP_404_NOT_FOUND,
            )

        # ----------------------------
        # Store response data
        # ----------------------------

        deleted_node = {
            "id": node.id,
            "name": node.node_name,
            "status": node.status,
        }

        # ----------------------------
        # Delete
        # ----------------------------

        node.delete()

        # ----------------------------
        # Response
        # ----------------------------

        return success_response(
            message="Node deleted successfully.",
            data={
                "deleted_node": deleted_node,
            },
            status_code=status.HTTP_200_OK,
        )

class AdminNodeTypeTagCreateAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsAdminUser,
    ]

    def post(self, request, pk):

        # ----------------------------
        # Validate Node ID
        # ----------------------------

        request_serializer = AdminNodeDetailRequestSerializer(
            data={
                "node_id": pk,
            }
        )

        if not request_serializer.is_valid():

            return error_response(
                message="Invalid node ID.",
                errors=request_serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        node_id = request_serializer.validated_data[
            "node_id"
        ]

        # ----------------------------
        # Get Node
        # ----------------------------

        try:

            node = Node.objects.get(
                pk=node_id
            )

        except Node.DoesNotExist:

            return error_response(
                message="Node not found.",
                errors={
                    "node_id": [
                        "Node with this ID does not exist."
                    ]
                },
                status_code=status.HTTP_404_NOT_FOUND,
            )

        # ----------------------------
        # Validate request body
        # ----------------------------

        serializer = AdminNodeTypeTagCreateSerializer(
            data=request.data
        )

        if not serializer.is_valid():

            return error_response(
                message="Invalid node type data.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        node_type = serializer.validated_data[
            "node_type"
        ]

        # ----------------------------
        # Check duplicate
        # ----------------------------

        if NodeTypeTag.objects.filter(
            node=node,
            node_type=node_type,
        ).exists():

            return error_response(
                message="Node type tag already exists.",
                errors={
                    "node_type": [
                        "This node type is already assigned "
                        "to this node."
                    ]
                },
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        # ----------------------------
        # Create tag
        # ----------------------------

        node_type_tag = NodeTypeTag.objects.create(
            node=node,
            node_type=node_type,
        )

        # ----------------------------
        # Response
        # ----------------------------

        data = {
            "id": node_type_tag.id,
            "node": {
                "id": node.id,
                "name": node.node_name,
            },
            "type": {
                "id": node_type.id,
                "code": node_type.type_code,
                "name": node_type.type_name,
            },
        }

        return success_response(
            message="Node type tag added successfully.",
            data=data,
            status_code=status.HTTP_201_CREATED,
        )

class AdminNodeTypeTagDeleteAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsAdminUser,
    ]

    def delete(self, request, pk, tag_id):

        serializer = AdminNodeTypeTagDeleteSerializer(
            data={
                "node_id": pk,
                "tag_id": tag_id,
            }
        )

        if not serializer.is_valid():

            return error_response(
                message="Invalid node type tag.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        node = serializer.validated_data["node"]
        node_type_tag = serializer.validated_data[
            "node_type_tag"
        ]

        deleted_tag = {
            "id": node_type_tag.id,
            "code": node_type_tag.node_type.type_code,
            "name": node_type_tag.node_type.type_name,
        }

        node_type_tag.delete()

        return success_response(
            message="Node type tag deleted successfully.",
            data={
                "node_id": node.id,
                "node_name": node.node_name,
                "deleted_tag": deleted_tag,
            },
            status_code=status.HTTP_200_OK,
        )