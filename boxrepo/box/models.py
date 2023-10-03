from django.db import models
from django.contrib.auth import get_user_model
import datetime
from user.models import Account
from box.aws_utils.s3_utils import S3FileManager


class Repo(models.Model):
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
    )
    repo_name = models.CharField(
        max_length=255,
    )
    # TODO: created_at
    # TODO: updated_at

    def save(self, *args, **kwargs):
        """Automatically create an OWNER access type"""
        super().save()
        if not RepoAccess.objects.filter(
            user=self.user, repo=self, access_type=RepoAccess.REPO_ACCESS_TYPE_OWNER
        ).exists():
            RepoAccess.objects.get_or_create(
                user=self.user, repo=self, access_type=RepoAccess.REPO_ACCESS_TYPE_OWNER
            )

    @property
    def boxes_list(self):
        return self.boxes.all()


class RepoAccess(models.Model):
    REPO_ACCESS_TYPE_OWNER = "OWNER"
    REPO_ACCESS_TYPE_ADMIN = "ADMIN"
    REPO_ACCESS_TYPE_VIEWER = "VIEWER"
    REPO_ACCESS_TYPE_CHOICES = (
        (REPO_ACCESS_TYPE_OWNER, REPO_ACCESS_TYPE_OWNER),
        (REPO_ACCESS_TYPE_ADMIN, REPO_ACCESS_TYPE_ADMIN),
        (REPO_ACCESS_TYPE_VIEWER, REPO_ACCESS_TYPE_VIEWER),
    )

    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
    )
    repo = models.ForeignKey(
        Repo,
        on_delete=models.CASCADE,
    )
    access_type = models.CharField(max_length=255, choices=REPO_ACCESS_TYPE_CHOICES)

    # TODO: created_at
    # TODO: updated_at


class Box(models.Model):
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="boxes",
    )
    repo = models.ForeignKey(
        Repo,
        on_delete=models.CASCADE,
        related_name="boxes",
    )
    box_name = models.CharField(max_length=255, default="")
    box_description = models.TextField(default="")
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(auto_now=True)


class BoxMedia(models.Model):
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        default=None,
    )
    box = models.ForeignKey(
        Box,
        on_delete=models.CASCADE,
        default=None,
    )
    file_name = models.TextField(default="")  # front end will encrypt the file_name

    @property
    def s3_bucket_file_path(self):
        return f"repo_{self.box.repo.id}/box_{self.box.id}/file_{self.id}"
