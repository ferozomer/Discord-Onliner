import sys
import json
import time
import requests
import websocket

class DiscordStatusUpdater:
    def __init__(self, token: str, status: str, custom_status: str):
        self.token = token
        self.status = status
        self.custom_status = custom_status
        self.headers = {"Authorization": token, "Content-Type": "application/json"}
        self.validate_token()
        self.user_info = self.get_user_info()

    def validate_token(self):
        response = requests.get('https://discordapp.com/api/v9/users/@me', headers=self.headers)
        if response.status_code != 200:
            print("[ERROR] Your token might be invalid. Please check it again.")
            sys.exit()

    def get_user_info(self):
        return requests.get('https://discordapp.com/api/v9/users/@me', headers=self.headers).json()

    def connect_websocket(self):
        ws = websocket.WebSocket()
        ws.connect("wss://gateway.discord.gg/?v=9&encoding=json")
        start = json.loads(ws.recv())
        heartbeat_interval = start["d"]["heartbeat_interval"]
        self.authenticate(ws)
        self.update_custom_status(ws)
        self.maintain_connection(ws, heartbeat_interval)

    def authenticate(self, ws):
        auth_payload = {
            "op": 2,
            "d": {
                "token": self.token,
                "properties": {
                    "$os": "Windows 10",
                    "$browser": "Google Chrome",
                    "$device": "Windows",
                },
                "presence": {"status": self.status, "afk": False},
            },
            "s": None,
            "t": None,
        }
        ws.send(json.dumps(auth_payload))

    def update_custom_status(self, ws):
        custom_status_payload = {
            "op": 3,
            "d": {
                "since": 0,
                "activities": [
                    {
                        "type": 4,
                        "state": self.custom_status,
                        "name": "Custom Status",
                        "id": "custom",
                    }
                ],
                "status": self.status,
                "afk": False,
            },
        }
        ws.send(json.dumps(custom_status_payload))

    def maintain_connection(self, ws, heartbeat_interval):
        keep_alive_payload = {"op": 1, "d": "None"}
        try:
            while True:
                time.sleep(heartbeat_interval / 1000)
                ws.send(json.dumps(keep_alive_payload))
        except KeyboardInterrupt:
            print("Interrupted by user, closing connection.")
            ws.close()

    def run(self):
        username = self.user_info["username"]
        discriminator = self.user_info["discriminator"]
        user_id = self.user_info["id"]
        print(f"Logged in as {username}#{discriminator} ({user_id}).")
        try:
            self.connect_websocket()
        except KeyboardInterrupt:
            print("Disconnected successfully.")

# Usage
usertoken = "" #Put token inside "" 
status = "online" #Online/idle/dnd
custom_status = "Playing Grand Theft Auto V"  #for no custom status
discord_updater = DiscordStatusUpdater(usertoken, status, custom_status)
discord_updater.run()
