from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.renderers import JSONRenderer

from user.models import Account
from box.models import Box, Repo, RepoAccess, BoxMedia

import logging
import json

logger = logging.getLogger(__name__)

REPO_URL = reverse("box:repo-list")
REPO_ACCESS_URL = reverse("box:repoaccess-list")
BOX_MEDIA_LIST_URL = reverse("box:boxmedia-list")
BOX_URL = reverse("box:box-list")
ACCOUNT_TYPE_FREE = "FREE"


def create_user(**params):
    user = get_user_model().objects.create_user(**params)
    Account.objects.create(user=user, account_type = ACCOUNT_TYPE_FREE)
    return user


class RepoApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        payload = {"username": "test@boxrepo.com", "password": "testpass"}
        self.user = create_user(**payload)
        self.client.force_authenticate(user=self.user)

    def test_repo_create(self):
        """Test that the basic creation and retrieval of a repo works"""
        payload = {
            "repo_name": "Repo 1",
        }
        logger.info(f"""test_repo_create REPO_URL:{REPO_URL}""")
        res = self.client.post(REPO_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        repo = Repo.objects.get(id=res.data["id"])
        self.assertEqual(repo.repo_name, payload["repo_name"])

    def test_repo_get(self):
        """Test the basic retrieval of a repo works"""
        payload = {
            "user": self.user,
            "repo_name": "Repo 1",
        }
        repo = Repo.objects.create(**payload)
        Repo.objects.create(**{"user": self.user, "repo_name": "Repo 2"})
        repo_get_url = REPO_URL + f"""{repo.id}/"""
        res = self.client.get(repo_get_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            res.data["repo_name"],
            payload["repo_name"],
        )

    def test_repo_create_gives_owner_access(self):
        repo = Repo.objects.create(**{"user": self.user, "repo_name": "Repo 1"})
        access_qset = RepoAccess.objects.filter(
            user=self.user, repo=repo, access_type=RepoAccess.REPO_ACCESS_TYPE_OWNER
        )
        self.assertTrue(access_qset.exists())


class BoxApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        payload = {"username": "test@boxrepo.com", "password": "testpass"}
        self.user = create_user(**payload)
        self.other_users = []
        self.repo = Repo.objects.create(**{"user": self.user, "repo_name": "Repo 1"})
        self.repo2 = Repo.objects.create(**{"user": self.user, "repo_name": "Repo 2"})
        for i in range(1, 4):
            payload = {"username": f"test_{str(i)}@boxrepo.com", "password": "testpass"}
            self.other_users.append(create_user(**payload))

    def test_only_owners_and_admins_can_manage_repo_perms(self):
        other_user = self.other_users[0]
        self.client.force_authenticate(user=other_user)
        payload = {
            "user": other_user.id,
            "repo": self.repo.id,
            "access_type": RepoAccess.REPO_ACCESS_TYPE_ADMIN,
        }
        res = self.client.post(REPO_ACCESS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.force_authenticate(user=self.user)
        owner_res = self.client.post(REPO_ACCESS_URL, payload)
        self.assertEqual(owner_res.status_code, status.HTTP_201_CREATED)

    def test_create_box_api(self):
        payload = {
            "user": self.user.id,
            "repo": self.repo.id,
            "box_name": "A box",
            "box_description": "This is a box",
        }
        self.client.force_authenticate(user=self.user)
        res = self.client.post(BOX_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_only_admins_can_create_boxes(self):
        """Only admins/owners should be able to create boxes"""
        payload = {
            "user": self.user.id,
            "repo": self.repo.id,
            "box_name": "A box",
            "box_description": "This is a box",
        }
        self.client.force_authenticate(user=self.other_users[0])
        res = self.client.post(BOX_URL,payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)



    def test_viewer_access_required_to_get_repo(self):
        """A user needs at least viewer access to retrieve a repo"""
        self.client.force_authenticate(user=self.other_users[0])
        repo_get_url = REPO_URL + f"""{self.repo.id}/"""
        res = self.client.get(repo_get_url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_only_repo_admin_owners_can_edit_box(self):
        """Test that admin/owner access is required to make changes to a box"""
        RepoAccess.objects.create(
            **{
                "user": self.other_users[0],
                "repo": self.repo,
                "access_type": RepoAccess.REPO_ACCESS_TYPE_VIEWER,
            }
        )
        box = Box.objects.create(
            **{"repo": self.repo, "user": self.user, "box_name": "Original Box name"}
        )
        box_patch_url = BOX_URL + f"{box.id}/"
        logger.info(f"""test_only_repo_admin_owners_can_edit_box box_patch_url:{box_patch_url}""")
        self.client.force_authenticate(user=self.other_users[0])
        res = self.client.patch(box_patch_url, {"box_name": "New Box Name"})

        self.assertEquals(res.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_free_accounts_only_make_5_repos(self):
        """Test that free accounts can only create 5 repos"""
        account_payload = {
            "user": self.user,
            "account_type": ACCOUNT_TYPE_FREE,
        }
        acct = Account.objects.create(**account_payload)
        for i in range(3, 6):
            Repo.objects.create(**{"user": self.user, "repo_name": f"Repo {i}"})
        
        self.client.force_authenticate(user=self.user)
        res = self.client.post(REPO_URL,{"user": self.user, "repo_name": f"Repo 6"})
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_free_accounts_only_make_5_boxes_per_repo(self):
        """Test that free accounts can only create 5 boxes per repo"""
        for i in range(1,6):
            Box.objects.create(**{"user": self.user, "repo":self.repo, "box_name": f"Box {i}"})
        self.client.force_authenticate(user=self.user)
        payload = {
            "user": self.user.id,
            "repo": self.repo.id,
            "box_name": "A box",
            "box_description": "This is a box",
        }
        res = self.client.post(BOX_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
