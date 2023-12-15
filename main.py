import os
import sys
import json
import time
import requests
import websocket
from keep_alive import keep_alive

# Configurable variables
status = "online"  # online/dnd/idle
custom_status = "Hey 👋"  # Put for custom status
usertoken = "" # Discord Authorization Token

authorization = "Authorization"
content_type = "Content-Type"
application_json = "application/json"
windows_os = "Windows 11"
chrome_browser = "Google Chrome"
windows_device = "Windows"

authorization_address = "https://discord.com/api/v9/users/@me"
websocket_address = "wss://gateway.discord.gg/?v=9&encoding=json"

def validate_token(usertoken):
    headers = {authorization: usertoken, content_type: application_json}
    try:
        response = requests.get(authorization_address, headers=headers)
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"Error validating token: {e}")
        return False

def get_user_data(headers):
    try:
        return requests.get(authorization_address, headers=headers).json()
    except requests.RequestException as e:
        print(f"Error fetching user data: {e}")
        return None

def apply_online_status(token, status):
    try:
        ws = websocket.WebSocket()
        ws.connect(websocket_address)
        start = json.loads(ws.recv())
        apply_auth(ws, start, token)
        apply_custom_status(ws, token)
        online = {"op": 1, "d": "None"}
        time.sleep(start["d"]["heartbeat_interval"] / 1000)
        ws.send(json.dumps(online))
    except websocket.WebSocketException as e:
        print(f"WebSocket Error: {e}")

def apply_auth(ws, start, token):
    auth = {
        "op": 2,
        "d": {
            "token": token,
            "properties": {
                "$os": windows_os,
                "$browser": chrome_browser,
                "$device": windows_device,
            },
            "presence": {"status": status, "afk": False},
        },
        "s": None,
        "t": None,
    }
    ws.send(json.dumps(auth))

def apply_custom_status(ws, token):
    cstatus = {
        "op": 3,
        "d": {
            "since": 0,
            "activities": [{"type": 4, "state": custom_status, "name": "Custom Status", "id": "custom"}],
            "status": status,
            "afk": False,
        },
    }
    ws.send(json.dumps(cstatus))

def main():
    os.system("clear")
    if not usertoken or not validate_token(usertoken):
        print("[ERROR] Please add a valid token.")
        sys.exit()

    headers = {authorization: usertoken, content_type: application_json}
    userinfo = get_user_data(headers)
    if userinfo:
        print(f"Logged in as {userinfo['username']}#{userinfo['discriminator']} ({userinfo['id']}).")
        while True:
            apply_online_status(usertoken, status)
            time.sleep(30)
    else:
        print("[ERROR] Failed to retrieve user data.")

keep_alive()
main()
