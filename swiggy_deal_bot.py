import os
import logging
import requests
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters
)

# --- Configuration & Logging ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Conversation States
CITY, ADDRESS, FOOD_TYPE, DIET, MOBILE, OTP = range(6)

class SwiggyAPI:
    """Helper class to interact with Swiggy's internal endpoints"""
    BASE_URL = "https://www.swiggy.com/dapi"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15",
            "Referer": "https://www.swiggy.com/"
        })

    def send_otp(self, mobile):
        # Placeholder for Swiggy's actual Auth endpoint
        # Example: self.session.post(f"{self.BASE_URL}/auth/sms-otp", data={"mobile": mobile})
        return True

    def verify_otp(self, otp):
        # Placeholder for verifying and getting the session cookie
        return True

    def get_best_deal(self, food_type, city):
        # This simulates fetching the 'Winner' restaurant by comparing discounts
        # In a real scenario, you'd iterate through 'restaurants' -> 'offers' array
        mock_deals = [
            {"name": "Biryani House", "discount": 60, "coupon": "WELCOME60"},
            {"name": "Pizza Corner", "discount": 50, "coupon": "SWIGGYIT"},
        ]
        return max(mock_deals, key=lambda x: x['discount'])

# --- Bot Handler Functions ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🍔 *Swiggy Deal Hunter*\n\nStep 1: Which *City* are you in?", parse_mode="Markdown")
    return CITY

async def get_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['city'] = update.message.text
    await update.message.reply_text("📍 Please enter your *Full Delivery Address*:")
    return ADDRESS

async def get_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['address'] = update.message.text
    await update.message.reply_text("🍕 What would you like to eat? (e.g., Biryani, Pizza):")
    return FOOD_TYPE

async def get_food_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['food_type'] = update.message.text
    reply_keyboard = [['Veg', 'Non-Veg', 'Both']]
    await update.message.reply_text(
        "Select preference:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True),
    )
    return DIET

async def get_diet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['diet'] = update.message.text
    await update.message.reply_text(
        "📱 Enter your Swiggy Mobile Number to find personal coupons:",
        reply_markup=ReplyKeyboardRemove()
    )
    return MOBILE

async def get_mobile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mobile = update.message.text
    swiggy = SwiggyAPI()
    context.user_data['swiggy'] = swiggy
    
    if swiggy.send_otp(mobile):
        await update.message.reply_text("📩 OTP sent! Enter it below:")
        return OTP
    else:
        await update.message.reply_text("❌ Failed to send OTP. Try again /start")
        return ConversationHandler.END

async def get_otp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    otp = update.message.text
    swiggy = context.user_data['swiggy']
    
    if swiggy.verify_otp(otp):
        await update.message.reply_text("🔍 *Scanning and comparing all restaurant deals...*", parse_mode="Markdown")
        
        winner = swiggy.get_best_deal(context.user_data['food_type'], context.user_data['city'])
        
        response = (
            f"🏆 *WINNER FOUND!*\n"
            f"━━━━━━━━━━━━━━━\n"
            f"🏪 *Restaurant:* {winner['name']}\n"
            f"🎟 *Best Coupon:* {winner['coupon']}\n"
            f"💰 *Discount:* {winner['discount']}% OFF\n\n"
            f"Ready to order for *{context.user_data['address']}*?"
        )
        await update.message.reply_text(response, parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ Invalid OTP. Use /start to retry.")
    
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Search cancelled. Type /start to search again.")
    return ConversationHandler.END

def main():
    if not BOT_TOKEN:
        print("Error: BOT_TOKEN not found!")
        return

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_city)],
            ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_address)],
            FOOD_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_food_type)],
            DIET: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_diet)],
            MOBILE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_mobile)],
            OTP: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_otp)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    print("Bot is alive...")
    app.run_polling()

if __name__ == "__main__":
    main()

