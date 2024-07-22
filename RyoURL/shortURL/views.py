from django.shortcuts import get_object_or_404, redirect
from .models import Url

# 將短網址導向原網址的函式
def redirectShortUrl(request, strUrl):
    url = get_object_or_404(Url, srtUrl=strUrl)
    return redirect(url.oriUrl)