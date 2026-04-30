class Channel:
    def __init__(self, data, instance):
        #print(data)
        self.id = data.get("id")
        self.name = data.get("name")
        self.topic = data.get("topic")
        self.type = data.get("type")
    async def send(self, content):
        await self.instance.s.POST(f"channels/{self.id}/messages", {"content": content})