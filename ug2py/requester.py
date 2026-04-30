import requests

class Requester:
    def __init__(self,token):
        self.token = token
        self.session = requests.Session()
        self.base_url = "https://alpha.celeste.gg/api/v9"
        self.headers = {"Authorization": f"{self.token}","User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome"}
    async def GET(self, path):
        return self.session.get(f"{self.base_url}/{path}", headers=self.headers)
    async def POST(self, path, data):
        return self.session.post(f"{self.base_url}/{path}", headers=self.headers, json=data)
    async def PATCH(self, path, data):
        return self.session.patch(f"{self.base_url}/{path}", headers=self.headers, json=data)
    async def DELETE(self, path):
        return self.session.delete(f"{self.base_url}/{path}", headers=self.headers)
    async def PUT(self, path, data):
        return self.session.put(f"{self.base_url}/{path}", headers=self.headers, json=data)