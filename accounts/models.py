from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser

from nodes.models import Company, NodeTypeTag, Role


class User(AbstractUser):
    company = models.ForeignKey(Company,on_delete=models.CASCADE,related_name="users", null=True, blank=True,)

    node_type_tag = models.ForeignKey(NodeTypeTag,on_delete=models.CASCADE,related_name="users", null=True, blank=True,)

    role = models.ForeignKey(Role,on_delete=models.PROTECT, related_name="users", null=True, blank=True,)

    email = models.EmailField(unique=True,)

    def __str__(self):
        return self.username