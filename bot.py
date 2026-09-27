import asyncio
import os
from datetime import datetime, timedelta, timezone
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import (
    Message,
    LabeledPrice,
    PreCheckoutQuery,
)

TOKEN = os.getenv("8874536741:AAGZPETk6ZyZ-eyUJyicPob9pA06zK_gt5Q")

PRODUCTS = {
    "trial":    ("на 1 неделю (пробный период)", 30),
    "month_1":  ("на 1 месяц",   90),
    "month_3":  ("на 3 месяца",  180),
    "month_6":  ("на 6 месяцев", 270),
    "month_12": ("на 12 месяцев",460),
    "forever":  ("навсегда",     750),
}

MONTHS_MAP = {
    "month_1": 1,
    "month_3": 3,
    "month_6": 6,
    "month_12": 12,
}

MSK = timezone(timedelta(hours=3))

dp = Dispatcher()


def add_months(source_date: datetime, months: int) -> datetime:
    month = source_date.month - 1 + months
    year = source_date.year + month // 12
    month = month % 12 + 1
    if month == 2:
        leap = (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
        max_day = 29 if leap else 28
    elif month in (4, 6, 9, 11):
        max_day = 30
    else:
        max_day = 31
    day = min(source_date.day, max_day)
    return source_date.replace(year=year, month=month, day=day)


def generate_sub_link(cmd: str) -> str:
    if cmd == "forever":
        end_date = datetime(2033, 3, 3, 0, 0, 0, tzinfo=MSK)
    elif cmd == "trial":
        end_date = datetime.now(MSK) + timedelta(days=7)
    else:
        months = MONTHS_MAP[cmd]
        now_msk = datetime.now(MSK)
        end_date = add_months(now_msk, months)
    timestamp = int(end_date.timestamp())
    return f"https://sub.combovpn-support.workers.dev/{timestamp}"


def generate_happ_link(cmd: str) -> str:
    base = generate_sub_link(cmd)
    encoded = base.replace("https://", "https%3A%2F%2F").replace("/", "%2F")
    return f"https://ssconnect.app/?q=happ%3A%2F%2Fadd%2F{encoded}"


async def send_invoice(message: Message, cmd: str):
    name, stars = PRODUCTS[cmd]
    await message.answer(f"Купить {name}:")
    await message.bot.send_invoice(
        chat_id=message.chat.id,
        title=f"ComboVPN {name}",
        description=f"Подписка ComboVPN {name}",
        payload=f"vpn:{cmd}",
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice(label=f"ComboVPN {name}", amount=stars)],
    )


@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "ComboVPN — это VPN, объединяющий в себе все необходимости для полноценного рунета в настоящее время:\n"
        "<blockquote>• Поддерживается на всех устройствах\n"
        "• Работает на любой сети при любых условиях\n"
        "• Обходит все ограничения от РКН, включая белые списки (на всех операторах и во всех регионах)\n"
        "• Обходит все антироссийские ограничения (блокировки ChatGPT, Claude, Gemini, Grok, Netflix, Spotify, SoundCloud, TikTok, игр Supercell и многого другого)\n"
        "• Не выключается при переключении сети\n"
        "• Не требует выключения для игр и российских сервисов\n"
        "• Удаляет рекламу из YouTube, оставляя доступ к заблокированному в РФ контенту\n"
        "• Быстрый (при включении подключается к самому быстрому серверу из нескольких серверов от разных провайдеров)\n"
        "• Стабильный (при обрыве соединения с текущим сервером автоматически подключается к другому серверу)\n"
        "• Безлимитный (не ограничивает количество устройств и не имеет лимита на трафик ни по скачиванию, ни по загрузке)\n"
        "• Надёжный (перенаправляет трафик только через серверы, доступ которых надёжно защищён)\n"
        "• Самый дешёвый на рынке VPN-сервисов в Telegram</blockquote>\n\n"
        "<i>Предложить идею и/или уточнить какой-либо момент можно написав в поддержку VPN (@ComboVPN_Support)</i>\n\n"
        "Купить:\n"
        "• <a href=\"https://t.me/ComboVPNroBot?start=trial\">на 1 неделю (пробный период)</a>\n"
        "• <a href=\"https://t.me/ComboVPNroBot?start=month_1\">на 1 месяц</a>\n"
        "• <a href=\"https://t.me/ComboVPNroBot?start=month_3\">на 3 месяца</a>\n"
        "• <a href=\"https://t.me/ComboVPNroBot?start=month_6\">на 6 месяцев</a>\n"
        "• <a href=\"https://t.me/ComboVPNroBot?start=month_12\">на 12 месяцев</a>\n"
        "• <a href=\"https://t.me/ComboVPNroBot?start=forever\">навсегда</a>",
        parse_mode="HTML",
    )


@dp.message(F.text.startswith("/start "))
async def cmd_start_deeplink(message: Message):
    arg = message.text.split(" ", 1)[1]
    if arg in PRODUCTS:
        await send_invoice(message, arg)


@dp.message(Command("trial"))
async def cmd_trial(message: Message):
    await send_invoice(message, "trial")

@dp.message(Command("month_1"))
async def cmd_month_1(message: Message):
    await send_invoice(message, "month_1")

@dp.message(Command("month_3"))
async def cmd_month_3(message: Message):
    await send_invoice(message, "month_3")

@dp.message(Command("month_6"))
async def cmd_month_6(message: Message):
    await send_invoice(message, "month_6")

@dp.message(Command("month_12"))
async def cmd_month_12(message: Message):
    await send_invoice(message, "month_12")

@dp.message(Command("forever"))
async def cmd_forever(message: Message):
    await send_invoice(message, "forever")


@dp.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery):
    await query.answer(ok=True)


@dp.message(F.successful_payment)
async def on_paid(message: Message):
    payload = message.successful_payment.invoice_payload
    cmd = payload.split(":")[1]

    sub_link = generate_sub_link(cmd)
    happ_link = generate_happ_link(cmd)

    await message.answer(
        f"Оплата прошла успешно!\n\n"
        f"Твоя подписка:\n"
        f"<code>{sub_link}</code>\n\n"
        f"Открыть в Happ:\n"
        f"{happ_link}",
        parse_mode="HTML",
    )


async def main():
    bot = Bot(token=TOKEN)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())