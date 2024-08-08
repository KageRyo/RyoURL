import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    USER_TYPE = (
        (1, '一般使用者'),
        (2, '管理員'),
    )
    user_type = models.IntegerField(choices=USER_TYPE, default=1)  # 使用者類型

class Url(models.Model):
    # 短網址相關欄位
    origin_url = models.URLField()
    short_string = models.CharField(max_length=10, unique=True, default='NULL')
    short_url = models.URLField()
    create_date = models.DateTimeField(default=datetime.datetime.now)
    expire_date = models.DateTimeField(null=True, blank=True)
    visit_count = models.IntegerField(default=0)
    # 使用者相關欄位
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
