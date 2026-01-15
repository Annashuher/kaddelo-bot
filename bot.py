# -*- coding: utf-8 -*-
"""Telegram Bot for Cadastral Engineer with Web Server"""

import asyncio
import logging
import os
import sys
from threading import Thread

# ==================== ВЕБ-СЕРВЕР ДЛЯ UPTIMEROBOT ====================
from flask import Flask

app = Flask('')

@app.route('/')
def home():
    return "🤖 Kaddelo Bot is running! ✅"

@app.route('/health')
def health():
    return "OK", 200

@app.route('/status')
def status():
    return "Bot is alive and responding to Telegram", 200

def run_web():
    """Запуск веб-сервера в отдельном потоке"""
    app.run(host='0.0.0.0', port=8080)

# ==================== ТЕЛЕГРАМ БОТ ====================
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ParseMode
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

print("=" * 50)
print("SETUP COMPLETE")
print("=" * 50)
print("aiogram installed")
print("python-dotenv installed")
print("flask installed for web server")
print("All libraries ready")
print("=" * 50)

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not found! Please set BOT_TOKEN environment variable")
ADMIN_ID = 1460213585

print("=" * 50)
print("CHECKING SETTINGS")
print("=" * 50)

try:
    bot = Bot(token=BOT_TOKEN)
    print("Bot created successfully!")
except Exception as e:
    print(f"Error creating bot: {e}")
    sys.exit()

dp = Dispatcher()
subscribers = []
client_requests = []

print(f"Subscribers in memory: {len(subscribers)}")
print(f"Requests in memory: {len(client_requests)}")
print(f"Admin ID: {ADMIN_ID}")
print("=" * 50)

@dp.message(Command("start"))
async def start_command(message: Message):
    user_id = message.from_user.id
    user_name = message.from_user.full_name

    if user_id not in subscribers:
        subscribers.append(user_id)
        print(f"New subscriber: {user_name} (ID: {user_id})")

    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="ПОРЯДОК ПОЛУЧЕНИЯ УСЛУГИ", callback_data="techplan_process")],
            [types.InlineKeyboardButton(text="ОСТАВИТЬ ЗАЯВКУ НА КОНСУЛЬТАЦИЮ", callback_data="leave_request")],
        ]
    )

    welcome_text = f"""
<b>Привет, {user_name}!</b>

Вы подписались на рассылку от кадастрового инженера Глайборода И.А.!
Теперь вы будете получать:
- Актуальную информацию по кадастровым услугам
- Специальные предложения и скидки

Всего подписчиков: {len(subscribers)}

<b>Обратите внимание:</b>
"""

    await message.answer(welcome_text, parse_mode=ParseMode.HTML, reply_markup=keyboard)

    await message.answer(
        "<b>Дополнительные команды:</b>\n"
        "/help - справка по боту\n"
        "/unsubscribe - отписаться от рассылки",
        parse_mode=ParseMode.HTML
    )

@dp.message(Command("help"))
async def help_command(message: Message):
    help_text = """
<b>Справка по Kaddelo Bot</b>

Это бот для получения информации от кадастрового инженера Глайборода И.А.

<b>Основные кнопки:</b>
- АЛГОРИТМ ПОЛУЧЕНИЯ УСЛУГИ - описание процесса работ
- ОСТАВИТЬ ЗАЯВКУ - консультация по кадастровым услугам

<b>Команды:</b>
/start - Подписаться на рассылку
/help - Эта справка
/unsubscribe - Отписаться от рассылки

<b>Для связи:</b>
Отправьте заявку через кнопку или напишите напрямую.
    """

    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="АЛГОРИТМ ПОЛУЧЕНИЯ УСЛУГИ", callback_data="techplan_process")],
            [types.InlineKeyboardButton(text="ОСТАВИТЬ ЗАЯВКУ", callback_data="leave_request")],
        ]
    )

    await message.answer(help_text, parse_mode=ParseMode.HTML, reply_markup=keyboard)

@dp.message(Command("unsubscribe"))
async def unsubscribe_command(message: Message):
    user_id = message.from_user.id

    if user_id in subscribers:
        subscribers.remove(user_id)
        await message.answer("Вы отписались от рассылки.")
        print(f"Unsubscribed: ID {user_id}")
    else:
        await message.answer("Вы не были подписаны.")

