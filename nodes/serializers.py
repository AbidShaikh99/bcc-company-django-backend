from rest_framework import serializers
from django.db import transaction
from .models import (
    Company,
    Node,
    NodeType,
    NodeTypeTag,
    Role
)


class CompanySerializer(serializers.ModelSerializer):

    class Meta:
        model = Company
        fields = [
            "id",
            "name",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
        ]

    def validate_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Company name is required."
            )

        if Company.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError(
                "Company already exists."
            )

        return value


class NodeCreateSerializer(serializers.ModelSerializer):

    type_tags = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=True,
    )

    class Meta:
        model = Node

        fields = [
            "id",
            "company",
            "node_name",
            "address",
            "email",
            "mobile_number",
            "status",
            "type_tags",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "status",
            "created_at",
            "updated_at",
        ]

    def validate_type_tags(self, value):

        if not value:
            raise serializers.ValidationError(
                "At least one type tag is required."
            )

        value = [
            item.strip().upper()
            for item in value
        ]

        # Don't allow empty strings
        if any(not item for item in value):
            raise serializers.ValidationError(
                "Type tag cannot be empty."
            )

        # Don't allow duplicate tags
        if len(value) != len(set(value)):
            raise serializers.ValidationError(
                "Duplicate type tags are not allowed."
            )

        return value

    @transaction.atomic
    def create(self, validated_data):

        type_tags = validated_data.pop("type_tags")

        # 1. Create Node
        node = Node.objects.create(
            **validated_data
        )

        # 2. Create/reuse NodeType
        for type_code in type_tags:

            node_type, created = NodeType.objects.get_or_create(
                type_code=type_code,
                defaults={
                    "type_name": type_code,
                },
            )

            # 3. Create NodeTypeTag
            NodeTypeTag.objects.create(
                node=node,
                node_type=node_type,
            )

        return node

class NodeActivateSerializer(serializers.Serializer):

    def validate(self, attrs):
        node = self.context["node"]

        # 1. Check current status
        if node.status == Node.ACTIVE:
            raise serializers.ValidationError(
                "Node is already active."
            )

        # 2. Check type tags
        if not node.type_tags.exists():
            raise serializers.ValidationError(
                "Node must have at least one type tag before activation."
            )

        return attrs

class RoleCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Role
        fields = [
            "id",
            "role_code",
            "role_name",
            "node_type",
        ]

        read_only_fields = [
            "id",
        ]

    def validate_role_code(self, value):

        value = value.strip().upper()

        if not value:
            raise serializers.ValidationError(
                "Role code is required."
            )

        if Role.objects.filter(
            role_code=value
        ).exists():
            raise serializers.ValidationError(
                "Role code already exists."
            )

        return value

    def validate_role_name(self, value):

        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Role name is required."
            )

        return value

    def validate_node_type(self, value):

        if not NodeType.objects.filter(
            id=value.id
        ).exists():
            raise serializers.ValidationError(
                "Selected node type does not exist."
            )

        return value

class AdminNodeDetailSerializer(serializers.ModelSerializer):

    company = serializers.SerializerMethodField()
    type_tags = serializers.SerializerMethodField()

    class Meta:
        model = Node
        fields = [
            "id",
            "node_name",
            "address",
            "email",
            "mobile_number",
            "status",
            "company",
            "type_tags",
            "created_at",
            "updated_at",
        ]

    def get_company(self, obj):

        if not obj.company:
            return None

        return {
            "id": obj.company.id,
            "name": obj.company.name,
        }

    def get_type_tags(self, obj):

        return [
            {
                "id": tag.id,
                "code": tag.node_type.type_code,
                "name": tag.node_type.type_name,
            }
            for tag in obj.type_tags.all()
        ]
class AdminNodeDetailRequestSerializer(serializers.Serializer):

    node_id = serializers.IntegerField(
        min_value=1
    )

class AdminNodeUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Node
        fields = [
            "node_name",
            "address",
            "email",
            "mobile_number",
            "company",
        ]
        extra_kwargs = {
            "node_name": {
                "required": False,
            },
            "address": {
                "required": False,
            },
            "email": {
                "required": False,
            },
            "mobile_number": {
                "required": False,
            },
            "company": {
                "required": False,
            },
        }

    def validate_node_name(self, value):

        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Node name cannot be empty."
            )

        return value

    def validate_address(self, value):

        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Address cannot be empty."
            )

        return value

    def validate_email(self, value):

        value = value.strip().lower()

        if not value:
            raise serializers.ValidationError(
                "Email cannot be empty."
            )

        return value

    def validate_mobile_number(self, value):

        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Mobile number cannot be empty."
            )

        return value

    def validate_company(self, value):

        if not value:
            raise serializers.ValidationError(
                "Company is required."
            )

        return value

class AdminNodeTypeTagCreateSerializer(serializers.Serializer):

    node_type = serializers.IntegerField(
        min_value=1
    )

    def validate_node_type(self, value):

        try:
            node_type = NodeType.objects.get(
                pk=value
            )
        except NodeType.DoesNotExist:
            raise serializers.ValidationError(
                "Node type does not exist."
            )

        return node_type

class AdminNodeTypeTagDeleteSerializer(serializers.Serializer):

    node_id = serializers.IntegerField(
        min_value=1
    )

    tag_id = serializers.IntegerField(
        min_value=1
    )

    def validate(self, attrs):

        node_id = attrs["node_id"]
        tag_id = attrs["tag_id"]

        try:
            node = Node.objects.get(
                pk=node_id
            )
        except Node.DoesNotExist:
            raise serializers.ValidationError({
                "node_id": "Node does not exist."
            })

        try:
            node_type_tag = NodeTypeTag.objects.select_related(
                "node",
                "node_type",
            ).get(
                pk=tag_id,
                node_id=node_id,
            )
        except NodeTypeTag.DoesNotExist:
            raise serializers.ValidationError({
                "tag_id": (
                    "Node type tag does not exist "
                    "for this node."
                )
            })

        # Active node must always have at least one tag
        if node.status == Node.ACTIVE:

            tag_count = NodeTypeTag.objects.filter(
                node_id=node_id
            ).count()

            if tag_count <= 1:
                raise serializers.ValidationError({
                    "tag_id": (
                        "Cannot remove the last type tag "
                        "from an active node."
                    )
                })

        attrs["node"] = node
        attrs["node_type_tag"] = node_type_tag

        return attrs

class AdminNodeDeleteSerializer(serializers.Serializer):

    node_id = serializers.IntegerField(
        min_value=1
    )

    def validate_node_id(self, value):

        try:
            node = Node.objects.get(pk=value)
        except Node.DoesNotExist:
            raise serializers.ValidationError(
                "Node with this ID does not exist."
            )

        # Check whether users are assigned to this node
        if node.type_tags.filter(users__isnull=False).exists():
            raise serializers.ValidationError(
                "Node cannot be deleted because users are assigned to it."
            )

        return value