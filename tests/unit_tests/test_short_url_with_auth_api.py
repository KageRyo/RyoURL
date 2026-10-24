import pytest
import random
import string
from http import HTTPStatus
from schemas.schemas import UrlSchema, ErrorSchema, CustomUrlCreateSchema

def generate_random_string(length=6):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

"""
需要認證的短網址 API 測試
"""

# POST /short-url-with-auth/custom 創建自定義短網址 (匿名用戶)
def test_anonymous_cannot_create_custom_url(anonymous_actions):
    data = CustomUrlCreateSchema(origin_url="https://www.example.com", short_string="custom")
    response = anonymous_actions.create_custom_url(str(data.origin_url), data.short_string)
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    error = ErrorSchema(**response.json())
    assert error.detail == "Unauthorized"


# GET /short-url-with-auth/all-my 取得所有自己的短網址 (匿名用戶)
def test_anonymous_cannot_get_all_my_urls(anonymous_actions):
    response = anonymous_actions.get_all_my_urls()
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    error = ErrorSchema(**response.json())
    assert error.detail == "Unauthorized"

# POST /short-url-with-auth/custom 創建自定義短網址 (已登入用戶)
def test_user_can_create_custom_url(user_actions):
    custom_string = generate_random_string()
    data = CustomUrlCreateSchema(origin_url="https://www.example.com", short_string=custom_string)
    response = user_actions.create_custom_url(str(data.origin_url), data.short_string)
    assert response.status_code == HTTPStatus.CREATED
    url = UrlSchema(**response.json())
    assert url.short_string == custom_string
    assert url.creator_username == "test_user_0000"

# GET /short-url-with-auth/all-my 取得所有自己的短網址 (已登入用戶)
def test_user_can_get_all_my_urls(user_actions, admin_actions):
    own_string = generate_random_string(10)
    foreign_string = generate_random_string(10)
    own_response = user_actions.create_custom_url("https://www.example.com/owned", own_string)
    assert own_response.status_code == HTTPStatus.CREATED
    own = UrlSchema(**own_response.json())
    foreign_created = False
    try:
        foreign_response = admin_actions.create_custom_url(
            "https://www.example.com/foreign", foreign_string
        )
        foreign_created = foreign_response.status_code == HTTPStatus.CREATED
        assert foreign_created
        foreign = UrlSchema(**foreign_response.json())
        assert own.creator_username != foreign.creator_username

        response = user_actions.get_all_my_urls()
        assert response.status_code == HTTPStatus.OK
        urls = [UrlSchema(**url) for url in response.json()]
        returned_ids = {url.short_string for url in urls}
        assert own.short_string in returned_ids
        assert foreign.short_string not in returned_ids
        assert all(url.creator_username == own.creator_username for url in urls)
    finally:
        user_actions.delete_url(own_string)
        if foreign_created:
            admin_actions.delete_url(foreign_string)

# DELETE /short-url-with-auth/url/{short_string} 刪除短網址 (已登入用戶)
def test_user_can_delete_own_url(user_actions):
    # 首先創建一個短網址
    custom_string = generate_random_string(10)  # 生成 10 個字符的隨機字符串
    data = CustomUrlCreateSchema(origin_url="https://www.example.com", short_string=custom_string)
    create_response = user_actions.create_custom_url(str(data.origin_url), data.short_string)
    assert create_response.status_code == HTTPStatus.CREATED, f"Failed to create URL: {create_response.json()}"

    url_data = UrlSchema(**create_response.json())
    short_string = url_data.short_string

    # 然後刪除這個短網址
    response = user_actions.delete_url(short_string)
    assert response.status_code == HTTPStatus.NO_CONTENT

    # 確認短網址已被刪除
    response = user_actions.delete_url(short_string)
    assert response.status_code == HTTPStatus.NOT_FOUND

# POST /short-url-with-auth/custom 創建自定義短網址 (管理員)
def test_admin_create_custom_short_url(admin_actions):
    data = CustomUrlCreateSchema(origin_url="https://www.example.com", short_string="adminurl")
    response = admin_actions.create_custom_url(str(data.origin_url), data.short_string)
    assert response.status_code == HTTPStatus.CREATED
    url = UrlSchema(**response.json())
    assert url.short_string == "adminurl"
    assert url.creator_username == "test_admin_0000"

# DELETE /short-url-with-auth/url/{short_string} 刪除短網址 (一般用戶刪除他人的網址)
def test_user_delete_others_short_url(user_actions):
    response = user_actions.delete_url("adminurl")
    assert response.status_code == HTTPStatus.FORBIDDEN
    error = ErrorSchema(**response.json())
    assert error.detail == "無權限刪除此短網址"
    
# DELETE /short-url-with-auth/url/{short_string} 刪除短網址 (管理員刪除任何人的網址)
def test_admin_delete_user_short_url(admin_actions):
    response = admin_actions.delete_url("adminurl")
    assert response.status_code == HTTPStatus.NO_CONTENT