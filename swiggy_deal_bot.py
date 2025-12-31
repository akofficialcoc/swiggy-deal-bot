import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    ConversationFactory,
    filters
)

# Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Conversation States
CITY, ADDRESS, FOOD_TYPE, DIET, MOBILE, OTP, COMPARE = range(7)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- Step 1: Start & City ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🍔 *Swiggy Pro Hunter Bot*\n\nStep 1: Which *City* are you in?",
        parse_mode="Markdown"
    )
    return CITY

# --- Step 2: Address ---
async def get_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['city'] = update.message.text
    await update.message.reply_text("📍 Please enter your *Full Delivery Address* (to calculate exact discounts):", parse_mode="Markdown")
    return ADDRESS

# --- Step 3: Food Type ---
async def get_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['address'] = update.message.text
    await update.message.reply_text("🍕 What do you want to eat? (e.g. Biryani, Pizza, North Indian):")
    return FOOD_TYPE

# --- Step 4: Veg/Non-Veg ---
async def get_food_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['food_type'] = update.message.text
    reply_keyboard = [['Veg Only', 'Non-Veg', 'Both']]
    await update.message.reply_text(
        "Select preference:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True),
    )
    return DIET

# --- Step 5: Mobile Number ---
async def get_diet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['diet'] = update.message.text
    await update.message.reply_text(
        "📱 To find *Account-Specific Coupons* (like HDFC, ICICI, or User-Specific), please enter your Swiggy Mobile Number:",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="Markdown"
    )
    return MOBILE

# --- Step 6: OTP (The Login Simulation) ---
async def get_mobile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['mobile'] = update.message.text
    # HERE: You would trigger the Swiggy Auth API to send an OTP
    await update.message.reply_text("📩 OTP sent to your phone. Please enter it here:")
    return OTP

# --- Step 7: Comparison Logic ---
async def get_otp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    otp = update.message.text
    await update.message.reply_text("🔄 *Logging in and comparing all restaurant coupons...*", parse_mode="Markdown")
    
    # SIMULATED LOGIC:
    # 1. Fetch restaurants for 'food_type' in 'city'
    # 2. Loop through each restaurant's 'offers' array
    # 3. Calculate: (Discount Amount / Base Price)
    
    results = [
        {"name": "Biryani Paradise", "coupon": "WELCOME60", "discount": "60%", "final": "₹120"},
        {"name": "Pizza Hut", "coupon": "SWIGGYIT", "discount": "50%", "final": "₹250"},
        {"name": "The Bowl Co", "coupon": "JUMBO", "discount": "₹100 OFF", "final": "₹180"}
    ]
    
    # Finding the 'Winner' (Greatest Coupon)
    winner = results[0] 

    response = (
        f"🏆 *WINNER RESTAURANT*\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🏪 *Name:* {winner['name']}\n"
        f"🎟 *Best Coupon:* {winner['coupon']}\n"
        f"💰 *Discount:* {winner['discount']}\n"
        f"💵 *Effective Price:* {winner['final']}\n\n"
        f"📍 *Delivering to:* {context.user_data['address']}"
    )

    await update.message.reply_text(response, parse_mode="Markdown")
    return ConversationFactory.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Process cancelled. Type /start to try again.")
    return ConversationFactory.END

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationFactory(
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
    app.run_polling()

if __name__ == "__main__":
    main()
