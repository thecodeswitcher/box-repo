from django.shortcuts import render
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.authtoken.models import Token

from django.contrib.auth import get_user_model
from rest_framework import generics, authentication, permissions
from rest_framework import viewsets, mixins, status

from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import APIView

from user.serializers import UserSerializer, AccountSerializer, AuthTokenSerializer
from user.models import Account
import logging
import os

logger = logging.getLogger(__name__)


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user"""

    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class CreateUserView(generics.CreateAPIView):
    """Create a new account"""

    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        res = super().post(request, *args, **kwargs)
        if res.status_code == 201:
            user = get_user_model().objects.get(id=res.data["id"])
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                "token": token.key,
                "id": user.id,
            })
        return res

class AccountViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin):
    """Class to manage accounts in the db"""

    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        if request.user.id != serializer.data["id"]:
            return Response({"msg": "You are not authorized to create an account for this user"},
                            status=status.HTTP_401_UNAUTHORIZED,
                            )
        return Response(
            serializer.data,
            status = status.HTTP_201_CREATED,
            headers=headers
        )