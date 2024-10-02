from aiogram import Router, F
from aiogram.types import CallbackQuery, LabeledPrice, Message, PreCheckoutQuery
from aiocryptopay import AioCryptoPay, Networks
import aiorocket

from database.premium_db import add_premium_user
from kb import premium_kb, pay_premium_kb, pay_cb, payment_keyboard
from loader import bot, dp

premium_router = Router()
prem_text = (f"💎 Birdy Premium\n\n"
             f"👑 Преимущества:\n"
             f"⌛️ Возможность получать карточки каждые 4 часа вместо 5.\n"
             f"🃏 Повышенная вероятность выпадения легендарных и мифических карт.\n"
             f"🔄 Более быстрая обработка твоих сообщений.\n"
             f"🍵 Чай выдается от 500 до 2000 вместо 200 до 2000.\n"
             f"🗓️ Срок действия 30 дней.\n\n"
             f"💳 Будете покупать?")
prem_textt = (f"💎 Birdy Premium\n\n"
              f"👑 Преимущества:\n"
              f"⌛️ Возможность получать карточки каждые 4 часа вместо 5.\n"
              f"🃏 Повышенная вероятность выпадения легендарных и мифических карт.\n"
              f"🔄 Более быстрая обработка твоих сообщений.\n"
              f"🍵 Чай выдается от 500 до 2000 вместо 200 до 2000.\n"
              f"🗓️ Срок действия 30 дней.\n\n"
              f"💳  Выберите способ оплаты:")
crypto = AioCryptoPay(token='275932:AAJGiROUIeR5syysCkBUgHT3N8IBnPcriKR', network=Networks.MAIN_NET)
api = aiorocket.Rocket('596b0776e2bb0331fbf0de951')
invoices = {}


@premium_router.callback_query(F.data.startswith("premium:"))
async def buy_premium(callback: CallbackQuery):
    user_id = callback.data.split(":")[1]
    if user_id != str(callback.from_user.id):
        await callback.answer("Вы арестованы, руки вверх!")
        return
    if callback.message.chat.type in ["supergroup", "group"]:
        await callback.message.reply(prem_text, reply_markup=await premium_kb(user_id))
    elif callback.message.chat.type == "private":
        await callback.message.reply(prem_textt, reply_markup=await pay_premium_kb())


@premium_router.callback_query(F.data.startswith("buy_premium:"))
async def pay_premium(callback: CallbackQuery):
    user_id = callback.data.split(":")[1]
    if user_id != str(callback.from_user.id):
        await callback.answer("Вы арестованы, руки вверх!")
        return
    try:
        await callback.bot.send_message(chat_id=callback.from_user.id, text=prem_textt,
                                        reply_markup=await pay_premium_kb())
        if callback.message.chat.type in ["supergroup", "group"]:
            await callback.message.reply("Способы об оплате отправлены в личные сообщения.")
    except Exception:
        await callback.answer("Напишите боту в личные сообщения что нибудь чтобы отправить вам реквизиты.",
                              show_alert=True)


@premium_router.callback_query(F.data.startswith("buy_"))
async def pay_invoice(callback: CallbackQuery):
    method = callback.data.split("_")[1]
    user_id = callback.from_user.id

    if method == "cb":
        invoice = await crypto.create_invoice(asset='USDT', amount=0.5)
        invoice_id = invoice.invoice_id
        await callback.message.answer("💳 Оплатите чек нажав на кнопку ниже, после оплаты нажмите на кнопку Я оплатил.",
                                      reply_markup=await pay_cb(invoice.bot_invoice_url, invoice_id, "cb"))

    elif method == "xr":
        invoice = await api.create_invoice(
            amount=0.50,
            currency='USDT'
        )
        invoice_link = invoice.link
        invoice_id = invoice.id
        await callback.message.answer(
            "💳 Оплатите чек нажав на кнопку ниже, после оплаты нажмите на кнопку Я оплатил.",
            reply_markup=await pay_cb(invoice_link, invoice_id, "xr")
        )
    elif method == "xtr":
        prices = [LabeledPrice(label="XTR", amount=30)]
        await callback.message.answer_invoice(
            title="🌟 Birdy Premium",
            description="💎 Покупка Birdy Premium",
            prices=prices,
            provider_token="",
            payload="birdy_premium",
            currency="XTR",
            reply_markup=await payment_keyboard(),
        )


@premium_router.callback_query(F.data.startswith("check_pay_"))
async def check_pay(callback: CallbackQuery):
    method = callback.data.split("_")[2]
    if method == "cb":
        invoice_id = callback.data.split("_")[3]
        old_invoice = await crypto.get_invoices(invoice_ids=int(invoice_id))
        if old_invoice.status == "paid":
            await add_premium_user(callback.from_user.id, 31)
            await callback.bot.edit_message_text(
                chat_id=callback.message.chat.id,
                message_id=callback.message.message_id,
                text="✅ Оплата прошла! Наслаждайтесь эксклюзивными преимуществами."
            )
        else:
            await callback.answer("❌ Оплата не прошла! Попрбуйте еще раз через некоторое время.", show_alert=True)
    elif method == "xr":
        invoice_id = callback.data.split("_")[3]
        invoice_status = await api.get_invoice(int(invoice_id))
        if invoice_status.paid:
            await add_premium_user(callback.from_user.id, 31)
            await callback.bot.edit_message_text(
                chat_id=callback.message.chat.id,
                message_id=callback.message.message_id,
                text="✅ Оплата прошла! Наслаждайтесь эксклюзивными преимуществами."
            )
        else:
            await callback.answer("❌ Оплата не прошла! Попрбуйте еще раз через некоторое время.", show_alert=True)


async def handle_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


async def handle_successful_payment(message: Message):
    await add_premium_user(message.from_user.id, 31)
    await message.answer(
        '✅ Оплата прошла! Наслаждайтесь эксклюзивными преимуществами.')


dp.pre_checkout_query.register(handle_pre_checkout_query)
dp.message.register(handle_successful_payment, F.successful_payment)
