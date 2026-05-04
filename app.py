import os
import json
import logging
import asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ========== LOGGING ==========
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ========== CONFIG ==========
BOT_TOKEN = "8543681427:AAF23GGo0ioNexLCDCGHhh0WmIfcV7l2xPM"
ADMIN_IDS = [7420938284]
TON_WALLET = "UQB37g1e9sANIvwdJd3mmxtqveSBae0y-bpqX7DXQPH3c9Lb"
TELEBIRR_NUMBER = "0940980555"

# ========== SERVICES ==========
SERVICES = {
    'phishing': {'name': "🎣 Phishing Page Generator", 'price_etb': 300, 'price_usdt': 5, 'desc': "Custom phishing pages. Clones any website.", 'delivery': "2-5 min", 'fields': ['target_url'], 'field_labels': {'target_url': "Send URL to clone:"}},
    'ddos': {'name': "🔥 DDoS Attack Panel", 'price_etb': 500, 'price_usdt': 8, 'desc': "L4/L7 attack panel. 50Gbps+ power.", 'delivery': "5-10 min", 'fields': ['target', 'attack_type', 'duration'], 'field_labels': {'target': "Send target IP/Website:", 'attack_type': "Select attack type:", 'duration': "Select duration:"}},
    'android_rat': {'name': "🦠 Android RAT Builder", 'price_etb': 400, 'price_usdt': 6, 'desc': "FUD Android RAT. Bind with any app.", 'delivery': "10-15 min", 'fields': ['app_name'], 'field_labels': {'app_name': "Send app name:"}},
    'sms_bomber': {'name': "💣 SMS/OTP Bomber", 'price_etb': 250, 'price_usdt': 4, 'desc': "1000+ SMS/min. Worldwide.", 'delivery': "Instant", 'fields': ['target_number', 'duration'], 'field_labels': {'target_number': "Send phone number:", 'duration': "Select duration:"}},
    'social_hack': {'name': "📱 Social Media Access", 'price_etb': 350, 'price_usdt': 5, 'desc': "FB, IG, TikTok, Snapchat access.", 'delivery': "15-30 min", 'fields': ['platform', 'target_profile'], 'field_labels': {'platform': "Select platform:", 'target_profile': "Send profile link:"}},
    'telegram_hack': {'name': "💬 Telegram Account Access", 'price_etb': 800, 'price_usdt': 12, 'desc': "Full Telegram account access.", 'delivery': "20-30 min", 'fields': ['victim_number'], 'field_labels': {'victim_number': "Send victim number:"}},
    'email_hack': {'name': "📧 Email Account Access", 'price_etb': 200, 'price_usdt': 3, 'desc': "Gmail, Yahoo, Outlook access.", 'delivery': "10-20 min", 'fields': ['target_email'], 'field_labels': {'target_email': "Send email:"}},
    'website_hack': {'name': "🌐 Website Takeover", 'price_etb': 450, 'price_usdt': 7, 'desc': "Deface, steal DB, redirect.", 'delivery': "30-60 min", 'fields': ['target_site'], 'field_labels': {'target_site': "Send website URL:"}},
    'crypto_drainer': {'name': "💰 Crypto Wallet Drainer", 'price_etb': 600, 'price_usdt': 10, 'desc': "MetaMask, TrustWallet, Phantom.", 'delivery': "15-20 min", 'fields': ['target_address'], 'field_labels': {'target_address': "Send wallet address:"}}
}

