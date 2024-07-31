import logging
from django.core.cache import cache
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.http import HttpResponse
from .models import Url

# logging 的設定
logger = logging.getLogger(__name__)

# 檢查短網址是否過期的函式
def is_url_expired(url):
    if url.expire_date and url.expire_date < timezone.now():
        url.delete()
        return HttpResponse("此短網址已過期並已被刪除。", status=404)

# 處理訪問次數與快取的函式
def handle_visit_count(url):
    # 處理訪問次數
    cache_key = f'visit_count_{url.id}'     # 設定快取的鍵
    visit_count = cache.get(cache_key)      # 從快取中取得訪問次數
    if visit_count is None: # 如果快取中沒有訪問次數，那就從資料庫拿
        visit_count = url.visit_count
        logger.debug(f'在快取中找不到訪問次數，從資料庫拿: {visit_count}')
    visit_count += 1    # 更新訪問次數
    
    # 更新快取
    cache.set(cache_key, visit_count, timeout=60*60*24) # 每天重置一次
    logger.debug(f'目前快取中的訪問次數: {visit_count}')
    
    # 每 10 次訪問更新數資料庫
    if visit_count % 10 == 0:
        url.visit_count = visit_count
        url.save()
        logger.debug(f'訪問次數儲存進資料庫: {url.visit_count}')

# 將短網址導向原網址的函式
def redirectShortUrl(request, short_string):
    url = get_object_or_404(Url, short_string=short_string)
    is_url_expired(url)  # 檢查短網址是否過期
    handle_visit_count(url) # 處理訪問次數
    
    # 將使用者重新導向至原網址
    return redirect(url.orign_url)