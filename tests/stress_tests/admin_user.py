import random
import string
from locust import HttpUser, task, between
from locustfile import BASE_URL
from actions.admin_actions import AdminActions

# 管理員
class AdminUser(HttpUser):
    host = BASE_URL
    wait_time = between(5, 10)
    
    # 開始時，先進行登入
    def on_start(self):
        self.login()
        self.admin_actions = AdminActions(self.client)
    
    def login(self):
        response = self.client.post("auth/login", json={
            "username": "test_admin_0000",
            "password": "test_admin_pwd0"
        })
        if response.status_code == 200:
            data = response.json()
            self.token = data["access"]
            self.client.headers = {"Authorization": f"Bearer {self.token}"}
    
    # 取得所有短網址
    @task(3)
    def get_all_urls(self):
        self.admin_actions.get_all_urls()
    
    # 刪除過期短網址
    @task(1)
    def delete_expired_urls(self):
        self.admin_actions.delete_expired_urls()
    
    # 取得所有使用者
    @task(2)
    def get_all_users(self):
        self.admin_actions.get_all_users()
    
    # 更新使用者類型
    @task(1)
    def update_user_type(self):
        response = self.admin_actions.get_all_users()
        if response.status_code == 200:
            users = response.json()
            if users:
                user = random.choice(users)
                new_type = random.choice([0, 1, 2])
                self.admin_actions.update_user_type(user['username'], new_type)
    
    # 刪除使用者
    @task(1)
    def delete_user(self):
        response = self.admin_actions.get_all_users()
        if response.status_code == 200:
            users = response.json()
            test_users = [user for user in users if user['username'].startswith('test_user_')]
            if test_users:
                user_to_delete = random.choice(test_users)
                self.admin_actions.delete_user(user_to_delete['username'])