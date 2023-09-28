from django.shortcuts import render
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from rest_framework.settings import api_settings
from rest_framework.authtoken.models import Token

from django.contrib.auth import get_user_model
from rest_framework import generics, authentication, permissions
from rest_framework import viewsets, mixins, status

from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import APIView

from box.serializers import (
    RepoSerializer,
    RepoAccessSerializer,
    BoxSerializer,
    BoxMediaSerializer,
)
from box.models import Repo, RepoAccess, Box, BoxMedia
from user.models import Account
import logging
import os
import boto3
from dotenv import load_dotenv


load_dotenv()


class S3FileUploader:
    def __init__(self):
        self.AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
        self.AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

        self.session = boto3.Session(
            aws_access_key_id=self.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=self.AWS_SECRET_ACCESS_KEY,
        )

        self.s3 = self.session.resource("s3")
        self.bucket = self.s3.Bucket("box-repo-s3-bucket")

    def upload_file(self, key, file_content):
        self.bucket.put_object(Key=key, Body=file_content)
        return key


logger = logging.getLogger(__name__)
MAX_FILESIZE_MB = 5  # TODO: Make configurable by account type


def user_has_repo_admin_access(
    user,
    repo,
    required_access=[
        RepoAccess.REPO_ACCESS_TYPE_VIEWER,
        RepoAccess.REPO_ACCESS_TYPE_ADMIN,
        RepoAccess.REPO_ACCESS_TYPE_OWNER,
    ],
):
    return RepoAccess.objects.filter(
        user=user,
        repo=repo,
        access_type__in=required_access,
    ).exists()


class BoxViewSet(
    viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin
):
    """Class to manage accounts in the db"""

    queryset = Box.objects.all()
    serializer_class = BoxSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    # def get_queryset(self):
    #     pass

    def perform_create(self, serializer):
        """Create a new box for a user"""
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        """Restricts creation of boxes for free accounts
        Also ensures only admins can create boxes
        """
        repo = Repo.objects.get(id=request.data["repo"])
        user_has_repo_access = user_has_repo_admin_access(request.user, repo)
        if not user_has_repo_access:
            return Response(
                {"msg": "Unauthorized to perform action"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        account = Account.objects.filter(user=request.user).order_by("-id")[0]
        num_boxes = len(repo.boxes_list)
        logger.info(
            f"""RepoViewSet.create user {request.user}'s latest account {account} is a {account.account_type} one and repo {repo} currently has {num_boxes} boxes"""
        )
        if num_boxes + 1 > account.max_boxes:
            return Response(
                {"msg": "You can't have more than 5 boxes per repo on a free account!"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        return super().create(request, *args, **kwargs)


class RepoRetrieveViewSet(
    generics.RetrieveAPIView,
):
    queryset = Repo.objects.all()
    serializer_class = RepoSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        repo = self.get_object()
        user_has_repo_access = user_has_repo_admin_access(request.user, repo)
        if not user_has_repo_access:
            return Response(
                {"msg": "You are not authorized to view this repo"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        return super().get(request, *args, **kwargs)


class RepoViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
):
    """Class to manage accounts in the db"""

    queryset = Repo.objects.all()
    serializer_class = RepoSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        """Create a new repo for a user"""
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        account = Account.objects.filter(user=request.user).order_by("-id")[0]
        num_repos = len(Repo.objects.filter(user=request.user))
        logger.info(
            f"""RepoViewSet.create user {request.user}'s latest account {account} is a {account.account_type} one and currently has {num_repos} repos"""
        )
        if num_repos + 1 > account.max_repos:
            return Response(
                {"msg": "You can't have more than 5 repos on a free account!"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        return super().create(request, *args, **kwargs)


class RepoAccessViewSet(
    viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin
):
    """Class to manage RepoAccess in the db"""

    queryset = RepoAccess.objects.all()
    serializer_class = RepoAccessSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        repo = Repo.objects.get(id=request.data["repo"])
        serializer.is_valid(raise_exception=True)
        user_has_repo_access = user_has_repo_admin_access(
            request.user,
            repo,
            required_access=[
                RepoAccess.REPO_ACCESS_TYPE_ADMIN,
                RepoAccess.REPO_ACCESS_TYPE_OWNER,
            ],
        )
        if not user_has_repo_access:
            return Response(
                {"msg": "You are not authorized to assign access to this repo"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


class BoxEditViewset(generics.UpdateAPIView):
    queryset = Box.objects.all()
    serializer_class = BoxSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def update(self, request, *args, **kwargs):
        box = self.get_object()
        repo = box.repo

        user_has_repo_access = user_has_repo_admin_access(
            request.user,
            repo,
            required_access=[
                RepoAccess.REPO_ACCESS_TYPE_ADMIN,
                RepoAccess.REPO_ACCESS_TYPE_OWNER,
            ],
        )
        if not user_has_repo_access:
            return Response(
                {"msg": "Not authorized to perform action"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        return super().update(request, *args, **kwargs)


class BoxMediaViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    queryset = BoxMedia.objects.all()
    serializer_class = BoxMediaSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        """Create a new BoxMedia for a user"""
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        if not request.FILES.get("file", False):
            return Response(
                {"msg": "file key is missing in body"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        received_file = request.FILES.getlist("file")[0]
        file_size = received_file.size

        if file_size > MAX_FILESIZE_MB * 1024 * 1024:
            return Response(
                {
                    "msg": f"Max size of file is \
                                {MAX_FILESIZE_MB} MB",
                    "max_size": f"{MAX_FILESIZE_MB} MB",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        box_id = request.data["box"]
        # logger.info(f"""BoxMediaViewSet.create box_id :{box_id} is type {type(box_id)}""")
        box = Box.objects.get(id=int(box_id))
        box_media = BoxMedia.objects.create(
            **{
                "user": request.user,
                "box": box,
                "file_name": request.data["file_name"],
            }
        )
        s3 = S3FileUploader()
        s3.upload_file(key=box_media.s3_bucket_file_path, file_content=received_file)
        serializer = self.get_serializer(box_media)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
