from django.db import models

# Create your models here.


class Company(models.Model):
    name = models.CharField(max_length=150, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class NodeType(models.Model):
    

    type_code = models.CharField(max_length=20,unique=True,)

    type_name = models.CharField(max_length=100)

    def __str__(self):
        return self.type_code


class Node(models.Model):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"

    STATUS_CHOICES = (
        (DRAFT, "Draft"),
        (ACTIVE, "Active"),
    )

    company = models.ForeignKey(Company,on_delete=models.CASCADE,related_name="nodes",)

    node_name = models.CharField(max_length=150)

    address = models.TextField()

    email = models.EmailField()

    mobile_number = models.CharField(max_length=20)

    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default=DRAFT,)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.node_name


class NodeTypeTag(models.Model):
    node = models.ForeignKey(
        Node,
        on_delete=models.CASCADE,
        related_name="type_tags",
    )

    node_type = models.ForeignKey(
        NodeType,
        on_delete=models.PROTECT,
        related_name="node_tags",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["node", "node_type"],
                name="unique_node_type",
            )
        ]

    def __str__(self):
        return f"{self.node} - {self.node_type}"


class Role(models.Model):
    role_code = models.CharField(
        max_length=30,
        unique=True,
    )

    role_name = models.CharField(
        max_length=100,
    )

    node_type = models.ForeignKey(
        NodeType,
        on_delete=models.PROTECT,
        related_name="roles",
        null=True,
        blank=True,
    )
    can_create_users = models.BooleanField(default=False)
    def __str__(self):
        return self.role_code