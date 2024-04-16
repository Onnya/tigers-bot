import asyncio

import telebot
from telebot import types
from telebot.async_telebot import AsyncTeleBot

import database
import photo_service


TOKEN = "7029765070:AAHEAbjrQ6n_3daTGs4AIykv7TFS5dPZCjQ"

bot = AsyncTeleBot(token=TOKEN)
db = database.Database()


def validate(message: telebot.types.Message, expected):
    """
    Checks if the message is valid.
    :param message: message to be checked
    :param expected: "text", "photo", "document" or "callback"
    :return: bool, True if the message is valid, otherwise False
    """
    if type(message) is telebot.types.CallbackQuery:
        return expected == "callback"
    return expected == message.content_type


async def step1(message):
    if not validate(message, "text"):
        await bot.send_message(message.message.chat.id, "Отправь текстовое сообщение")
        return step1.__name__
    validate(message, "text")
    markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("Загрузить фото 🐅", callback_data="step_1"))
    await bot.send_message(message.chat.id, "Привет, я ТигроБот! 🐯 Я умный тигр и я могу определить, на кого из моих сородичей ты похож. Чтобы узнать ответ, нажми на кнопку и загрузи свое фото!", reply_markup=markup)
    return step2.__name__


async def step2(callback):
    if not validate(callback, "callback"):
        await bot.send_message(callback.message.chat.id, "Нажми на кнопку")
        return step2.__name__
    await bot.send_message(callback.message.chat.id, "Жду твое фото!")
    return step3.__name__


async def step3(message):
    if not validate(message, "photo"):
        try:
            await bot.send_message(message.chat.id, "Отправь фото")
            return step3.__name__
        except Exception as e:
            await bot.send_message(message.message.chat.id, "Отправь фото")
            return step3.__name__
    photo = message.photo
    await bot.send_message(message.chat.id, "Кажется, я знаю, кто ты 😏")

    file_id = photo[-1].file_id
    file_info = await bot.get_file(file_id)
    photo = await bot.download_file(file_info.file_path)

    with open(f"photos/{file_id}.png", "wb") as f:
        f.write(photo)

        db.add_photo(message.chat.id, f"photos/{file_id}.png")

    tiger_photo = photo_service.get_photo(photo)

    await bot.send_photo(message.chat.id, tiger_photo, caption="<description>")

    buttons = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("Да", callback_data="yes"))
    buttons.add(types.InlineKeyboardButton("А что это?", callback_data="question"))
    buttons.add(types.InlineKeyboardButton("Нет", callback_data="no"))
    await bot.send_message(message.chat.id, "Хочешь микс с Кандинским? 🧑🏻‍ 🪄 🐯", reply_markup=buttons)

    return step4.__name__


async def end(callback):
    if not validate(callback, "callback"):
        return end.__name__
    return await step8(callback.message)


async def step6(message):
    button = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("А что ты еще умеешь?", callback_data="step8"))
    await bot.send_message(message.chat.id, "Мои малыши-помощники тигрята удивлены! 🐯😮 Но не переживай, может быть в следующий раз тебе захочется создать что-то особенное с нами! 🐾🎨", reply_markup=button)
    return end.__name__


async def step7(message, photo):
    with open(photo, "rb") as f:
        photo = f.read()
    """ Делаем микс """
    button = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("А что ты еще умеешь?", callback_data="step8"))
    await bot.send_photo(message.chat.id, photo, caption="Вот, что у нас получилось✨😱", reply_markup=button)
    return end.__name__


async def step5(callback):
    if not validate(callback, "callback"):
        await bot.send_message(callback.chat.id, "Вернись к последнему сообщению и выбери нужную кнопку!")
        return step5.__name__
    answer = callback.data
    if answer == "mix":
        photo = db.get_photo(callback.from_user.id)
        step = await step7(callback.message, photo)
        return step
    if answer == "not_mix":
        step = await step6(callback.message)
        return step
    await bot.send_message(callback.message.chat.id, "Ой! Кажется, ты нажал не на ту кнопку. Вернись к последнему сообщению и выбери правильный вариант!")
    return step5.__name__


async def step4(callback):
    if not validate(callback, "callback"):
        await bot.send_message(callback.chat.id, "Нажми на кнопку с твоим вариантом ответа")
        return step4.__name__
    answer = callback.data
    match answer:
        case "yes":
            photo = db.get_photo(callback.from_user.id)
            ''' микс фотки '''
            step = await step7(callback.message, photo)
            return step
        case "question":
            buttons = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("Давай! 💪🎨", callback_data="mix"))
            buttons.add(types.InlineKeyboardButton("Я передумал", callback_data="not_mix"))
            await bot.send_message(callback.message.chat.id, "Кандинский - это такая умная штука - нейросеть, созданная разработчиками из Сбера. 🧠💡 Он может соединить твое фото с фото твоего тигрового двойника 🐯🔗 Интересно же, правда? 🤩 Готов попробовать? 😄", reply_markup=buttons)
            return step5.__name__
        case "no":
            step = await step6(callback.message)
            return step
    await bot.send_message(callback.message.chat.id, "Ой. Ты нажал не на ту кнопку( вернись к последнему сообщению и выбери свой вариант ответа!")
    return step4.__name__


