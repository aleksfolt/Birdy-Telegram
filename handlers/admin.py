from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.mailing import get_all_users_and_chats, remove_chat_from_db, remove_user_from_db
from kb import admin_keyboard, mailing_keyboard

adm_router = Router()

class MailingState(StatesGroup):
    waiting_for_text = State()
    waiting_for_button = State()

@adm_router.message(Command("admin"))
async def admin_menu(message: Message):
    if message.chat.type in ["supergroup", "group"]:
        return
    if message.from_user.id != 6184515646:
        return
    await message.reply("Привет админ!", reply_markup=await admin_keyboard())

@adm_router.callback_query(F.data.startswith("adm_"))
async def admin_handler(callback: CallbackQuery):
    data = callback.data.split("_")
    action = data[1]
    if action == "mailing":
        await callback.bot.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            text="Выберите настройки для рассылки:",
            reply_markup=await mailing_keyboard()
        )
    elif action == "addprem":
        await callback.bot.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            text="Выберите настройки для рассылки:",
            reply_markup=await mailing_keyboard()
        )


@adm_router.callback_query(F.data.startswith("mailing_"))
async def mailing(callback: CallbackQuery, state: FSMContext):
    data = callback.data.split(":")
    if len(data) < 3:
        await callback.answer("Ошибка в данных. Пожалуйста, попробуйте снова.", show_alert=True)
        return

    action = data[0].split("_")[1]
    selected_groups = data[1] == "True"
    selected_pm = data[2] == "True"

    if action == "groups":
        selected_groups = not selected_groups
    elif action == "pm":
        selected_pm = not selected_pm
    elif action == "next":
        if selected_groups or selected_pm:
            await state.update_data(selected_groups=selected_groups, selected_pm=selected_pm)
            await state.set_state(MailingState.waiting_for_text)
            await callback.bot.edit_message_text(
                chat_id=callback.message.chat.id,
                message_id=callback.message.message_id,
                text="Пожалуйста, отправьте текст для рассылки:"
            )
        else:
            await callback.answer("Нужно выбрать хотя бы одну опцию для рассылки!", show_alert=True)
        return

    await callback.bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        text="Выберите настройки для рассылки:",
        reply_markup=await mailing_keyboard(selected_groups, selected_pm)
    )


@adm_router.message(MailingState.waiting_for_text)
async def process_mailing_text(message: Message, state: FSMContext):
    mailing_text = message.text
    await state.update_data(mailing_text=mailing_text)
    await state.set_state(MailingState.waiting_for_button)
    await message.answer("Теперь отправьте текст и ссылку для кнопки в формате <текст> - <ссылка>:")


@adm_router.message(MailingState.waiting_for_button)
async def process_mailing_button(message: Message, state: FSMContext):
    button_data = message.text
    if " - " not in button_data:
        await message.answer("Неправильный формат. Пожалуйста, отправьте в формате <текст> - <ссылка>.")
        return

    button_text, button_link = button_data.split(" - ", 1)

    data = await state.get_data()
    mailing_text = data.get("mailing_text")
    selected_groups = data.get("selected_groups", False)
    selected_pm = data.get("selected_pm", False)

    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Отправить", callback_data="send_mailing"))

    await message.answer(
        f"Текст для рассылки: {mailing_text}\n"
        f"Группы: {selected_groups}\nЛС: {selected_pm}\n"
        f"Кнопка: Текст - {button_text}, Ссылка - {button_link}",
        reply_markup=builder.as_markup()
    )

    await state.update_data(button_text=button_text, button_link=button_link)
    await state.set_state(MailingState.waiting_for_button)

async def mailing_send(bot: Bot, message_text: str, button_text: str = None, button_url: str = None, send_to_users=False, send_to_chats=False):
    users, chats = await get_all_users_and_chats()

    if button_text and button_url:
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=button_text, url=button_url)]
        ])
    else:
        keyboard = None

    if send_to_users:
        for user_id in users:
            try:
                await bot.send_message(chat_id=user_id, text=message_text, reply_markup=keyboard)
            except Exception:
                await remove_user_from_db(user_id)
                continue

    if send_to_chats:
        for chat_id in chats:
            try:
                await bot.send_message(chat_id=chat_id, text=message_text, reply_markup=keyboard)
            except Exception:
                await remove_chat_from_db(chat_id)
                continue




@adm_router.callback_query(F.data == "send_mailing")
async def send_mailing(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    mailing_text = data.get("mailing_text")
    button_text = data.get("button_text")
    button_link = data.get("button_link")
    selected_groups = data.get("selected_groups", False)
    selected_pm = data.get("selected_pm", False)

    if not selected_groups and not selected_pm:
        await callback.answer("Нужно выбрать хотя бы один канал для рассылки!", show_alert=True)
        return

    await mailing_send(
        bot=callback.bot,
        message_text=mailing_text,
        button_text=button_text,
        button_url=button_link,
        send_to_users=selected_pm,
        send_to_chats=selected_groups
    )

    await state.clear()
    await callback.answer("Рассылка успешно отправлена!")
