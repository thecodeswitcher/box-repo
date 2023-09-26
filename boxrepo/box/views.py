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

from box.serializers import RepoSerializer
from box.models import Repo
import logging
import os

logger = logging.getLogger(__name__)


class RepoViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin):
    """Class to manage accounts in the db"""

    queryset = Repo.objects.all()
    serializer_class = RepoSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    # def get_queryset(self):
    #     pass
    
    def perform_create(self, serializer):
        """Create a new repo for a user"""
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)        
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status = status.HTTP_201_CREATED,
            headers=headers
        )