from django.urls import path

from .views import (

    AdminCreateUserAPIView,AdminUserDetailAPIView,AdminUserUpdateAPIView, LoginAPIView
)


urlpatterns = [



    path(
        "admin/users/",
        AdminCreateUserAPIView.as_view(),
        name="admin-create-user",
    ),
    path(
    "admin/users/<int:pk>/",
    AdminUserDetailAPIView.as_view(),
    name="admin-user-detail",
),
    path(
    "admin/user/<int:pk>/",
    AdminUserUpdateAPIView.as_view(),
    name="admin-user-update",
),
    path(
        "admin/user/<int:pk>/",
        AdminUserDetailAPIView.as_view(),
        name="admin-user-detail",
    ),
    path(
    "auth/login/",
    LoginAPIView.as_view(),
    name="login",
),
]