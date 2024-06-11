from os import getenv
from os.path import exists
from json import load
from random import choice
from pathlib import Path
from shutil import rmtree

import asyncio
import telebot
from telebot import types
from telebot.async_telebot import AsyncTeleBot
from dotenv import load_dotenv

import database
import photo_service
from kandinsky import mix_via_kandinsky


load_dotenv()

facts_file_name = "facts.json"

ADMIN_USER_ID = getenv("ADMIN_USER_ID")

TOKEN = getenv("TOKEN")
bot = AsyncTeleBot(token=TOKEN)

if not exists("database.sqlite"):
    database.create_database("database.sqlite")
db = database.Database()

task_queue = asyncio.Queue()


async def process_queue():
    while True:
        task = await task_queue.get()
        try:
            result = await task['func'](task['message'], *task['args'])
            task['future'].set_result(result)
        except Exception as e:
            task['future'].set_exception(e)
        finally:
            task_queue.task_done()


def get_random_fact(filename):
    with open(filename, 'r') as file:
        data = load(file)
        facts = data['facts']
        return choice(facts)


def validate(msg, expected):
    if isinstance(msg, telebot.types.CallbackQuery):
        return expected == "callback"
    return expected == msg.content_type


async def start(message):
    if not validate(message, "text"):
        await bot.send_message(message.chat.id, "Отправь текстовое сообщение")
        return start.__name__

    with open("photos/static/step1.png", "rb") as f:
        photo = f.read()

    markup = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton("Загрузить фото 🐅", callback_data="upload_photo"))

    await bot.send_photo(message.chat.id, photo,
                         caption="Привет, я ТигроБот! 🐯 Я умный тигр и я могу определить, на кого из моих сородичей ты похож. Чтобы узнать ответ, нажми на кнопку и загрузи свое фото!",
                         reply_markup=markup)

    return request_photo.__name__


async def request_photo(callback):
    if not validate(callback, "callback"):
        await bot.send_message(callback.message.chat.id, "Нажми на кнопку")
        return request_photo.__name__

    await bot.send_message(callback.message.chat.id, "Жду твое фото!")

    return receive_photo.__name__


async def receive_photo(message):
    if not validate(message, "photo"):
        await bot.send_message(message.chat.id, "Отправь фото")
        return receive_photo.__name__

    photo = message.photo
    await bot.send_message(message.chat.id, "Кажется, я знаю, кто ты 😏")

    file_id = photo[-1].file_id
    file_info = await bot.get_file(file_id)
    photo = await bot.download_file(file_info.file_path)

    with open(f"photos/user_data/{file_id}.png", "wb") as f:
        f.write(photo)

        db.add_photo(message.chat.id, f"{file_id}.png")

    tiger_photo, tiger_description = photo_service.get_photo(photo)

    with open(f"photos/user_data/tiger_{file_id}.png", "wb") as f:
        f.write(tiger_photo)

    await bot.send_photo(message.chat.id, tiger_photo, caption=tiger_description)

    random_fact = get_random_fact(facts_file_name)
    await bot.send_message(message.chat.id, f"💡*Интересный факт:*\n{random_fact}", parse_mode="Markdown")

    buttons = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("Да", callback_data="confirm_analysis"))
    buttons.add(types.InlineKeyboardButton("А что это?", callback_data="ask_question"))
    buttons.add(types.InlineKeyboardButton("Нет", callback_data="decline_analysis"))
    await bot.send_message(message.chat.id, "Хочешь микс с Кандинским? 🧑🏻‍ 🪄 🐯", reply_markup=buttons)

    return analyze_photo.__name__


