import pytest
from django.utils import timezone

from shortURL.models import Url
from shortURL.api import UrlSchema

# 新增短網址 API 測試
# API：creatShortUrl [POST]
@pytest.mark.django_db
def test_createShortUrl(client):
    response = client.post(
        '/api/createShortUrl?oriUrl=https://www.google.com'
    )
    assert response.status_code == 200
    response_data = UrlSchema(**response.json())
    assert response_data.oriUrl == "https://www.google.com"
    assert response_data.srtUrl
    assert response_data.creDate

# 以縮短網址查詢原網址 API 測試
# API：lookforOriUrl [GET]
@pytest.mark.django_db
def test_lookforOriUrl(client):
    url = Url.objects.create(
        oriUrl='https://www.example.com', 
        srtUrl='test01',
        creDate=timezone.now()
    )
    response = client.get(f'/api/lookforOriUrl/{url.srtUrl}')
    assert response.status_code == 200
    response_data = UrlSchema(**response.json())
    assert response_data.oriUrl == url.oriUrl
    assert response_data.srtUrl == url.srtUrl
    assert response_data.creDate

# 查詢所有短網址 API 測試
# API：getAllUrl [GET]
@pytest.mark.django_db
def test_getAllUrl(client):
    Url.objects.create(
        oriUrl='https://www.example.com', 
        srtUrl='test01',
        creDate=timezone.now()
    )
    Url.objects.create(
        oriUrl='https://www.example.org', 
        srtUrl='test02',
        creDate=timezone.now()
    )
    response = client.get('/api/getAllUrl')
    assert response.status_code == 200
    response_data = [UrlSchema(**url) for url in response.json()]
    assert len(response_data) == 2
    for url in response_data:
        assert url.oriUrl
        assert url.srtUrl
        assert url.creDate