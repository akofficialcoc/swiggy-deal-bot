import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

# Get bot token from Railway environment variable
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN not found in environment variables")

# Store user city/pincode temporarily
user_city = {}

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🍔 *Welcome to Swiggy Deal Finder Bot*\n\n"
        "📍 Send your *City name or Pincode* to find best food deals.\n\n"
        "⚠️ We never ask for OTP, mobile number, or login.",
        parse_mode="Markdown"
    )

# Save city/pincode
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
        f"📍 Location set to *{city}*\n\nChoose a deal option:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

# Handle button clicks
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    city = user_city.get(query.from_user.id, "India")
    base_url = "https://www.swiggy.com/search?query="

    search_links = {
        "best": f"{base_url}best%20offers%20near%20{city}",
        "cheap": f"{base_url}under%2099%20near%20{city}",
        "veg": f"{base_url}veg%20food%20near%20{city}",
        "nonveg": f"{base_url}non%20veg%20food%20near%20{city}",
        "night": f"{base_url}late%20night%20food%20near%20{city}",
    }

    await query.edit_message_text(
        text="✅ *Deal ready!*\n\nTap below to order safely in Swiggy 👇",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🍽 Open in Swiggy", url=search_links[query.data])]]
        ),
        parse_mode="Markdown"
    )

# Main function
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, save_city))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("🤖 Swiggy Deal Bot is running...")
    app.run_polling()

# Run bot
if __name__ == "__main__":
    main()