from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.http import HttpResponse
from .models import Url

# 將短網址導向原網址的函式
def redirectShortUrl(request, short_string):
    url = get_object_or_404(Url, short_string=short_string)
    
    # 檢查短網址是否已過期
    if url.expire_date and url.expire_date < timezone.now():
        url.delete()
        return HttpResponse("此短網址已過期並已被刪除。", status=404)
    
    # 更新訪問次數
    url.visit_count += 1
    url.save()
    
    # 進行重定向
    return redirect(url.orign_url)