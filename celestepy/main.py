import asyncio
import contextlib
import json
import random
from .classes import Guild
from .classes import Message
from .classes import User
from .requester import Requester
import websockets
from websockets.exceptions import ConnectionClosed, InvalidStatusCode
import threading

class Client:
    def __init__(self, token):
        self.token = token
        self.ws_url = "wss://alpha-gateway.celeste.gg/?encoding=json&v=9"
        self.s:Requester = Requester(token)
        self.ws = None
        self.User:User = None
        self.sequence = None
        self.session_id = None
        self.heartbeat_task = None
        self.running = False
        self.reconnect = True

    def make_identify_payload(self):
        return {
            "op": 2,
            "d": {
                "token": self.token,
                "capabilities": 1734653,
                "properties": {
                    "os": "Linux",
                    "browser": "Chrome",
                    "device": "",
                    "system_locale": "en-US",
                    "has_client_mods": None,
                    "browser_user_agent": (
                        "Mozilla/5.0 (X11; Linux x86_64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/147.0.0.0 Safari/537.36"
                    ),
                    "browser_version": "147.0.0.0",
                    "os_version": "",
                    "referrer": "",
                    "referring_domain": "",
                    "referrer_current": "",
                    "referring_domain_current": "",
                    "release_channel": "canary",
                    "client_build_number": 531672,
                    "client_event_source": None,
                    "client_launch_id": "29fba90b-19e6-434c-bf39-a4ffab175cfc",
                    "is_fast_connect": True,
                },
                "client_state": {
                    "guild_versions": {}
                }
            }
        }

    def make_resume_payload(self):
        return {
            "op": 6,
            "d": {
                "token": self.token,
                "session_id": self.session_id,
                "seq": self.sequence
            }
        }

    async def send_json(self, payload):
        if self.ws is None:
            raise RuntimeError("WebSocket is not connected")

        await self.ws.send(json.dumps(payload, separators=(",", ":")))

    async def heartbeat_loop(self, interval_ms):
        interval = interval_ms / 1000

        try:
            while self.running:
                await asyncio.sleep(interval)

                await self.send_json({
                    "op": 1,
                    "d": self.sequence
                })

        except asyncio.CancelledError:
            raise

        except ConnectionClosed:
            pass

    async def start(self):
        self.running = True
        attempt = 0

        while self.running:
            try:
                await self.connect_once()
                attempt = 0

            except InvalidStatusCode as e:
                print(f"HTTP error while connecting: {e.status_code}")
                break

            except ConnectionClosed as e:
                print(f"Connection closed: {e.code} {e.reason}")

            except Exception as e:
                print(f"Gateway error: {type(e).__name__}: {e}")
                # print error line
                import traceback
                traceback.print_exc()

            finally:
                await self.cleanup_heartbeat()

            if not self.running or not self.reconnect:
                break

            attempt += 1
            delay = min(60, 2 ** min(attempt, 6)) + random.uniform(0, 3)
            print(f"Reconnecting in {delay:.1f}s...")
            await asyncio.sleep(delay)

    async def connect_once(self):
        #print("Connecting...")

        async with websockets.connect(
            self.ws_url,
            open_timeout=15,
            close_timeout=5,
            ping_interval=None,
            max_queue=32,
            compression=None,
        ) as ws:
            self.ws = ws
            #print("Connected")

            async for raw in ws:
                try:
                    data = json.loads(raw)
                except json.JSONDecodeError:
                    print("Received non-JSON packet")
                    continue

                await self.handle_gateway_packet(data)

    async def handle_gateway_packet(self, data):
        op = data.get("op")
        event_name = data.get("t")

        if data.get("s") is not None:
            self.sequence = data["s"]

        if op == 10:
            interval = data["d"]["heartbeat_interval"]

            self.heartbeat_task = asyncio.create_task(
                self.heartbeat_loop(interval)
            )

            if self.session_id and self.sequence is not None:
                print("Resuming session...")
                await self.send_json(self.make_resume_payload())
            else:
                print("Identifying...")
                await self.send_json(self.make_identify_payload())

            return
        if op == 1:
            await self.send_json({
                "op": 1,
                "d": self.sequence
            })
            return

        if op == 11:
            return

        if op == 9:
            print("Invalid session")
            self.session_id = None
            self.sequence = None
            return

        if op == 0:
            await self.dispatch(event_name, data.get("d", {}))
        

    async def dispatch(self, event_name, event_data):
        print(f"Event: {event_name}")
        if event_name == "PRESENCE_UPDATE":
            #print(event_data)
            return
        if event_name == "READY":
            self.session_id = event_data.get("session_id")
            info = json.dumps(event_data, indent=4)
            data = json.loads(info)
            self.guilds:list[Guild] = []
            self.User:User = User(data["user"],self)
            self.ws_url = data["resume_gateway_url"]
            for guild in data["guilds"]:
                g = Guild(guild,self)
                channels = []
                for channel in g.channels:
                    channels.append(channel.id)
                channel_subs = {channel_id: [[0, 99]] for channel_id in channels}

                payload = {
                    "op":37,
                        "d":{"subscriptions":
                            {g.id:{
                            "typing":True,
                            "activities":True,
                            "threads":True,
                            "channels":channel_subs
                             }
                            }
                        }
                    }
                
                await self.send_json(payload)
                self.guilds.append(Guild(guild,self))
            keys = data.keys()
            #print(keys.keys())
            await self.on_ready(self)
            return
        if event_name == "PASSIVE_UPDATE_V2":
            #print(json.dumps(event_data, indent=4))
            return
        
        if event_name == "MESSAGE_CREATE":
            await self.on_message_create(Message(event_data,self))
            return


    async def cleanup_heartbeat(self):
        if self.heartbeat_task:
            self.heartbeat_task.cancel()

            with contextlib.suppress(asyncio.CancelledError):
                await self.heartbeat_task

            self.heartbeat_task = None

    async def close(self):
        self.running = False

        await self.cleanup_heartbeat()

        if self.ws:
            await self.ws.close()

    # Events

    async def on_ready(self, data):
        pass

    async def on_message_create(self, data):
        pass