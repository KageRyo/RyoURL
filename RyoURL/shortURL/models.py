from django.db import models
import datetime

class Url(models.Model):
    oriUrl = models.URLField()  # 原網址
    srtUrl = models.CharField(max_length=10, unique=True)  # 短網址
    creDate = models.DateTimeField(default=datetime.datetime.now)  # 創建日期