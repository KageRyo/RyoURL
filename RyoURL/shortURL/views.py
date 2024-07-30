from django.shortcuts import get_object_or_404, redirect
from .models import Url

# 將短網址導向原網址的函式
def redirectShortUrl(request, short_string):
    url = get_object_or_404(Url, short_string=short_string)
    url.visit_count += 1
    url.save()
    return redirect(url.orign_url)