async def analyze_photo(callback):
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)

    if not validate(callback, "callback"):
        await bot.send_message(callback.message.chat.id, "Нажми на кнопку с твоим вариантом ответа")
        return analyze_photo.__name__

    match callback.data:
        case "confirm_analysis":
            return await mix_photo_in_queue(callback.message, db.get_photo(callback.from_user.id))
        case "ask_question":
            markup = types.InlineKeyboardMarkup().add(
                types.InlineKeyboardButton("Давай! 💪🎨", callback_data="mix_photo"))
            markup.add(types.InlineKeyboardButton("Я передумал", callback_data="skip_mix"))
            await bot.send_message(callback.message.chat.id,
                                  "Кандинский - это нейросеть, созданная разработчиками из Сбера. "
                                   "Он может соединить твое фото с фото твоего тигрового двойника 🐯🔗 Интересно же, правда? "
                                   "🤩 Готов попробовать? 😄", reply_markup=markup)

            return choose_mix_option.__name__
        case "decline_analysis":
            return await tigers_shocked(callback.message)
            # return await skip_analysis(callback.message)

    await bot.send_message(callback.message.chat.id,
                           "Ой, ты нажал не на ту кнопку! Вернись к последнему сообщению и выбери свой вариант ответа.")
    return analyze_photo.__name__


async def skip_mix(message):
    with open("photos/static/skip_mix.png", "rb") as f:
        photo = f.read()

    markup = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton("А что ты еще умеешь?", callback_data="more_options"))
    await bot.send_photo(message.chat.id, photo,
        "Странно! 🐅 Но ничего страшного. Если вдруг захочешь сделать микс, знай, что я всегда готов к новым экспериментам! 🎨🐾", reply_markup=markup)

    return end.__name__


async def tigers_shocked(message):
    with open("photos/static/step6.png", "rb") as f:
        photo = f.read()

    markup = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton("А что ты еще умеешь?", callback_data="more_options"))
    await bot.send_photo(message.chat.id, photo, caption=
    "Мои малыши-помощники тигрята удивлены! 🐯😮 Но не переживай, может быть в следующий раз тебе захочется создать что-то особенное с нами! 🐾🎨", reply_markup=markup)

    return end.__name__


async def choose_mix_option(callback):
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)

    if not validate(callback, "callback"):
        await bot.send_message(callback.message.chat.id, "Нажми на кнопку с твоим вариантом ответа")
        return choose_mix_option.__name__

    match callback.data:
        case "mix_photo":
            return await mix_photo_in_queue(callback.message, db.get_photo(callback.from_user.id))
        case "skip_mix":
            return await skip_mix(callback.message)

    await bot.send_message(callback.message.chat.id,
                           "Ой! Кажется, ты нажал не на ту кнопку. Вернись к последнему сообщению и выбери правильный вариант!")

    return choose_mix_option.__name__


async def end(callback):
    if not validate(callback, "callback"):
        return end.__name__

    return await more_options(callback.message)


async def also_end(callback):
    if not validate(callback, "callback"):
        return also_end.__name__

    with open("photos/static/finish.png", "rb") as f:
        photo = f.read()

    await bot.send_photo(callback.message.chat.id, photo, caption="Приходи в гости! Я буду тебя ждать 🤗🌿")

    return start.__name__


async def skip_analysis(message):
    markup = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton("Тебе спасибо! Ты классный ❤️", callback_data="also_end"))
    await bot.send_message(message.chat.id,
                           "Тогда спасибо, что заглянул поболтать со мной! 🐾 А то мне бывает скучно одному 🥺 Надеюсь, тебе было интересно со мной общаться! Буду рад видеть тебя здесь снова 🐯🧡", reply_markup=markup)

    return also_end.__name__


async def mix_photo(message, photo_path):
    await mix_via_kandinsky(photo_path)

    with open("photos/user_data/mixed_" + photo_path, "rb") as f:
        mixed_photo = f.read()

    markup = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton("А что ты еще умеешь?", callback_data="more_options"))
    await bot.send_photo(message.chat.id, mixed_photo, caption="Вот, что у нас получилось✨😱", reply_markup=markup)

    return end.__name__


async def more_options(message):
    markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("Хочу еще разок 🤩", callback_data="restart"))
    markup.add(types.InlineKeyboardButton("Хочу поделиться ботом",
        switch_inline_query="Узнай, на какого тигра ты больше всего похож в этом боте! Присоединяйся и отправь свою фотографию, чтобы найти своего тигра-двойника! 📸🐯"), )
    markup.add(types.InlineKeyboardButton("Хочу оставить отзыв 📝", callback_data="feedback"))
    markup.add(types.InlineKeyboardButton("Пока хватит", callback_data="finish"))
    await bot.send_message(message.chat.id, "А что ты хочешь? 😁", reply_markup=markup)

    return handle_options.__name__


