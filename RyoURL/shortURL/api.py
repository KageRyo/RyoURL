import random
import string
import datetime

from typing import List
from django.http import HttpResponse
from ninja import NinjaAPI, Schema

from .models import Url

api = NinjaAPI()    # 初始化 API

# 定義 Url 的 Schema
class UrlSchema(Schema):
    oriUrl: str
    srtStr: str
    srtUrl: str
    creDate: datetime.datetime
    
# 產生隨機短網址的函式
def geneShortUrl(length = 6):
    char = string.ascii_letters + string.digits
    while True:
        srtUrl = ''.join(random.choices(char, k=length))
        if not Url.objects.filter(srtUrl=srtUrl).exists():
            return srtUrl   # 如果短網址不存在 DB 中，則回傳此短網址
    
# 處理短網址域名的函式
def handleShortUrl(request, srtStr):
    domain = request.build_absolute_uri('/')[:-1].strip('/')
    return f'{domain}/{srtStr}'
    
# GET : 首頁 API /
@api.get("/")
def index(request):
    return "已與 RyoURL 建立連線。"
    
# POST : 新增短網址 API /creatShortUrl
@api.post("createShortUrl", response=UrlSchema)
def createShortUrl(request, oriUrl: str):
    srtStr = geneShortUrl()
    srtUrl = handleShortUrl(request, srtStr)
    url = Url.objects.create(
        oriUrl = oriUrl,
        srtStr = srtStr,
        srtUrl = srtUrl,
        creDate = datetime.datetime.now()
    )
    return url

# GET : 以縮短網址字符查詢原網址 API /lookforOriUrl/{srtStr}
@api.get('lookforOriUrl/{srtStr}', response=UrlSchema)
def lookforOriUrl(request, srtStr: str):
    try:
        url = Url.objects.get(srtStr=srtStr)
    except Url.DoesNotExist:
        return HttpResponse('URL not found', status=404)
    return url

# GET : 查詢所有短網址 API /getAllUrl
@api.get('getAllUrl', response=List[UrlSchema])
def getAllUrl(request):
    url = Url.objects.all()
    return url
