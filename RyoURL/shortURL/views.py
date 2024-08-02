import logging

from redis import RedisError
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import F
from typing import Optional

from .models import Url

# logging 的設定
logger = logging.getLogger(__name__)

# 常數設定
CACHE_TIMEOUT = 60 * 60 * 24        # 快取過期時間為 24 小時
VISIT_COUNT_UPDATE_THRESHOLD = 10   # 訪問次數更新的閾值

# 檢查短網址是否過期的函式
def is_url_expired(url: Url) -> bool:
    if url.expire_date and url.expire_date < timezone.now():
        try:
            url.delete()
            return True
        except Exception as e:
            logger.error(f'刪除過期URL時發生錯誤: {e}')
    return False

# 更新資料庫中的訪問次數的函式
def update_visit_count(visit_count: int, url: Url) -> None:
    Url.objects.filter(id=url.id).update(visit_count=F('visit_count') + visit_count)
    logger.debug(f'訪問次數儲存進資料庫: {visit_count}')

# 處理訪問次數與快取的函式
def handle_visit_count(url: Url) -> None:
    try:
        # 處理快取
        cache_key = f'visit_count_{url.id}'     # 設定快取的鍵
        visit_count = cache.get(cache_key)      # 從快取中取得訪問次數
        if visit_count is None: # 如果快取中沒有訪問次數，那就從資料庫拿
            visit_count = url.visit_count
            logger.debug(f'在快取中找不到訪問次數，從資料庫拿: {visit_count}')
        
        # 增加訪問次數
        cache.set(cache_key, visit_count, timeout=CACHE_TIMEOUT) # 初始化快取，設定快取時間為 24 小時
        visit_count = cache.incr(cache_key)     # 訪問次數加 1
        logger.debug(f'目前快取中的訪問次數: {visit_count}')
        
        # 每 10 次訪問更新資料庫
        if visit_count % VISIT_COUNT_UPDATE_THRESHOLD == 0:
            update_visit_count(visit_count, url)
            
        # 處理快取過期的處理（每日至少儲存至資料庫一次）
        daily_update_key = f'daily_update_{url.id}'
        if not cache.get(daily_update_key):
            cache.set(daily_update_key, True, timeout=CACHE_TIMEOUT) # 快取 24 小時過期
            Url.objects.filter(id=url.id).update(visit_count=F('visit_count') + (visit_count % VISIT_COUNT_UPDATE_THRESHOLD))
            logger.debug(f'每日訪問次數儲存進資料庫: {visit_count}')
    
    # 如果 Redis 連線失敗，直接更新資料庫
    except RedisError as e:
        logger.error(f'與 Redis 操作失敗，直接更新資料庫: {e}', exc_info=True)
        update_visit_count(1, url)
    # 其他錯誤
    except Exception as e:
        logger.error(f'處理訪問次數時發生錯誤: {e}', exc_info=True)
        
# 將短網址導向原網址的函式
def redirectShortUrl(request, short_string: str) -> HttpResponse:
    try:
        url = get_object_or_404(Url, short_string=short_string)
        if is_url_expired(url):  # 檢查短網址是否過期
            return HttpResponse("此短網址已過期並已被刪除。", status=410)  # 410 Gone
        handle_visit_count(url) # 處理訪問次數
            
        # 將使用者重新導向至原網址
        return HttpResponseRedirect(url.orign_url)
    
    except Url.DoesNotExist:
        logger.warning(f'短網址不存在: {short_string}')
        return HttpResponse("此短網址不存在。", status=404)
    except Exception as e:
        logger.error(f'發生錯誤: {e}', exc_info=True)
        return HttpResponse("發生錯誤，請稍後再試。", status=500)