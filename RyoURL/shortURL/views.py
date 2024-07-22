from django.shortcuts import get_object_or_404, redirect
from .models import Url

def redirectShortUrl(request, strUrl):
    url = get_object_or_404(Url, srtUrl=strUrl)
    return redirect(url.oriUrl)