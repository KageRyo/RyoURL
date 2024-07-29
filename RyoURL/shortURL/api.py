import random
import string
import datetime
import requests

from typing import List
from django.http import HttpResponse
from ninja import NinjaAPI, Schema

from .models import Url

api = NinjaAPI()    # 初始化 API

# 定義 Url 的 Schema
class UrlSchema(Schema):
    orign_url: str
    short_string: str
    short_url: str
    create_date: datetime.datetime
    
# 產生隨機短網址的函式
def generator_short_url(length = 6):
    char = string.ascii_letters + string.digits
    while True:
        short_url = ''.join(random.choices(char, k=length))
        if not Url.objects.filter(short_url=short_url).exists():
            return short_url   # 如果短網址不存在 DB 中，則回傳此短網址
    
# 處理短網址域名的函式
def handle_domain(request, short_string):
    domain = request.build_absolute_uri('/')[:-1].strip('/')
    return f'{domain}/{short_string}'

# 檢查 http 前綴的函式
def check_http_format(orign_url):
    if not (orign_url.startswith('http://') or orign_url.startswith('https://')):
        return f'http://{orign_url}'
    return orign_url

# 檢查 URL 是否有效的函式
def check_url_available(orign_url):
    try:
        response = requests.head(orign_url, allow_redirects=True, timeout=5)
        return response.status_code == 200
    except:
        return False
    
# GET : 首頁 API /
@api.get("/")
def index(request):
    return "已與 RyoURL 建立連線。"
    
# POST : 新增短網址 API /short_url
@api.post("short_url", response=UrlSchema)
def create_short_url(request, orign_url: str):
    orign_url = check_http_format(orign_url)            # 檢查 http 前綴
    short_string = generator_short_url()                     # 產生隨機短網址字符串
    short_url = handle_domain(request, short_string)    # 處理短網址域名
    # 如果 URL 無效，則回傳 404
    if not check_url_available(orign_url):
        return HttpResponse('URL 不存在或無法存取，請檢查是否出錯。', status=404)
    else:
        # 建立新的短網址並儲存進資料庫
        url = Url.objects.create(
            orign_url = orign_url,
            short_string = short_string,
            short_url = short_url,
            create_date = datetime.datetime.now()
        )
        return url

# POST : 新增自訂短網址 API /custom_url
@api.post("custom_url", response=UrlSchema)
def create_custom_url(request, orign_url: str, short_string: str):
    orign_url = check_http_format(orign_url)            # 檢查 http 前綴
    short_url = handle_domain(request, short_string)    # 處理短網址域名
    # 如果 URL 無效，則回傳 404
    if not check_url_available(orign_url):
        return HttpResponse('URL 不存在或無法存取，請檢查是否出錯。', status=404)
    elif Url.objects.filter(short_url=short_url).exists():
        return HttpResponse('自訂短網址已存在，請更換其他短網址。', status=406)
    else:
        # 建立新的短網址並儲存進資料庫
        url = Url.objects.create(
            orign_url = orign_url,
            short_string = short_string,
            short_url = short_url,
            create_date = datetime.datetime.now()
        )
        return url

# GET : 以縮短網址字符查詢原網址 API /orign_url/{short_string}
@api.get('orign_url/{short_string}', response=UrlSchema)
def get_short_url(request, short_string: str):
    try:
        url = Url.objects.get(short_string=short_string)
    except Url.DoesNotExist:
        return HttpResponse('URL not found', status=404)
    return url

# GET : 查詢所有短網址 API /all_url
@api.get('all_url', response=List[UrlSchema])
def get_all_url(request):
    url = Url.objects.all()
    return url

# DELETE : 刪除短網址 API /short_url/{short_string}
@api.delete('short_url/{short_string}')
def delete_short_url(request, short_string: str):
    try:
        url = Url.objects.get(short_string=short_string)
    except Url.DoesNotExist:
        return HttpResponse('這個短網址並不存在。', status=404)
    url.delete()
    return HttpResponse('成功刪除！', status=200)