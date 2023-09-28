from django.urls import path, include
from box import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("box", views.BoxViewSet)
router.register("repo", views.RepoViewSet)
router.register("repoaccess", views.RepoAccessViewSet)
router.register("boxmedia", views.BoxMediaViewSet)

app_name = "box"

urlpatterns = [
    path("", include(router.urls)),
    path("repo/<int:pk>/", views.RepoRetrieveViewSet.as_view(), name="repo_item"),
    path("box/<int:pk>/", views.BoxEditViewset.as_view(), name="edit_box_item"),
    # path("token/", views.CreateTokenView.as_view(), name="token"),
]