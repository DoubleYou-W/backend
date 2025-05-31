import os
import requests

from telethon import TelegramClient, events

API_URL = os.getenv("API_URL", "http://localhost:8000")
API_URL_UPDATE = f"{API_URL}/api/update"

api_id = os.getenv("TELEGRAM_API_ID")
api_hash = os.getenv("TELEGRAM_API_HASH")

client = TelegramClient('session', api_id, api_hash)

@client.on(events.NewMessage(incoming=True))
async def handle_incoming_message(event):
    if (event.is_group): return

    sender = await event.get_sender()
    sender_name = sender.username or sender.first_name or str(sender.id)

    msg = event.message.message.strip().replace("\n", " ").replace("\r", " ")

    data = {
        "source": "telegram",
        "timestamp": f"{int(event.message.date.timestamp())}",
        "content": f"received a telegram message from {sender_name} in chat {event.chat.title if event.chat else 'Private'}. The content of the message is {msg}"
    }

    response = requests.post(API_URL_UPDATE, json=data)

@client.on(events.NewMessage(outgoing=True))
async def handle_outgoing_message(event):
    if (event.is_group): return

    msg = event.message.message.strip().replace("\n", " ").replace("\r", " ")

    data = {
        "source": "telegram",
        "timestamp": f"{int(event.message.date.timestamp())}",
        "content": f"sent a telegram message in chat '{event.chat.title if event.chat else 'Private'}'. The content of the message is {msg}"
    }

    response = requests.post(API_URL_UPDATE, json=data)

if __name__ == "__main__":
    client.start()
    client.loop.run_until_complete(client.run_until_disconnected())