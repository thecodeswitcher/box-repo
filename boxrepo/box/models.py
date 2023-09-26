from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.
class Repo(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE,)
    repo_name = models.CharField(max_length=255,)

    def max_box_number(self):
        pass

class Box(models.Model):
    pass