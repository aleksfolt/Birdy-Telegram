from gc import callbacks

from aiogram import types
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


async def profile_kb(user_id):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🎴 Мои карточки", callback_data=f"cards:{user_id}"))
    builder.add(InlineKeyboardButton(text="🀄️ Купить лимитку", callback_data=f"cool_card:{user_id}"))
    builder.add(InlineKeyboardButton(text="💎 Премиум", callback_data=f"premium:{user_id}"))
    builder.add(InlineKeyboardButton(text="🌀 Рефералка", callback_data=f"ref:{user_id}"))
    builder.adjust(2, 2)
    return builder.as_markup()


async def rarity_kb():
    keyboard = InlineKeyboardBuilder()
    rarities = ["⚡️ Редкая", "🐲 Сверхредкая", "⚔️ Мифическая", "🩸 Легендарная", "👁‍🗨 Крутка"]
    rarities_callback = ["Редкая", "Сверхредкая", "Мифическая", "Легендарная", "Крутка"]

    for rarity, rarity_callback in zip(rarities, rarities_callback):
        button = InlineKeyboardButton(text=rarity, callback_data=f"select_rarity:{rarity_callback}")
        keyboard.add(button)

    keyboard.adjust(1)

    return keyboard.as_markup()


async def start_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="🃏 Кнок"))
    builder.add(types.KeyboardButton(text="☕️ Чай"))
    builder.add(types.KeyboardButton(text="👤 Бпрофиль"))
    builder.add(types.KeyboardButton(text="🏆 Топ карточек"))
    builder.add(types.KeyboardButton(text="⭐️ Топ чая"))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


async def cards_kb(user_id: str, current_index: int, total_cards: int, rarity: str, current_bird_name):
    prev_button = InlineKeyboardButton(text="⬅️ Назад", callback_data=f"ccards:{rarity}:{current_index - 1}")
    next_button = InlineKeyboardButton(text="Вперед ➡️", callback_data=f"ccards:{rarity}:{current_index + 1}")
    fork_button = InlineKeyboardButton(text="⚙️ Inline", switch_inline_query=f"{current_bird_name}")

    keyboard = InlineKeyboardBuilder()

    if current_index > 0:
        keyboard.add(prev_button)
    if current_index < total_cards - 1:
        keyboard.add(next_button)
    keyboard.add(fork_button)
    keyboard.adjust(2, 1)

    return keyboard.as_markup()


async def cool_card_kb(user_id):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🃏 Купить", callback_data=f'buy_cool_card:{user_id}'))
    return builder.as_markup()


async def cards_top_kb(user_id):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🃏 Топ по карточкам", callback_data=f"top_cards:{user_id}"))
    builder.add(InlineKeyboardButton(text="💯 Топ по очкам", callback_data=f"top_points:{user_id}"))
    builder.add(InlineKeyboardButton(text="🎴 Топ за все время", callback_data=f"top_all:{user_id}"))
    builder.adjust(2, 1)
    return builder.as_markup()


async def back_cards(user_id):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🔙 Назад", callback_data=f"top_back:{user_id}"))
    return builder.as_markup()


async def premium_kb(user_id):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="💎 Купить", callback_data=f"buy_premium:{user_id}"))
    return builder.as_markup()


async def pay_premium_kb():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="💰 Crypto Bot", callback_data=f"buy_cb"))
    builder.add(InlineKeyboardButton(text="🚀 xRocket", callback_data=f"buy_xr"))
    builder.add(InlineKeyboardButton(text="🌟 Telegram Stars", callback_data=f"buy_xtr"))
    builder.adjust(2, 1)
    return builder.as_markup()


async def pay_cb(url, invoice_id, method):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="💵 Оплатить", url=url))
    builder.add(InlineKeyboardButton(text="✅ Я оплатил", callback_data=f"check_pay_{method}_{invoice_id}"))
    return builder.as_markup()


async def payment_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text=f"Оплатить 30 ⭐️", pay=True)

    return builder.as_markup()


async def admin_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Mailing", callback_data="adm_mailing"))
    builder.add(InlineKeyboardButton(text="Get user", callback_data="adm_getuser"))
    builder.add(InlineKeyboardButton(text="Add points", callback_data="adm_addpoints"))
    builder.add(InlineKeyboardButton(text="Pick up points", callback_data="adm_pickuppoints"))
    builder.add(InlineKeyboardButton(text="Reset knock cooldown", callback_data="adm_resetknock"))
    builder.add(InlineKeyboardButton(text="Add tea", callback_data="adm_addtea"))
    builder.add(InlineKeyboardButton(text="Pick up tea", callback_data="adm_pickuptea"))
    builder.add(InlineKeyboardButton(text="Reset tea cooldown", callback_data="adm_resettea"))
    builder.add(InlineKeyboardButton(text="Add premium", callback_data="adm_addprem"))
    builder.adjust(2, 2)
    return builder.as_markup()


async def mailing_keyboard(selected_groups=False, selected_pm=False):
    builder = InlineKeyboardBuilder()

    group_checked = "✅ Группы" if selected_groups else "Группы"
    pm_checked = "✅ Лс" if selected_pm else "Лс"

    builder.add(
        InlineKeyboardButton(text=group_checked, callback_data=f"mailing_groups:{selected_groups}:{selected_pm}"))
    builder.add(InlineKeyboardButton(text=pm_checked, callback_data=f"mailing_pm:{selected_groups}:{selected_pm}"))
    builder.add(InlineKeyboardButton(text="Далее", callback_data=f"mailing_next:{selected_groups}:{selected_pm}"))
    builder.adjust(2)
    return builder.as_markup()
