import os
import sys
import pytest
import requests
from urllib.parse import urljoin
from dotenv import load_dotenv

from actions.admin_actions import AdminActions
from actions.user_actions import UserActions
from actions.anonymous_actions import AnonymousActions

# 載入 .env 文件
load_dotenv()

# 環境變數設定
BASE_URL = os.getenv("BASE_URL")
TEST_USER = {
    "username": os.getenv("TEST_USER_USERNAME"),
    "password": os.getenv("TEST_USER_PASSWORD")
}
ADMIN_USER = {
    "username": os.getenv("ADMIN_USER_USERNAME"),
    "password": os.getenv("ADMIN_USER_PASSWORD")
}

# 載入 Schemas 子模組
sys.path.append(os.path.join(os.path.dirname(__file__), 'schemas'))

from schemas.schemas import (UrlSchema, UserResponseSchema, UserInfoSchema,
                             ErrorSchema, UrlCreateSchema, CustomUrlCreateSchema)

# API 客戶端類別
class APIClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.token = None

    def login(self, username, password):
        response = self.post("auth/login", json={"username": username, "password": password})
        if response.status_code == 200:
            self.token = response.json()["access"]
        return response

    def request(self, method, endpoint, **kwargs):
        url = urljoin(self.base_url, endpoint)
        headers = kwargs.pop("headers", {})
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        response = requests.request(method, url, headers=headers, **kwargs)
        print(f"Request to {url}: Status {response.status_code}, Content: {response.text[:200]}")
        return response

    def get(self, endpoint, **kwargs):
        return self.request("GET", endpoint, **kwargs)

    def post(self, endpoint, **kwargs):
        return self.request("POST", endpoint, **kwargs)

    def delete(self, endpoint, **kwargs):
        return self.request("DELETE", endpoint, **kwargs)

    def put(self, endpoint, **kwargs):
        return self.request("PUT", endpoint, **kwargs)

# 匿名使用者客戶端
@pytest.fixture
def api_client():
    return APIClient(BASE_URL)

# 一般使用者客戶端
@pytest.fixture
def user_client(api_client):
    api_client.login(TEST_USER["username"], TEST_USER["password"])
    return api_client

# 管理員客戶端
@pytest.fixture
def admin_client(api_client):
    api_client.login(ADMIN_USER["username"], ADMIN_USER["password"])
    return api_client

# 管理員的 API 操作行為
@pytest.fixture
def admin_actions(admin_client):
    return AdminActions(admin_client)

# 一般使用者的 API 操作行為
@pytest.fixture
def user_actions(user_client):
    return UserActions(user_client)

# 匿名使用者的 API 操作行為
@pytest.fixture
def anonymous_actions(api_client):
    return AnonymousActions(api_client)