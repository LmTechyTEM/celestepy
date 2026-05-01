import celestepy
import asyncio

token="YOUR TOKEN HERE"

class Commands(celestepy.Commands):
    async def test(self, message:celestepy.Message):
        await message.reply("Test")

class Client(celestepy.Client):
    async def on_ready(self, user):
        print(f"Logged in as {user.username}")

bot = Client(token, commands=Commands(prefix="!"))
     
asyncio.run(bot.start())