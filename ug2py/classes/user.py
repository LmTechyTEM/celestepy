class User:
    def __init__(self, user, instance):
        self.instance = instance
        self.id = user["id"]
        self.username = user["username"]
    async def send_friend_request(self):
        await self.instance.s.PUT(f"users/@me/relationships/{self.id}",{})