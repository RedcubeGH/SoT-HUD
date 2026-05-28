# client.py
import socketio
import asyncio

sio = socketio.AsyncClient()

name = None

@sio.event
async def connect():
    print("[CLIENT] Connected")

    await sio.emit("identify", name)

@sio.event
async def disconnect():
    print("[CLIENT] Disconnected")

@sio.event
async def value_update(value):
    print(f"[SERVER] value = {value}\n", end="")
    
async def get_input():
    # runs blocking input safely
    return await asyncio.to_thread(input, "")

async def input_loop():
    while True:
        msg = await get_input()

        try:
            value = float(msg)

            print(f"[YOU -> SERVER] set_value = {value}")

            await sio.emit("set_value", value)

        except ValueError:
            print("Enter a number")

async def main():
    global name

    url = input("Server URL: ")
    name = input("Name: ")

    print(f"[CLIENT] Connecting as {name}")

    await sio.connect(url, transports=["websocket"])

    await input_loop()

asyncio.run(main())