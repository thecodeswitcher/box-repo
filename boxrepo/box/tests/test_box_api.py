from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.renderers import JSONRenderer

from user.models import Account
from box.models import Box, Repo
# from box.serializers import BoxSerializer, RepoSerializer
import logging
import json

logger = logging.getLogger(__name__)

REPO_URL = reverse("box:repo-list")

def create_user(**params):
    return get_user_model().objects.create_user(**params)


class RepoApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        payload = {"username": "test@boxrepo.com", "password": "testpass"}
        self.user = create_user(**payload)
        self.client.force_authenticate(user = self.user)
    
    def test_repo_create(self):
        """Test that the basic creation and retrieval of a repo works"""
        payload = {
            "repo_name": "Repo 1",
        }
        res = self.client.post(REPO_URL,payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        repo = Repo.objects.get(id=res.data["id"])
        self.assertEqual(repo.repo_name, payload["repo_name"])

    def test_repo_get(self):
        """Test the basic retrieval of a repo works"""
        payload = {
            "repo_name": "Repo 1",
        }
        self.client.post(REPO_URL,payload)
        res = self.client.get(REPO_URL + f"""?repo_name='{payload["repo_name"]}'""")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data[0]["repo_name"], payload["repo_name"])
    
class BoxApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        payload = {"username": "test@boxrepo.com", "password": "testpass"}
        self.user = create_user(**payload)

#TODO: Test that users can only retrieve boxes that they at least have viewer access to
#TODO: Test that admin/owner access is required to make changes to a box

#TODO: Test that free accounts can only create 5 repos
#TODO: Test that free accounts can only create 5 boxes per repo

