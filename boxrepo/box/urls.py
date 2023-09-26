from django.urls import path, include
from box import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
# router.register("box", views.BoxViewSet)
router.register("repo", views.RepoViewSet)

app_name = "box"

urlpatterns = [
    path("", include(router.urls)),
    # path("create/", views.CreateUserView.as_view(), name="create"),
    # path("token/", views.CreateTokenView.as_view(), name="token"),
]