print("User commands added!")

@dp.message(Command("admin"))
async def admin_command(message: Message):
    """Admin panel - /admin command"""
    if message.from_user.id != ADMIN_ID:
        await message.answer("Access denied")
        return

    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="Статистика")],
            [types.KeyboardButton(text="Сделать рассылку")],
            [types.KeyboardButton(text="Пример акции")],
            [types.KeyboardButton(text="Закрыть панель")],
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )

    admin_text = f"""
<b>Панель администратора</b>

Бот: Kaddelo Bot
Админ: {message.from_user.full_name}
Подписчиков: {len(subscribers)}
Заявок: {len(client_requests)}

<b>Используйте кнопки ниже:</b>
    """
    await message.answer(admin_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)

@dp.message(lambda message: message.text == "Статистика" and message.from_user.id == ADMIN_ID)
async def stats_button(message: Message):
    """Statistics button"""
    stats_text = f"""
<b>Статистика Kaddelo Bot</b>

Всего подписчиков: <b>{len(subscribers)}</b>
Активных заявок: <b>{len(client_requests)}</b>
Админ ID: <code>{ADMIN_ID}</code>

<b>Последние 5 подписчиков:</b>
"""
    if subscribers:
        last_subscribers = subscribers[-5:] if len(subscribers) >= 5 else subscribers
        for i, user_id in enumerate(last_subscribers, 1):
            stats_text += f"{i}. <code>{user_id}</code>\n"
    else:
        stats_text += "Пока нет подписчиков\n"

    if client_requests:
        stats_text += f"\n<b>Последние 3 заявки:</b>\n"
        for i, req in enumerate(client_requests[-3:], 1):
            stats_text += f"{i}. ID: <code>{req['user_id']}</code> ({req['timestamp'].strftime('%d.%m %H:%M')})\n"
    await message.answer(stats_text, parse_mode=ParseMode.HTML)

@dp.message(lambda message: message.text == "Сделать рассылку" and message.from_user.id == ADMIN_ID)
async def mailing_button(message: Message):
    """Mailing button"""
    if len(subscribers) == 0:
        await message.answer("Нет подписчиков для рассылки!")
        return

    mailing_text = f"""
<b>Готов к рассылке!</b>

Получателей: {len(subscribers)}

<b>Отправьте сообщение, которое нужно разослать:</b>
- Можно отправить текст
- Можно отправить фото с подписью
- Можно отправить видео с подписью

Сообщение будет отправлено всем {len(subscribers)} подписчикам.
"""
    await message.answer(mailing_text, parse_mode=ParseMode.HTML, reply_markup=types.ReplyKeyboardRemove())

@dp.message(lambda message: message.text == "Пример акции" and message.from_user.id == ADMIN_ID)
async def promo_example_button(message: Message):
    """Promo example with inline buttons"""
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="АЛГОРИТМ ПОЛУЧЕНИЯ УСЛУГИ", callback_data="techplan_process")],
            [types.InlineKeyboardButton(text="ОСТАВИТЬ ЗАЯВКУ", callback_data="leave_request")],
        ]
    )

    promo_text = """
<b>АКЦИЯ ОТ KADDELO!</b>

<b>СКИДКА 10%</b> на технический план нежилого здания:
- Гараж
- Летняя кухня
- Хозблок
Только до 20 января!

Бесплатная консультация
Отслеживаем результат работ
Срочный заказ

Оставляйте заявку прямо в боте!
"""
    await message.answer("<b>Пример рекламного сообщения:</b>", parse_mode=ParseMode.HTML)
    await message.answer(promo_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    await message.answer("<i>Скопируйте этот текст для рассылки или создайте свой</i>", parse_mode=ParseMode.HTML)

@dp.callback_query(lambda c: c.data == "techplan_process")
async def techplan_process_handler(callback_query: types.CallbackQuery):
    """Handler for techplan process button"""
    process_text = """
<b>ПОРЯДОК ПОЛУЧЕНИЯ УСЛУГИ:</b>

1. <b>Изучение документов</b> и заключение договора
2. <b>Выезд на объект</b> для обмеров
3. <b>Подготовка документов (Технический план здания)</b>
4. <b>Передача заказчику технического плана на CD диске</b>


<b>Срок исполнения:</b> 2-3 рабочих дня
"""
    action_keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[[types.InlineKeyboardButton(text="ОСТАВИТЬ ЗАЯВКУ", callback_data="leave_request")]]
    )
    await callback_query.message.answer(process_text, parse_mode=ParseMode.HTML, reply_markup=action_keyboard)
    await callback_query.answer()

