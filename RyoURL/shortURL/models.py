from django.db import models
import datetime

class Url(models.Model):
    oriUrl = models.URLField()  # 原網址
    srtStr = models.CharField(max_length=10, unique=True, default='NULL')  # 短網址的字符串
    srtUrl = models.URLField()  # 完整的短網址
    creDate = models.DateTimeField(default=datetime.datetime.now)  # 創建日期