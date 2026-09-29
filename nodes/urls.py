from nodes.views import (AdminCompanyCreateAPIView,AdminNodeCreateAPIView,AdminNodeActivateAPIView, AdminRoleCreateAPIView, AdminNodeDetailAPIView, AdminNodeTypeTagCreateAPIView,AdminNodeTypeTagDeleteAPIView )
from django.urls import path


urlpatterns = [
    path(
    "admin/companies/",
    AdminCompanyCreateAPIView.as_view(),
    name="admin-company-create",
    ),
    path(
    "admin/nodes/",
    AdminNodeCreateAPIView.as_view(),
    name="admin-node-create",
    ),
    path(
    "admin/nodes/<int:pk>/activate/",
    AdminNodeActivateAPIView.as_view(),
    name="admin-node-activate",
    ),
    path(
    "admin/roles/",
    AdminRoleCreateAPIView.as_view(),
    name="admin-role-create",
    ),
    path(
        "admin/nodes/<int:pk>/",
        AdminNodeDetailAPIView.as_view(),
        name="admin-node-detail",
    ),
    path(
    "admin/nodes/<int:pk>/type-tags/",
    AdminNodeTypeTagCreateAPIView.as_view(),
    name="admin-node-type-tag-create",
    ),
    path(
    "admin/nodes/<int:pk>/type-tags/<int:tag_id>/",
    AdminNodeTypeTagDeleteAPIView.as_view(),
    name="admin-node-type-tag-delete",
    ),
]