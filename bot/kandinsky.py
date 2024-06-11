from os import getenv

import telethon
from telethon import TelegramClient
from dotenv import load_dotenv


load_dotenv()

api_id = int(getenv("API_ID"))
api_hash = getenv("API_HASH")

bot_username = '@kandinsky21_bot'
client = TelegramClient('anon', api_id, api_hash)


async def get_message(entity):
    messages = await client.get_messages(entity, limit=1)
    message = messages[0]
    while not isinstance(message.reply_markup, telethon.tl.types.ReplyInlineMarkup):
        messages = await client.get_messages(entity, limit=1)
        message = messages[0]
    return message


async def mix_via_kandinsky(photo_path):
    await client.start()

    entity = await client.get_entity(bot_username)

    await client.send_message(entity, "/start")

    message: telethon.tl.types.ReplyInlineMarkup = await get_message(entity)
    rows = message.reply_markup.rows
    for i, row in enumerate(rows):
        for j, button in enumerate(row.buttons):
            if "Смешивание" in button.text:
                await message.click(i, j)

    message = await get_message(entity)
    rows = message.reply_markup.rows
    for i, row in enumerate(rows):
        for j, button in enumerate(row.buttons):
            if "Картинка + картинка" in button.text:
                await message.click(i, j)

    message = [await client.get_messages(entity, limit=1) for _ in range(1)][-1][0]
    await client.send_file(entity, "photos/user_data/"+photo_path)

    message = [await client.get_messages(entity, limit=1) for _ in range(1)][-1][0]
    await client.send_file(entity, "photos/user_data/tiger_"+photo_path)

    message = await get_message(entity)
    rows = message.reply_markup.rows
    for i, row in enumerate(rows):
        for j, button in enumerate(row.buttons):
            if "Начать генерацию" in button.text:
                await message.click(i, j)

    message = [i async for i in client.iter_messages(entity, limit=5)][1]
    result_path = "photos/user_data/mixed_"+photo_path
    await client.download_media(message.media, result_path)

    message = await get_message(entity)
    rows = message.reply_markup.rows
    for i, row in enumerate(rows):
        for j, button in enumerate(row.buttons):
            if "Новое смешивание" in button.text:
                await message.click(i, j)