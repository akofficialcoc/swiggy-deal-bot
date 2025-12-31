from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

import os
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Store user location
user_city = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🍔 Welcome to Swiggy Deal Finder Bot\n\n"
        "Send your *City name or Pincode* to find best food deals.\n\n"
        "⚠️ We NEVER ask for OTP or login.",
        parse_mode="Markdown"
    )

async def save_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = update.message.text.strip()
    user_city[update.effective_user.id] = city

    keyboard = [
        [InlineKeyboardButton("🔥 Best Deals", callback_data="best")],
        [InlineKeyboardButton("💸 Under ₹99", callback_data="cheap")],
        [InlineKeyboardButton("🥗 Veg Only", callback_data="veg")],
        [InlineKeyboardButton("🍗 Non-Veg", callback_data="nonveg")],
        [InlineKeyboardButton("🌙 Night Offers", callback_data="night")]
    ]

    await update.message.reply_text(
        f"📍 Location set: *{city}*\n\nChoose an option:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    city = user_city.get(query.from_user.id, "India")
    base = "https://www.swiggy.com/search?query="

    links = {
        "best": f"{base}best%20offers%20near%20{city}",
        "cheap": f"{base}under%2099%20near%20{city}",
        "veg": f"{base}veg%20food%20near%20{city}",
        "nonveg": f"{base}non%20veg%20food%20near%20{city}",
        "night": f"{base}late%20night%20food%20near%20{city}",
    }

    keyboard = [
        [InlineKeyboardButton("🍽 Open in Swiggy", url=links[query.data])]
    ]

    await query.edit_message_text(
        text="✅ Best option found!\n\nClick below to order safely in Swiggy app 👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, save_city))
    app.add_handler(MessageHandler(filters.StatusUpdate.ALL, lambda x,y: None))
    app.add_handler(
        telegram.ext.CallbackQueryHandler(button_handler)
    )

    print("🤖 Swiggy Deal Bot Running...")
    app.run_polling()

if __name__ == "__main__":
    main()
