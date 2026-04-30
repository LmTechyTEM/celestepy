import ug2py
import asyncio

class Client(ug2py.Client):
    async def on_ready(self, user):
        print(f"Logged in as {user.username}")

bot = Client("YOUR TOKEN HERE")
     
asyncio.run(bot.start())