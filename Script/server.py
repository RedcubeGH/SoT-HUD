# server.py
import socketio
from aiohttp import web
from pyngrok import ngrok
import webbrowser
import subprocess
import os
import sys

sio = socketio.AsyncServer(cors_allowed_origins="*")
app = web.Application()
sio.attach(app)

shared_value = 0.0

clients = {}

@sio.event
async def connect(sid, environ):
    print(f"[CONNECT] sid={sid} (waiting for identify)")

@sio.event
async def identify(sid, name):
    clients[sid] = name
    print(f"[IDENTIFY] {name} connected with sid={sid}")

    # send current state
    await sio.emit("value_update", shared_value, to=sid)

@sio.event
async def disconnect(sid):
    name = clients.get(sid, "UNKNOWN")
    print(f"[DISCONNECT] {name} (sid={sid})")

    clients.pop(sid, None)

@sio.event
async def set_value(sid, value):
    global shared_value

    name = clients.get(sid, "UNKNOWN")

    print(f"[{name} -> SERVER] set_value = {value}")

    shared_value = float(value)

    print(f"[SERVER] shared_value = {shared_value}")

    await sio.emit("value_update", shared_value)

async def start(app):
    tunnel = ngrok.connect(5000)

    print(f"SERVER URL: {tunnel.public_url}")

app.on_startup.append(start)
try:
    web.run_app(app, port=5000)
except Exception as e:
    webbrowser.open("https://dashboard.ngrok.com/get-started/your-authtoken")
    token = input("ngrok authtoken not configured. Enter your ngrok authtoken to continue: ")

    subprocess.run(["ngrok", "config", "add-authtoken", token], check=True)
    # restart this script so the new ngrok config is picked up
    os.execv(sys.executable, [sys.executable] + sys.argv)