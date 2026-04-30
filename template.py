import ug2py
import asyncio

token="YOUR TOKEN HERE"

class Client(ug2py.Client):
    async def on_ready(self, user):
        print(f"Logged in as {user.username}")

bot = Client(token)
     
asyncio.run(bot.start())