TOOLS = {
    'dark_rat': {'name': "DarkRAT v4.2", 'category': "RAT", 'price_etb': 600, 'price_usdt': 10, 'desc': "FUD RAT. Windows & Android.", 'delivery': "Instant"},
    'phishing_kit': {'name': "Phishing Kit Pro", 'category': "Phishing", 'price_etb': 400, 'price_usdt': 6, 'desc': "25+ phishing pages.", 'delivery': "Instant"},
    'combo_list': {'name': "Combolist 100M+", 'category': "Database", 'price_etb': 350, 'price_usdt': 5, 'desc': "Email:Pass combos.", 'delivery': "Instant"},
    'proxy_pack': {'name': "Socks5 Proxies 50K", 'category': "Network", 'price_etb': 200, 'price_usdt': 3, 'desc': "Premium proxies.", 'delivery': "Instant"},
    'crypto_grabber': {'name': "Crypto Grabber", 'category': "Malware", 'price_etb': 500, 'price_usdt': 8, 'desc': "Wallet grabber configs.", 'delivery': "Instant"},
    'mirai_botnet': {'name': "Mirai Botnet Source", 'category': "Botnet", 'price_etb': 700, 'price_usdt': 11, 'desc': "Full source + C2 panel.", 'delivery': "Instant"},
    'redline_stealer': {'name': "RedLine Stealer", 'category': "Stealer", 'price_etb': 450, 'price_usdt': 7, 'desc': "Browser password stealer.", 'delivery': "Instant"},
    'cpanel_access': {'name': "cPanel Access", 'category': "Access", 'price_etb': 350, 'price_usdt': 5, 'desc': "cPanel credentials list.", 'delivery': "Instant"},
    'rdp_access': {'name': "RDP Access Pack", 'category': "Access", 'price_etb': 300, 'price_usdt': 4, 'desc': "RDP admin access.", 'delivery': "Instant"},
    'cc_dumps': {'name': "CC Dumps T1+T2", 'category': "Cards", 'price_etb': 500, 'price_usdt': 8, 'desc': "CC dumps with PIN.", 'delivery': "Instant"}
}

TEXTS = {
    'en': {
        'welcome': "💎 *WELCOME*\n\nChoose language:",
        'main_menu': "💎 *MAIN MENU*",
        'payment_method': "💳 *Payment*\n{amount_etb} Birr / {amount_usdt} USDT\n\nChoose:",
        'telebirr_pay': "📱 *Telebirr*\nSend {amount_etb} Birr\nTo: `{number}`\nName: Naol\n\nSend screenshot here",
        'ton_pay': "💰 *TON USDT*\nSend {amount_usdt} USDT\nNetwork: TON\n`{wallet}`\n\nSend screenshot",
        'processing': "⏳ *Processing Payment...*\n\nVerifying... 5-15 minutes.",
        'confirmed': "✅ *Payment Verified*\n\nProcessing... Delivery: {delivery_time}",
        'completed': "✅ *Order Fulfilled*\n\nDone. Thank you.",
        'tool_delivered': "✅ *Purchase Complete*\n\n{name}\n\nDownload ready.",
        'ask_field': "{label}",
        'back': "« Back",
        'services_list': "🛠 *SERVICES*",
        'tools_list': "🛒 *TOOLS SHOP*",
        'orders': "📋 *Orders*\n\n{orders}",
        'no_orders': "No orders yet."
    },
    'am': {
        'welcome': "💎 *እንኳን ደህና መጡ*\n\nቋንቋ ይምረጡ:",
        'main_menu': "💎 *ዋና ምናሌ*",
        'payment_method': "💳 *ክፍያ*\n{amount_etb} ብር / {amount_usdt} USDT\n\nዘዴ ይምረጡ:",
        'telebirr_pay': "📱 *ቴሌብር*\nላክ {amount_etb} ብር\nወደ: `{number}`\nስም: ናኦል\n\nስክሪንሾት ይላኩ",
        'ton_pay': "💰 *TON USDT*\nላክ {amount_usdt} USDT\nኔትዎርክ: TON\n`{wallet}`\n\nስክሪንሾት ይላኩ",
        'processing': "⏳ *ክፍያ በመስራት ላይ...*\n\nበማረጋገጥ ላይ... 5-15 ደቂቃ።",
        'confirmed': "✅ *ክፍያ ተረጋግጧል*\n\nበማሰራት ላይ... ጊዜ: {delivery_time}",
        'completed': "✅ *ትዕዛዝ ተጠናቋል*\n\nተጠናቋል። እናመሰግናለን።",
        'tool_delivered': "✅ *ግዢ ተጠናቋል*\n\n{name}\n\nማውረድ ዝግጁ ነው።",
        'ask_field': "{label}",
        'back': "« ተመለስ",
        'services_list': "🛠 *አገልግሎቶች*",
        'tools_list': "🛒 *የመሳሪያዎች ሱቅ*",
        'orders': "📋 *ትዕዛዞች*\n\n{orders}",
        'no_orders': "እስካሁን ምንም ትዕዛዝ የለም።"
    }
}

