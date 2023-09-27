from django.db import models
from django.contrib.auth import get_user_model

class Account(models.Model):
    ACCOUNT_TYPE_FREE = "FREE"
    ACCOUNT_TYPE_PAID = "PAID"
    
    max_box_dict = {ACCOUNT_TYPE_FREE: 5, ACCOUNT_TYPE_PAID: float("inf")}
    max_repo_dict = {ACCOUNT_TYPE_FREE: 5, ACCOUNT_TYPE_PAID: float("inf")}

    ACCOUNT_PAID_MONTHS_CHOICES = (
        (1,1),
        (3,3),
        (6,6),
        (12,12),
    )
    ACCOUNT_TYPE_CHOICES = (
        (ACCOUNT_TYPE_FREE,ACCOUNT_TYPE_FREE),
        (ACCOUNT_TYPE_PAID,ACCOUNT_TYPE_PAID),
    )
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    account_type = models.CharField(max_length=255, default=ACCOUNT_TYPE_FREE, choices=ACCOUNT_TYPE_CHOICES)
    account_paid_months = models.IntegerField(null=True, choices=ACCOUNT_PAID_MONTHS_CHOICES)

    @property
    def max_boxes(self):
        return self.max_box_dict[self.account_type]

    @property
    def max_repos(self):
        return self.max_repo_dict[self.account_type]

