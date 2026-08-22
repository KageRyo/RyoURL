import random
import string
from locust import HttpUser, task, between
from locustfile import BASE_URL
from actions.anonymous_actions import AnonymousActions

def generate_random_string(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# 匿名使用者
class AnonymousUser(HttpUser):
    host = BASE_URL
    wait_time = between(1, 5)
    
    def on_start(self):
        self.anonymous_actions = AnonymousActions(self.client)
    
    # 建立短網址
    @task(3)
    def create_short_url(self):
        data = {"origin_url": f"https://www.example.com/{random.randint(1, 1000)}"}
        response = self.anonymous_actions.create_short_url(data['origin_url'])
        if response.status_code == 201:
            self.short_string = response.json()['short_string']
    
    # 取得原始網址
    @task(2)
    def get_original_url(self):
        if hasattr(self, 'short_string'):
            self.anonymous_actions.get_original_url(self.short_string)
    
    # 註冊新使用者
    @task(1)
    def register_user(self):
        username = f"test_user_{generate_random_string()}"
        self.anonymous_actions.register_user(username, "test_password")