async def step8(message):
    buttons = types.InlineKeyboardMarkup()
    buttons.add(types.InlineKeyboardButton("Хочу еще разок 🤩", callback_data="restart"))
    buttons.add(types.InlineKeyboardButton("Хочу поделиться ботом", switch_inline_query="Узнай, на какого тигра ты больше всего похож в этом боте! Присоединяйся и отправь свою фотографию, чтобы найти своего тигра-двойника! 📸🐯"))
    buttons.add(types.InlineKeyboardButton("Хочу поделиться результатом", callback_data="share_result"))
    buttons.add(types.InlineKeyboardButton("Хочу оставить отзыв 📝", callback_data="feedback"))
    buttons.add(types.InlineKeyboardButton("Пока хватит", callback_data="finish"))
    await bot.send_message(message.chat.id, "А что ты хочешь? 😁", reply_markup=buttons)
    return step9.__name__


async def another_step8(message):
    buttons = types.InlineKeyboardMarkup()
    buttons.add(types.InlineKeyboardButton("Хочу еще разок 🤩", callback_data="restart"))
    buttons.add(types.InlineKeyboardButton("Хочу поделиться ботом", switch_inline_query="Узнай, на какого тигра ты больше всего похож в этом боте! Присоединяйся и отправь свою фотографию, чтобы найти своего тигра-двойника! 📸🐯"))
    buttons.add(types.InlineKeyboardButton("Хочу поделиться результатом", callback_data="share_result"))
    buttons.add(types.InlineKeyboardButton("Хочу оставить отзыв 📝", callback_data="feedback"))
    buttons.add(types.InlineKeyboardButton("Пока хватит", callback_data="finish"))
    await bot.send_message(message.chat.id, "Хочешь сделать что нибудь еще 🐯?", reply_markup=buttons)
    return step9.__name__


async def step9(callback):
    if not validate(callback, "callback"):
        await bot.send_message(callback.message.chat.id, "Нажми на кнопку с твоим вариантом ответа")
        return step9.__name__
    answer = callback.data
    match answer:
        case "restart":
            await bot.send_message(callback.message.chat.id, "Жду твое фото!")
            return step3.__name__
        case "share_result":
            await bot.send_message(callback.message.chat.id, "url")
            await bot.send_message(callback.message.chat.id, "Ты можешь снова загрузить фото")
            return step3.__name__
        case "feedback":
            buttons = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("Я передумал", callback_data="cancel"))
            await bot.send_message(callback.message.chat.id, "Напиши свой отзыв в сообщении и отправь его мне 😊✍️", reply_markup=buttons)
            return feedback.__name__
        case "finish":
            buttons = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("Тебе спасибо! Ты классный ❤️", callback_data="absolutly_finish"))
            await bot.send_message(callback.message.chat.id, "Тогда спасибо, что заглянул поболтать со мной! 🐾  А то мне бывает скучно одному 🥺 Надеюсь, тебе было интересно со мной общаться! Буду рад видеть тебя здесь снова 🐯🧡", reply_markup=buttons)
            return finish.__name__
    await bot.send_message(callback.message.chat.id, "Ой. Ты нажал не на ту кнопку( вернись к последнему сообщению и выбери свой вариант ответа!")
    return step9.__name__


async def finish(callback):
    if not validate(callback, "callback"):
        await bot.send_message(callback.chat.id, "Нажми на кнопку с твоим вариантом ответа")
        return finish.__name__
    answer = callback.data
    if answer == "absolutly_finish":
        await bot.send_message(callback.message.chat.id, "Приходи в гости! Я буду тебя ждать 🤗🌿")
        return step1.__name__
    await bot.send_message(callback.message.chat.id, "Ой. Ты нажал не на ту кнопку( вернись к последнему сообщению и выбери свой вариант ответа!")
    return finish.__name__


async def feedback(message):
    if validate(message, "callback"):
        await bot.send_message(message.message.chat.id, "Очень жаль, ведь твоё мнение очень важно для меня🥺")
        return await step8(message.message)
    if not validate(message, "text"):
        await bot.send_message(message.chat.id, "Отправь отзыв текстовым сообщением!")
        return feedback.__name__
    message: types.Message = message
    print("\n"*5, "-"*100, "У нас есть отзыв!\n", message.text, "\n", "-"*100, "\n"*5)
    await bot.send_message(message.chat.id, "Спасибо🙏🏻 Я всё передам, твоё мнение правда важно для нас 🐯❤️")
    return await step8(message)


@bot.message_handler(commands=["reset"])
async def reset(message):
    db.update_step(message.from_user.id, step1.__name__)


@bot.message_handler(commands=["test"])
async def test(message):
    me = await bot.get_me()
    print(me.id)
    buttons = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton("test", switch_inline_query="Попробуй этого крутейшего бота!"))
    await bot.send_message(message.chat.id, "text", reply_markup=buttons)


@bot.message_handler(content_types=["text", "photo", "document"])
@bot.callback_query_handler(func=lambda message: True)
async def send_welcome(message):
    step = db.get_user(message.from_user.id)
    step = await globals()[step](message)
    db.update_step(message.from_user.id, step)


async def main():
    await bot.infinity_polling(timeout=1000)


if __name__ == '__main__':
    print("Bot starting")
    asyncio.run(globals()[main.__name__]())
    print("Bot stopped")
