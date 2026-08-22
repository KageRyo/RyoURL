class AnonymousActions:
    def __init__(self, client):
        self.client = client

    def create_short_url(self, origin_url):
        return self.client.post("short-url/short", json={"origin_url": origin_url})
    
    def create_custom_url(self, origin_url, short_string):
        return self.client.post("short-url-with-auth/custom", json={
            "origin_url": str(origin_url),
            "short_string": short_string
        })
        
    def get_all_my_urls(self):
        return self.client.get("short-url-with-auth/all-my")

    def get_original_url(self, short_string):
        return self.client.get(f"short-url/origin/{short_string}")

    def register_user(self, username, password):
        return self.client.post("auth/register", json={
            "username": username,
            "password": password
        })
        
    def get(self, path):
        return self.client.get(path)
    
    def post(self, path, json=None):
        return self.client.post(path, json=json)

    def put(self, path, params=None):
        return self.client.put(path, params=params)

    def delete(self, path):
        return self.client.delete(path)