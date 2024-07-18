from django.db import models

class Url(models.Model):
    oriUrl = models.CharField(max_length=200)   # 原網址
    srtUrl = models.CharField(max_length=200)   # 短網址
    creDate = models.DateTimeField('創建日期')