@dp.callback_query(lambda c: c.data == "leave_request")
async def leave_request_handler(callback_query: types.CallbackQuery):
    """Request message from user"""
    request_text = """
<b>ОТПРАВЬТЕ ВАШЕ СООБЩЕНИЕ</b>

Напишите сообщение для кадастрового инженера.
"""
    await callback_query.message.answer(request_text, parse_mode=ParseMode.HTML)
    await callback_query.answer("Напишите ваше сообщение в чат")

@dp.message(lambda message: message.text and not message.text.startswith('/') and message.from_user.id != ADMIN_ID)
async def handle_user_message(message: Message):
    """Handle regular messages from users as requests"""
    user_id = message.from_user.id
    user_name = message.from_user.full_name or "Без имени"
    username = message.from_user.username or "Нет username"

    client_requests.append({
        'user_id': user_id,
        'user_name': user_name,
        'username': username,
        'timestamp': datetime.now(),
        'status': 'новая',
        'message': message.text
    })

    await message.answer(
        f"<b>СООБЩЕНИЕ ОТПРАВЛЕНО!</b>\n\n"
        f"Кадастровый инженер получил сообщение и свяжется с Вами в течение рабочего дня.",
        parse_mode=ParseMode.HTML
    )

    request_message = f"""
<b>НОВАЯ ЗАЯВКА ОТ КЛИЕНТА!</b>

<b>Клиент:</b> {user_name}
<b>Username:</b> @{username}
<b>ID:</b> <code>{user_id}</code>
<b>Время:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}

<b>Сообщение:</b>
{message.text}
"""

    await bot.send_message(
        ADMIN_ID,
        request_message,
        parse_mode=ParseMode.HTML,
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[[
                types.InlineKeyboardButton(text="Написать клиенту", callback_data=f"write_{user_id}"),
                types.InlineKeyboardButton(text="Взять в работу", callback_data=f"take_{user_id}"),
            ]]
        )
    )

@dp.callback_query(lambda c: c.data.startswith("write_"))
async def write_to_client_handler(callback_query: types.CallbackQuery):
    """Write to client button - send message to client"""
    if callback_query.from_user.id != ADMIN_ID:
        await callback_query.answer("Доступ запрещен", show_alert=True)
        return

    user_id = callback_query.data.replace("write_", "")

    try:
        await bot.send_message(
            chat_id=int(user_id),
            text="<b>Сообщение от кадастрового инженера</b>\n\n"
                 "Здравствуйте! Получил Вашу заявку, рассмотрю в течение рабочего дня. Пока Вы можете оставить свои контакты для связи и более подробной консультации по заказу",
            parse_mode=ParseMode.HTML
        )

        await callback_query.message.answer(
            f"<b>Сообщение отправлено клиенту!</b>\n\n"
            f"ID клиента: <code>{user_id}</code>\n"
            f"Клиент получил ваше сообщение.",
            parse_mode=ParseMode.HTML
        )

        await callback_query.answer("Сообщение отправлено клиенту!")

    except Exception as e:
        await callback_query.message.answer(
            f"<b>Не удалось отправить сообщение</b>\n\n"
            f"Ошибка: {str(e)}\n\n"
            f"ID клиента: <code>{user_id}</code>",
            parse_mode=ParseMode.HTML
        )
        await callback_query.answer("Ошибка отправки", show_alert=True)

@dp.callback_query(lambda c: c.data.startswith("take_"))
async def take_request_handler(callback_query: types.CallbackQuery):
    """Take request button in notification"""
    if callback_query.from_user.id != ADMIN_ID:
        await callback_query.answer("Доступ запрещен", show_alert=True)
        return
    user_id = callback_query.data.replace("take_", "")
    for request in client_requests:
        if str(request['user_id']) == user_id:
            request['status'] = 'в работе'
            request['taken_at'] = datetime.now()
            break
    await callback_query.message.edit_text(
        callback_query.message.text + f"\n\n<b>Заявка взята в работу</b>\nВремя: {datetime.now().strftime('%H:%M')}",
        parse_mode=ParseMode.HTML
    )
    await callback_query.answer("Заявка взята в работу!")

