import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

Token = "7654182339:AAFnOgNQ6ivRGgZHAj3kIc7mXQjvZHBwt0o"
user_file = "user.json"

roza_times = {
    i: {"sahur": f"04:{30+i%10:02d}", "iftor": f"18:{45+i%10:02d}"} for i in range(1, 31)
}

duolar = {
    "Ro'za tutish uchun": "Navvaytu an asuma ghadin...",
    "Ro'zani ochish uchun": "Allohumma laka sumtu...",
    "Qo'shimcha duo": "Robbana taqabbal minna...",
}


def save_to_json(data):
    if not os.path.exists(user_file):
        with open(user_file, 'w') as file:
            json.dump([], file, indent=4)
    with open(user_file, 'r') as file:
        existing_data = json.load(file)

    existing_data.append(data)

    with open(user_file, 'w') as file:
        json.dump(existing_data, file, indent=4)


def chunk_buttons(buttons, chunk_size=5):
    return [buttons[i:i + chunk_size] for i in range(0, len(buttons), chunk_size)]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Ro'za vaqtlarini ko'rish", callback_data="show_roza_times")],
        [InlineKeyboardButton("O'qiladigan duolarni ko'rish", callback_data="show_duas")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Assalomu alaykum! Ramazon ro'za va duolarini ko'rish uchun tugmalardan foydalaning.",
        reply_markup=reply_markup
    )


async def show_roza_times(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    buttons = [InlineKeyboardButton(f"{i}-kun", callback_data=f"roza_{i}") for i in range(1, 31)]

    keyboard = chunk_buttons(buttons, chunk_size=5)
    keyboard.append([InlineKeyboardButton("Bekor qilish", callback_data="cancel")])  # Oxirgi qator

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text("Ro'za vaqtlarini ko'rish uchun kunni tanlang:", reply_markup=reply_markup)


async def roza_times_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    selected_day = int(query.data.split("_")[1])
    sahar = roza_times[selected_day]["sahur"]
    iftor = roza_times[selected_day]["iftor"]

    message = f"Ro'zaning {selected_day}-kuni:\n\nSahar vaqti: {sahar}\nIftor vaqti: {iftor}"

    user_data = {
        "user_id": query.from_user.id,
        "user_name": query.from_user.username,
        "day": selected_day,
        "sahur": sahar,
        "iftor": iftor,
    }
    save_to_json(user_data)

    keyboard = [
        [InlineKeyboardButton("Boshqa kunni tanlash", callback_data="show_roza_times")],
        [InlineKeyboardButton("Bekor qilish", callback_data="cancel")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(message, reply_markup=reply_markup)


async def show_duas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    message = "Duolar:\n\n"
    for name, text in duolar.items():
        message += f"{name}: {text}\n\n"

    keyboard = [
        [InlineKeyboardButton("Asosiy menyuga qaytish", callback_data="start")],
        [InlineKeyboardButton("Bekor qilish", callback_data="cancel")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(message, reply_markup=reply_markup)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Amal bekor qilindi.")


if __name__ == "__main__":
    app = ApplicationBuilder().token(Token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(show_roza_times, pattern="^show_roza_times$"))
    app.add_handler(CallbackQueryHandler(roza_times_handler, pattern="^roza_\\d+$"))
    app.add_handler(CallbackQueryHandler(show_duas, pattern="^show_duas$"))
    app.add_handler(CallbackQueryHandler(cancel, pattern="^cancel$"))

    print("Bot ishlamoqda!")
    app.run_polling()
