import pytest
from django.urls import reverse
from shortURL.models import Url

# 新增短網址 API 測試
# API：creatShortUrl [POST]
@pytest.mark.django_db
def test_creatShortUrl(client):
    response = client.post(
        reverse('creatShortUrl'), 
        {'oriUrl': 'https://www.google.com'}
    )
    assert response.status_code == 201 # 201 Created
    assert 'srtUrl' in response.json() # 檢查 srtUrl 是否有在回傳的 JSON 中（檢查是否成功創立短網址）

# 以縮短網址查詢原網址 API 測試
# API：lookforOriUrl [GET]
@pytest.mark.django_db
def test_lookforOriUrl(client):
    url = Url.objects.create(           # 假設一筆短網址資料
        oriUrl='https://www.example.com', 
        srtUrl='test01',
        creDate='2000-01-01 00:00:00'
    )
    response = client.get(
        reverse('lookforOriUrl', kwargs={'srtUrl': 'test01'}))
    assert response.status_code == 200 # 200 OK
    assert response.json()['oriUrl'] == url.oriUrl # 檢查回傳的原網址是否正確

# 查詢所有短網址 API 測試
# API：getAllUrl [GET]
@pytest.mark.django_db
def test_getAllUrl(client):
    # 假設有兩筆短網址資料
    Url.objects.create(
        oriUrl='https://www.example.com', 
        srtUrl='test01',
        creDate='2000-01-01 00:00:00'
    )
    Url.objects.create(
        oriUrl='https://www.example.com', 
        srtUrl='test02',
        creDate='2000-01-01 00:01:00'
    )
    response = client.get(reverse('getAllUrl'))
    assert response.status_code == 200 # 200 OK
    assert len(response.json()) == 2   # 檢查回傳的短網址數量是否正確