async def handle_options(callback):
    if not validate(callback, "callback"):
        await bot.send_message(callback.message.chat.id, "Нажми на кнопку с твоим вариантом ответа")
        return handle_options.__name__

    match callback.data:
        case "restart":
            await bot.send_message(callback.message.chat.id, "Жду твое фото!")
            return receive_photo.__name__
        case "feedback":
            markup = types.InlineKeyboardMarkup().add(
                types.InlineKeyboardButton("Я передумал", callback_data="cancel_feedback"))
            await bot.send_message(callback.message.chat.id, "Напиши свой отзыв в сообщении и отправь его мне 😊✍️",
                                   reply_markup=markup)
            return handle_feedback.__name__
        case "finish":
            return await skip_analysis(callback.message)
    await bot.send_message(callback.message.chat.id,
                           "Ой, ты нажал не на ту кнопку! Вернись к последнему сообщению и выбери свой вариант ответа.")

    return handle_options.__name__


async def handle_more_options(message):
    markup = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton("Хочу еще разок 🤩", callback_data="restart"),
        types.InlineKeyboardButton("Хочу поделиться ботом",
                                   switch_inline_query="Узнай, на какого тигра ты больше всего похож в этом боте! Присоединяйся и отправь свою фотографию, чтобы найти своего тигра-двойника! 📸🐯"),
        types.InlineKeyboardButton("Хочу оставить отзыв 📝", callback_data="feedback"),
        types.InlineKeyboardButton("Пока хватит", callback_data="finish")
    )
    await bot.send_message(message.chat.id, "Хочешь сделать что-нибудь еще? 🐯", reply_markup=markup)

    return handle_options.__name__


async def handle_feedback(message):
    if validate(message, "callback"):
        await bot.send_message(message.message.chat.id, "Очень жаль, ведь твоё мнение очень важно для меня🥺")
        return await handle_more_options(message.message)

    if not validate(message, "text"):
        await bot.send_message(message.chat.id, "Отправь отзыв текстовым сообщением!")
        return handle_feedback.__name__

    review = message.text
    user_id = message.from_user.id
    user_name = message.from_user.username

    review_text = f'Отзыв от @{user_name} (ID: {user_id}):\n{review}'

    try:
        await bot.send_message(ADMIN_USER_ID, review_text)
    except Exception as e:
        print(f"Ошибка при отправке сообщения админу: {e}")

    with open("feedback.txt", "a", encoding="UTF-8") as f:
        f.write(review_text + "\n" * 2)

    await bot.send_message(message.chat.id, "Спасибо🙏🏻 Я всё передам, твоё мнение правда важно для нас 🐯❤️",)
    return await handle_more_options(message)


async def mix_photo_in_queue(message, photo_path):
    future = asyncio.Future()
    task = {
        'func': mix_photo,
        'message': message,
        'args': (photo_path,),
        'future': future
    }

    await task_queue.put(task)

    position = task_queue.qsize()
    await bot.send_message(message.chat.id, f"Ваше фото добавлено в очередь. Позиция в очереди: {position}")

    result = await future
    return result


@bot.message_handler(commands=["reset"])
async def reset(message):
    db.update_step(message.from_user.id, start.__name__)


@bot.message_handler(commands=["test"])
async def test(message):
    me = await bot.get_me()
    markup = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton("test", switch_inline_query="Попробуй этого крутейшего бота!"))
    await bot.send_message(message.chat.id, "text", reply_markup=markup)


@bot.message_handler(content_types=["text", "photo", "document"])
@bot.callback_query_handler(func=lambda msg: True)
async def handle_messages(msg):
    step = db.get_user(msg.from_user.id)
    step = await globals()[step](msg)
    db.update_step(msg.from_user.id, step)


async def main():
    queue_task = asyncio.create_task(process_queue())
    await bot.infinity_polling(timeout=1000)


def clean_user_data():
    for path in Path("photos/user_data").iterdir():
        if path.is_dir():
            rmtree(path)
        else:
            path.unlink()


if __name__ == '__main__':
    clean_user_data()
    print("Bot starting")
    asyncio.run(main())
    print("Bot stopped")