@dp.message(lambda message: message.text == "Закрыть панель" and message.from_user.id == ADMIN_ID)
async def close_panel_button(message: Message):
    """Close panel"""
    await message.answer("Панель закрыта. Напишите /admin чтобы открыть снова.", reply_markup=types.ReplyKeyboardRemove())

print("Admin panel added!")

@dp.message(lambda message: message.from_user.id == ADMIN_ID)
async def handle_admin_mailing(message: Message):
    if message.text in ["Статистика", "Сделать рассылку", "Пример акции", "Закрыть панель"]:
        return

    if len(subscribers) == 0:
        await message.answer("Нет подписчиков для рассылки!")
        return

    await message.answer(f"Начинаю рассылку на {len(subscribers)} пользователей...")

    success_count = 0
    failed_count = 0

    for user_id in subscribers:
        try:
            if message.photo:
                await bot.send_photo(
                    chat_id=user_id,
                    photo=message.photo[-1].file_id,
                    caption=message.caption or "",
                    parse_mode=ParseMode.HTML
                )

            elif message.video:
                await bot.send_video(
                    chat_id=user_id,
                    video=message.video.file_id,
                    caption=message.caption or "",
                    parse_mode=ParseMode.HTML
                )

            else:
                await bot.send_message(
                    chat_id=user_id,
                    text=message.text or message.caption or "",
                    parse_mode=ParseMode.HTML
                )

            success_count += 1

            await asyncio.sleep(0.05)

        except Exception as e:
            failed_count += 1
            print(f"Error sending to user {user_id}: {e}")

    report_text = f"""
<b>Рассылка завершена!</b>

<b>Отчет:</b>
- Успешно отправлено: <b>{success_count}</b>
- Не удалось отправить: <b>{failed_count}</b>
- Всего получателей: <b>{len(subscribers)}</b>

<i>Для новой рассылки снова нажмите "Сделать рассылку"</i>
"""

    await message.answer(report_text, parse_mode=ParseMode.HTML)

    print("=" * 50)
    print("MAILING REPORT")
    print("=" * 50)
    print(f"Success: {success_count}")
    print(f"Failed: {failed_count}")
    print(f"Total: {len(subscribers)}")
    print("=" * 50)

print("Mailing system ready!")

async def main():
    # Запускаем веб-сервер в отдельном потоке
    web_thread = Thread(target=run_web, daemon=True)
    web_thread.start()
    print("🌐 Веб-сервер запущен на порту 8080")
    print("📡 URL для UptimeRobot: https://ваш-пропкт.ваш-логин.repl.co")
    print("📡 Или: https://ваш-проект.ваш-логин.repl.co/health")
    
    print("=" * 60)
    print("STARTING CADASTRAL ENGINEER BOT")
    print("=" * 60)

    try:
        bot_info = await bot.get_me()
        print(f"Bot connected: @{bot_info.username}")
        print(f"Bot name: {bot_info.first_name}")
        print(f"Bot ID: {bot_info.id}")
    except Exception as e:
        print(f"CONNECTION ERROR: {e}")
        print("Check the bot token")
        return

    print("\n" + "=" * 60)
    print("INSTRUCTIONS:")
    print("=" * 60)
    print("1. Open Telegram")
    print("2. Find and message your bot")
    print("3. Send /start command to subscribe")
    print("\n4. Open the bot from admin account")
    print("5. Send /admin command")
    print("6. Use buttons to manage:")
    print("   - Статистика - view subscribers and requests")
    print("   - Сделать рассылку - send message to all")
    print("   - Пример акции - view template with buttons")
    print("   - Закрыть панель - hide buttons")
    print("\n" + "=" * 60)
    print("Bot is running...")
    print("=" * 60 + "\n")

    try:
        await dp.start_polling(bot)
    except Exception as e:
        print(f"Bot error: {e}")
    finally:
        await bot.session.close()
        print("Bot stopped")

print("Press Run to start the bot...")

if __name__ == "__main__":
    asyncio.run(main())
