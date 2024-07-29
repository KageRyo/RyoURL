from django.db import models
import datetime

class Url(models.Model):
    orign_url = models.URLField()  # 原網址
    short_string = models.CharField(max_length=10, unique=True, default='NULL')  # 短網址的字符串
    short_url = models.URLField()  # 完整的短網址
    create_date = models.DateTimeField(default=datetime.datetime.now)  # 創建日期