from telethon.sync import TelegramClient
from telethon.tl.types import InputMessagesFilterPhotos
import json
import os
from datetime import datetime
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH
import logging

logging.basicConfig(filename='scrape.log', level=logging.INFO)

async def scrape_channel(channel_url, output_dir):
    async with TelegramClient('session', TELEGRAM_API_ID, TELEGRAM_API_HASH) as client:
        channel = await client.get_entity(channel_url)
        os.makedirs(output_dir, exist_ok=True)
        messages = []
        async for message in client.iter_messages(channel, limit=100):
            msg_data = {
                "id": message.id,
                "date": message.date.isoformat(),
                "text": message.text,
                "has_image": message.photo is not None
            }
            if message.photo:
                photo_path = f"{output_dir}/images/{message.id}.jpg"
                os.makedirs(f"{output_dir}/images", exist_ok=True)
                await message.download_media(file=photo_path)
                msg_data["photo_path"] = photo_path
            messages.append(msg_data)
        output_path = f"{output_dir}/{channel.username}_{datetime.now().strftime('%Y-%m-%d')}.json"
        with open(output_path, 'w') as f:
            json.dump(messages, f, indent=2)
        logging.info(f"Scraped {channel.username} at {datetime.now()}")

if __name__ == "__main__":
    import asyncio
    channels = ["Chemed", "lobelia4cosmetics", "tikvahpharma"]
    for channel in channels:
        asyncio.run(scrape_channel(f"https://t.me/{channel}", f"data/raw/telegram_messages/{datetime.now().strftime('%Y-%m-%d')}/{channel}"))