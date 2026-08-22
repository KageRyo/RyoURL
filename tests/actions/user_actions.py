class UserActions:
    def __init__(self, client):
        self.client = client

    def create_custom_url(self, origin_url, short_string):
        return self.client.post("short-url-with-auth/custom", json={
            "origin_url": str(origin_url),
            "short_string": short_string
        })

    def get_all_my_urls(self):
        return self.client.get("short-url-with-auth/all-my")

    def delete_url(self, short_string):
        return self.client.delete(f"short-url-with-auth/url/{short_string}")

    def get_user_info(self, username):
        return self.client.get(f"user/info?username={username}")

    def create_short_url(self, origin_url):
        return self.client.post("short-url/short", json={"origin_url": origin_url})
    
    def get_all_urls(self):
        return self.client.get("admin/all-urls")

    def delete_expired_urls(self):
        return self.client.delete("admin/expire-urls")

    def get_all_users(self):
        return self.client.get("admin/users")

    def update_user_type(self, username, user_type):
        return self.client.put(f"admin/user/{username}", params={"user_type": user_type})

    def delete_user(self, username):
        return self.client.delete(f"admin/user/{username}")
    
    def get(self, path):
        return self.client.get(path)
    
    def post(self, path, json=None):
        return self.client.post(path, json=json)

    def put(self, path, params=None):
        return self.client.put(path, params=params)

    def delete(self, path):
        return self.client.delete(path)