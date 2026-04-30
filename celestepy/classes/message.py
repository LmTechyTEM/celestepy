from .user import User
from ..requester import Requester
from .guild import Guild

class Message:
    def __init__(self, message, instance):
        self.channel_id = message["channel_id"]
        self.content = message["content"]
        self.id = message["id"]
        self.mentions:list[User] = []
        for user in message["mentions"]:
            self.mentions.append(User(user, instance))
        self.instance = instance
        self.author = User(message["author"], instance)
        self.guild_id = message.get("guild_id")
        if self.guild_id:
            for g in self.instance.guilds:
                if g.id == self.guild_id:
                    self.guild:Guild = g
        else:
            self.guild = None
    async def delete(self):
        return await self.instance.s.DELETE(f"channels/{self.channel_id}/messages/{self.id}")
    async def edit(self, content):
        return await self.instance.s.PATCH(f"channels/{self.channel_id}/messages/{self.id}", {"content": content})
    async def reply(self, content):
        data = {}
        msg_reference = {
            "message_id": self.id,
            "channel_id": self.channel_id,
            "guild_id": self.guild_id}
        
        data["message_reference"] = msg_reference
        data["content"] = content
        
        m = await self.instance.s.POST(f"channels/{self.channel_id}/messages", data)
        return Message(m.json(), self.instance)