# Store user data in memory (will reset on restart, but keeps it simple)
user_data = {}
order_data = {}

def get_text(user_id, key, **kwargs):
    lang = user_data.get(str(user_id), {}).get('lang', 'en')
    text = TEXTS.get(lang, TEXTS['en']).get(key, '')
    if kwargs and text:
        try:
            text = text.format(**kwargs)
        except:
            pass
    return text

ATTACK_TYPES = [("Layer 7 HTTP", "l7"), ("Layer 4 SYN", "l4"), ("UDP Amp", "udp"), ("DNS Flood", "dns"), ("Mixed", "mixed")]
DURATIONS = [("1 Hour", "1"), ("3 Hours", "3"), ("6 Hours", "6"), ("12 Hours", "12"), ("24 Hours", "24")]
SMS_DURATIONS = [("5 Min", "5"), ("15 Min", "15"), ("30 Min", "30"), ("1 Hour", "60")]
PLATFORMS = [("Facebook", "fb"), ("Instagram", "ig"), ("TikTok", "tt"), ("Snapchat", "sc"), ("Telegram", "tg"), ("WhatsApp", "wa")]

async def error_handler(update, context):
    logger.error(f"Error: {context.error}")

async def start(update, context):
    user_id = str(update.effective_user.id)
    if user_id not in user_data:
        user_data[user_id] = {'lang': None, 'current_item': None, 'order_data': {}, 'current_field': 0}
    
    keyboard = [[InlineKeyboardButton("🇬🇧 English", callback_data='lang_en')], [InlineKeyboardButton("🇪🇹 አማርኛ", callback_data='lang_am')]]
    await update.message.reply_text(get_text(user_id, 'welcome'), reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def button_handler(update, context):
    query = update.callback_query
    await query.answer()
    user_id = str(update.effective_user.id)
    d = query.data
    
    try:
        if d.startswith('lang_'):
            user_data[user_id]['lang'] = d.split('_')[1]
            await query.edit_message_text("✅ English" if user_data[user_id]['lang'] == 'en' else "✅ አማርኛ")
            keyboard = [[InlineKeyboardButton("🛠 Services", callback_data='svcs')], [InlineKeyboardButton("🛒 Tools Shop", callback_data='tools')], [InlineKeyboardButton("📋 Orders", callback_data='orders')]]
            await query.message.reply_text(get_text(user_id, 'main_menu'), reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
        
        elif d == 'menu':
            user_data[user_id]['current_item'] = None
            keyboard = [[InlineKeyboardButton("🛠 Services", callback_data='svcs')], [InlineKeyboardButton("🛒 Tools Shop", callback_data='tools')], [InlineKeyboardButton("📋 Orders", callback_data='orders')]]
            await query.edit_message_text(get_text(user_id, 'main_menu'), reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
        
        elif d == 'svcs':
            kb = [[InlineKeyboardButton(f"{v['name']} - {v['price_etb']} Br", callback_data=f"s_{k}")] for k, v in SERVICES.items()]
            kb.append([InlineKeyboardButton(get_text(user_id, 'back'), callback_data='menu')])
            await query.edit_message_text(get_text(user_id, 'services_list'), reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')
        
        elif d == 'tools':
            kb = [[InlineKeyboardButton(f"{v['name']} [{v['category']}] - {v['price_etb']} Br", callback_data=f"t_{k}")] for k, v in TOOLS.items()]
            kb.append([InlineKeyboardButton(get_text(user_id, 'back'), callback_data='menu')])
            await query.edit_message_text(get_text(user_id, 'tools_list'), reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')
        
        elif d.startswith('s_') or d.startswith('t_'):
            key = d[2:]
            item_type = 'service' if d.startswith('s_') else 'tool'
            item = SERVICES.get(key) or TOOLS.get(key)
            user_data[user_id]['current_item'] = key
            user_data[user_id]['current_type'] = item_type
            user_data[user_id]['order_data'] = {}
            user_data[user_id]['current_field'] = 0
            
            kb = [[InlineKeyboardButton(f"📱 Telebirr ({item['price_etb']} Br)", callback_data=f"ptb_{key}")], [InlineKeyboardButton(f"💰 TON ({item['price_usdt']}$)", callback_data=f"pton_{key}")], [InlineKeyboardButton(get_text(user_id, 'back'), callback_data='menu')]]
            await query.edit_message_text(f"*{item['name']}*\n{item['desc']}\n\n{get_text(user_id, 'payment_method').format(amount_etb=item['price_etb'], amount_usdt=item['price_usdt'])}", reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')
        
        elif d.startswith('ptb_'):
            key = d[4:]
            item = SERVICES.get(key) or TOOLS.get(key)
            user_data[user_id]['pending'] = {'key': key, 'method': 'telebirr', 'amount': item['price_etb']}
            await query.edit_message_text(get_text(user_id, 'telebirr_pay').format(amount_etb=item['price_etb'], number=TELEBIRR_NUMBER), parse_mode='Markdown')
        
        elif d.startswith('pton_'):
            key = d[5:]
            item = SERVICES.get(key) or TOOLS.get(key)
            user_data[user_id]['pending'] = {'key': key, 'method': 'ton', 'amount': item['price_usdt']}
            await query.edit_message_text(get_text(user_id, 'ton_pay').format(amount_usdt=item['price_usdt'], wallet=TON_WALLET), parse_mode='Markdown')
        
        elif d.startswith('opt_'):
            val = d[4:]
            key = user_data[user_id].get('current_item')
            item = SERVICES.get(key) or TOOLS.get(key)
            if item:
                fields = item.get('fields', [])
                idx = user_data[user_id].get('current_field', 0)
                if idx < len(fields):
                    user_data[user_id]['order_data'][fields[idx]] = val
                    user_data[user_id]['current_field'] = idx + 1
                    await show_next_field(query, user_id, key, item)
        
        elif d == 'orders':
            await query.edit_message_text(get_text(user_id, 'no_orders'), parse_mode='Markdown')
    
    except Exception as e:
        logger.error(f"Button error: {e}")

async def show_next_field(query, user_id, key, item):
    fields = item.get('fields', [])
    idx = user_data[user_id].get('current_field', 0)
    
    if idx < len(fields):
        fname = fields[idx]
        label = item.get('field_labels', {}).get(fname, fname)
        
        if fname == 'attack_type':
            kb = [[InlineKeyboardButton(n, callback_data=f'opt_{v}')] for n, v in ATTACK_TYPES]
            kb.append([InlineKeyboardButton(get_text(user_id, 'back'), callback_data='menu')])
            await query.edit_message_text("Select attack type:", reply_markup=InlineKeyboardMarkup(kb))
        elif fname == 'duration':
            dur = SMS_DURATIONS if 'sms' in key else DURATIONS
            kb = [[InlineKeyboardButton(n, callback_data=f'opt_{v}')] for n, v in dur]
            kb.append([InlineKeyboardButton(get_text(user_id, 'back'), callback_data='menu')])
            await query.edit_message_text("Select duration:", reply_markup=InlineKeyboardMarkup(kb))
        elif fname == 'platform':
            kb = [[InlineKeyboardButton(n, callback_data=f'opt_{v}')] for n, v in PLATFORMS]
            kb.append([InlineKeyboardButton(get_text(user_id, 'back'), callback_data='menu')])
            await query.edit_message_text("Select platform:", reply_markup=InlineKeyboardMarkup(kb))
        else:
            await query.edit_message_text(label, parse_mode='Markdown')
    else:
        user_data[user_id]['current_item'] = None
        await query.edit_message_text(get_text(user_id, 'completed'), parse_mode='Markdown')

async def handle_photo(update, context):
    user_id = str(update.effective_user.id)
    
    if update.message.photo:
        for admin in ADMIN_IDS:
            try:
                await context.bot.send_photo(admin, update.message.photo[-1].file_id, caption=f"Payment from `{user_id}`", parse_mode='Markdown')
            except:
                pass
        
        await update.message.reply_text(get_text(user_id, 'processing'), parse_mode='Markdown')
        await asyncio.sleep(3)
        
        pending = user_data[user_id].get('pending', {})
        key = pending.get('key')
        item_type = user_data[user_id].get('current_type', 'service')
        
        if key:
            item = SERVICES.get(key) if item_type == 'service' else TOOLS.get(key)
            if item:
                await context.bot.send_message(user_id, get_text(user_id, 'confirmed').format(delivery_time=item.get('delivery', 'soon')), parse_mode='Markdown')
                
                if item_type == 'tool':
                    await asyncio.sleep(2)
                    await context.bot.send_message(user_id, get_text(user_id, 'tool_delivered').format(name=item['name']), parse_mode='Markdown')
                    user_data[user_id]['current_item'] = None
                else:
                    await asyncio.sleep(2)
                    fields = item.get('fields', [])
                    if fields:
                        user_data[user_id]['order_data'] = {}
                        user_data[user_id]['current_field'] = 0
                        fname = fields[0]
                        label = item.get('field_labels', {}).get(fname, fname)
                        
                        if fname in ['attack_type', 'duration', 'platform']:
                            if fname == 'attack_type':
                                kb = [[InlineKeyboardButton(n, callback_data=f'opt_{v}')] for n, v in ATTACK_TYPES]
                                await context.bot.send_message(user_id, "Select attack type:", reply_markup=InlineKeyboardMarkup(kb))
                            elif fname == 'duration':
                                dur = SMS_DURATIONS if 'sms' in key else DURATIONS
                                kb = [[InlineKeyboardButton(n, callback_data=f'opt_{v}')] for n, v in dur]
                                await context.bot.send_message(user_id, "Select duration:", reply_markup=InlineKeyboardMarkup(kb))
                            elif fname == 'platform':
                                kb = [[InlineKeyboardButton(n, callback_data=f'opt_{v}')] for n, v in PLATFORMS]
                                await context.bot.send_message(user_id, "Select platform:", reply_markup=InlineKeyboardMarkup(kb))
                        else:
                            await context.bot.send_message(user_id, label, parse_mode='Markdown')
            
            user_data[user_id]['pending'] = {}

async def handle_text(update, context):
    user_id = str(update.effective_user.id)
    text = update.message.text
    key = user_data[user_id].get('current_item')
    
    if not key:
        return
    
    item = SERVICES.get(key) or TOOLS.get(key)
    if not item:
        return
    
    fields = item.get('fields', [])
    idx = user_data[user_id].get('current_field', 0)
    
    if idx < len(fields):
        fname = fields[idx]
        if fname in ['attack_type', 'duration', 'platform']:
            return
        user_data[user_id]['order_data'][fname] = text
        user_data[user_id]['current_field'] = idx + 1
        
        if user_data[user_id]['current_field'] < len(fields):
            next_f = fields[user_data[user_id]['current_field']]
            next_label = item.get('field_labels', {}).get(next_f, next_f)
            
            if next_f in ['attack_type', 'duration', 'platform']:
                if next_f == 'attack_type':
                    kb = [[InlineKeyboardButton(n, callback_data=f'opt_{v}')] for n, v in ATTACK_TYPES]
                    await update.message.reply_text("Select attack type:", reply_markup=InlineKeyboardMarkup(kb))
                elif next_f == 'duration':
                    dur = SMS_DURATIONS if 'sms' in key else DURATIONS
                    kb = [[InlineKeyboardButton(n, callback_data=f'opt_{v}')] for n, v in dur]
                    await update.message.reply_text("Select duration:", reply_markup=InlineKeyboardMarkup(kb))
                elif next_f == 'platform':
                    kb = [[InlineKeyboardButton(n, callback_data=f'opt_{v}')] for n, v in PLATFORMS]
                    await update.message.reply_text("Select platform:", reply_markup=InlineKeyboardMarkup(kb))
            else:
                await update.message.reply_text(next_label, parse_mode='Markdown')
        else:
            user_data[user_id]['current_item'] = None
            await update.message.reply_text(get_text(user_id, 'completed'), parse_mode='Markdown')

# ========== MAIN ==========
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_error_handler(error_handler)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    logger.info("Bot starting...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
