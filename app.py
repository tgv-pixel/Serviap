import os
import json
import logging
import asyncio
import time
import sys
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.error import Conflict, NetworkError, TimedOut

# ========== LOGGING ==========
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ========== CONFIG ==========
BOT_TOKEN = os.getenv("BOT_TOKEN", "8543681427:AAF23GGo0ioNexLCDCGHhh0WmIfcV7l2xPM")
PORT = int(os.getenv("PORT", 8080))
ADMIN_IDS = [7420938284]
TON_WALLET = "UQB37g1e9sANIvwdJd3mmxtqveSBae0y-bpqX7DXQPH3c9Lb"
TELEBIRR_NUMBER = "0940980555"

USER_DATA_FILE = "users.json"
ORDER_DATA_FILE = "orders.json"

# ========== SERVICES ==========
SERVICES = {
    'phishing': {
        'name': "🎣 Phishing Page Generator",
        'price_etb': 300,
        'price_usdt': 5,
        'desc': "Custom phishing pages undetectable by browsers. SSL support. Clones any website instantly.",
        'delivery': "2-5 minutes",
        'fields': ['target_url'],
        'field_labels': {'target_url': "📝 Send the URL you want to clone:"}
    },
    'ddos': {
        'name': "🔥 DDoS Attack Panel",
        'price_etb': 500,
        'price_usdt': 8,
        'desc': "Layer 4/7 attack panel. 50Gbps+ power. Instant setup. Multiple attack vectors available.",
        'delivery': "5-10 minutes",
        'fields': ['target', 'attack_type', 'duration'],
        'field_labels': {
            'target': "📝 Send target IP/Website:",
            'attack_type': "📝 Select attack type:",
            'duration': "📝 Select duration:"
        }
    },
    'android_rat': {
        'name': "🦠 Android RAT Builder",
        'price_etb': 400,
        'price_usdt': 6,
        'desc': "Fully undetectable Android RAT. Bind with any app. Access: files, camera, mic, SMS, location, contacts.",
        'delivery': "10-15 minutes",
        'fields': ['app_name', 'features'],
        'field_labels': {
            'app_name': "📝 Send app name to bind with (WhatsApp, Telegram, etc):",
            'features': "📝 Select features needed:\n1. Camera+Mic\n2. Files+SMS\n3. Full Access"
        }
    },
    'sms_bomber': {
        'name': "💣 SMS/OTP Bomber",
        'price_etb': 250,
        'price_usdt': 4,
        'desc': "Ultimate SMS bomber. 1000+ SMS/min. Works worldwide. Perfect for OTP harassment.",
        'delivery': "Instant",
        'fields': ['target_number', 'duration'],
        'field_labels': {
            'target_number': "📝 Send target phone number (+251...):",
            'duration': "📝 Select duration:"
        }
    },
    'social_hack': {
        'name': "📱 Social Media Access",
        'price_etb': 350,
        'price_usdt': 5,
        'desc': "Access any Facebook, Instagram, TikTok, Snapchat account. No login or verification needed from victim.",
        'delivery': "15-30 minutes",
        'fields': ['platform', 'target_profile'],
        'field_labels': {
            'platform': "📝 Select platform:",
            'target_profile': "📝 Send profile link or username:"
        }
    },
    'wifi_crack': {
        'name': "📡 WiFi Password Cracker",
        'price_etb': 300,
        'price_usdt': 5,
        'desc': "Crack any WPA/WPA2/WPA3 WiFi. Cloud cracking for speed. Wordlist generator included.",
        'delivery': "10-20 minutes",
        'fields': ['network_name', 'location'],
        'field_labels': {
            'network_name': "📝 Send WiFi name (SSID):",
            'location': "📝 Send general location (city/area):"
        }
    },
    'telegram_hack': {
        'name': "💬 Telegram Account Access",
        'price_etb': 800,
        'price_usdt': 12,
        'desc': "Full Telegram account access. Get all messages, contacts, media, and files. Completely undetected.",
        'delivery': "20-30 minutes",
        'fields': ['victim_number'],
        'field_labels': {'victim_number': "📝 Send victim's phone number (+251...):"}
    },
    'email_hack': {
        'name': "📧 Email Account Access",
        'price_etb': 200,
        'price_usdt': 3,
        'desc': "Access Gmail, Yahoo, Outlook accounts. All emails, attachments, and contacts included.",
        'delivery': "10-20 minutes",
        'fields': ['target_email'],
        'field_labels': {'target_email': "📝 Send target email address:"}
    },
    'website_hack': {
        'name': "🌐 Website Takeover",
        'price_etb': 450,
        'price_usdt': 7,
        'desc': "Full website takeover. Deface, steal databases, inject malware, or redirect traffic.",
        'delivery': "30-60 minutes",
        'fields': ['target_site', 'action'],
        'field_labels': {
            'target_site': "📝 Send target website URL:",
            'action': "📝 What do you want?\n1. Deface\n2. Steal Database\n3. Redirect\n4. Full Control"
        }
    },
    'crypto_drainer': {
        'name': "💰 Crypto Wallet Drainer",
        'price_etb': 600,
        'price_usdt': 10,
        'desc': "Drain any crypto wallet. MetaMask, TrustWallet, Phantom, Exodus supported. Undetectable smart contract.",
        'delivery': "15-20 minutes",
        'fields': ['wallet_type', 'target_address'],
        'field_labels': {
            'wallet_type': "📝 Select wallet type:\n1. MetaMask\n2. TrustWallet\n3. Phantom\n4. Exodus",
            'target_address': "📝 Send target wallet address:"
        }
    }
}

# ========== TOOLS SHOP ==========
TOOLS = {
    'dark_rat': {
        'name': "DarkRAT v4.2",
        'category': "RAT",
        'price_etb': 600,
        'price_usdt': 10,
        'desc': "Advanced Remote Administration Tool. FUD. Windows & Android. Keylogger, file manager, reverse proxy, persistence.",
        'delivery': "Instant download"
    },
    'phishing_kit': {
        'name': "Phishing Kit Pro 2024",
        'category': "Phishing",
        'price_etb': 400,
        'price_usdt': 6,
        'desc': "25+ premium phishing pages. Banking, social media, crypto wallets. Anti-bot, anti-detection. Full source.",
        'delivery': "Instant download"
    },
    'combo_list': {
        'name': "Combolist 100M+",
        'category': "Database",
        'price_etb': 350,
        'price_usdt': 5,
        'desc': "Email:Pass combos. Freshly cracked 2024. Multiple countries. 60%+ valid. Premium quality.",
        'delivery': "Instant download"
    },
    'proxy_pack': {
        'name': "Socks5 Proxies 50K",
        'category': "Network",
        'price_etb': 200,
        'price_usdt': 3,
        'desc': "Premium residential & datacenter proxies. Checked, working, anonymous. Perfect for carding and cracking.",
        'delivery': "Instant download"
    },
    'crypto_grabber': {
        'name': "Crypto Grabber Configs",
        'category': "Malware",
        'price_etb': 500,
        'price_usdt': 8,
        'desc': "Wallet grabber for MetaMask, TrustWallet, Exodus, Binance Chain. Undetectable. Includes setup guide.",
        'delivery': "Instant download"
    },
    'mirai_botnet': {
        'name': "Mirai Botnet Source",
        'category': "Botnet",
        'price_etb': 700,
        'price_usdt': 11,
        'desc': "Mirai botnet + C2 panel full source. IoT exploitation scripts. Ready to deploy and modify.",
        'delivery': "Instant download"
    },
    'redline_stealer': {
        'name': "RedLine Stealer Cracked",
        'category': "Stealer",
        'price_etb': 450,
        'price_usdt': 7,
        'desc': "Browser password stealer. Cookies, crypto wallets, autofill data. FUD guaranteed 2 weeks. Lifetime updates.",
        'delivery': "Instant download"
    },
    'cpanel_access': {
        'name': "cPanel Access List",
        'category': "Access",
        'price_etb': 350,
        'price_usdt': 5,
        'desc': "cPanel & WHM access credentials. Multiple providers worldwide. Validated and working. Updated weekly.",
        'delivery': "Instant download"
    },
    'rdp_access': {
        'name': "RDP Access Pack",
        'category': "Access",
        'price_etb': 300,
        'price_usdt': 4,
        'desc': "Remote Desktop access. USA, EU, Asia. Admin privileges. Perfect for hosting or carding.",
        'delivery': "Instant download"
    },
    'cc_dumps': {
        'name': "CC Dumps Track 1+2",
        'category': "Cards",
        'price_etb': 500,
        'price_usdt': 8,
        'desc': "Credit card dumps with PIN. Track 1 & 2 included. High balance guarantee. Worldwide BINs.",
        'delivery': "Instant download"
    }
}

# ========== TEXTS ==========
TEXTS = {
    'en': {
        'welcome': "💎 *WELCOME*\n\nChoose language:",
        'main_menu': "💎 *MAIN MENU*\n\nWhat do you need?",
        'services': "🛠 *SERVICES*",
        'tools': "🛒 *TOOLS SHOP*",
        'payment_method': "💳 *Payment*\n\n{amount_etb} Birr / {amount_usdt} USDT\n\nChoose payment:",
        'telebirr_pay': "📱 *Telebirr Payment*\n\nSend: {amount_etb} Birr\nTo: `{number}`\nName: Naol\n\n⚠️ *Send screenshot here after payment*",
        'ton_pay': "💰 *TON (USDT)*\n\nSend: {amount_usdt} USDT\nNetwork: TON\nAddress: `{wallet}`\n\n⚠️ *Send screenshot after payment*",
        'processing': "⏳ *Processing Payment...*\n\nVerifying your transaction...\nThis takes 5-15 minutes.\n\nYou will be notified automatically.",
        'confirmed': "✅ *Payment Verified*\n\nProcessing your order...\nEstimated delivery: {delivery_time}\n\nWe will update you shortly.",
        'completed': "✅ *Order Fulfilled*\n\nYour request has been processed.\n\nThank you for your business.",
        'tool_delivered': "✅ *Purchase Complete*\n\n{name}\n\n📥 Your download is ready.\n\nThank you for your purchase.",
        'ask_field': "{label}",
        'back': "« Back",
        'services_list': "Available services:",
        'tools_list': "Available tools:",
        'choose_attack': "Select attack type:",
        'choose_duration': "Select duration:",
        'choose_sms_duration': "Select duration:",
        'choose_platform': "Select platform:",
        'orders': "📋 *Your Orders*\n\n{orders}",
        'no_orders': "📋 No orders yet. Browse /start"
    },
    'am': {
        'welcome': "💎 *እንኳን ደህና መጡ*\n\nቋንቋ ይምረጡ:",
        'main_menu': "💎 *ዋና ምናሌ*\n\nምን ያስፈልግዎታል?",
        'services': "🛠 *አገልግሎቶች*",
        'tools': "🛒 *የመሳሪያዎች ሱቅ*",
        'payment_method': "💳 *ክፍያ*\n\n{amount_etb} ብር / {amount_usdt} USDT\n\nየክፍያ ዘዴ ይምረጡ:",
        'telebirr_pay': "📱 *የቴሌብር ክፍያ*\n\nላክ: {amount_etb} ብር\nወደ: `{number}`\nስም: ናኦል\n\n⚠️ *ከከፈሉ በኋላ ስክሪንሾት ይላኩ*",
        'ton_pay': "💰 *TON (USDT)*\n\nላክ: {amount_usdt} USDT\nኔትዎርክ: TON\nአድራሻ: `{wallet}`\n\n⚠️ *ከከፈሉ በኋላ ስክሪንሾት ይላኩ*",
        'processing': "⏳ *ክፍያ በመስራት ላይ...*\n\nትራንዛክሽንዎን እያረጋገጥን ነው...\nይህ 5-15 ደቂቃ ይወስዳል።\n\nበራስ-ሰር እናሳውቅዎታለን።",
        'confirmed': "✅ *ክፍያ ተረጋግጧል*\n\nትዕዛዝዎን እየሰራን ነው...\nየሚፈጀው ጊዜ: {delivery_time}\n\nበቅርቡ እናዘምንዎታለን።",
        'completed': "✅ *ትዕዛዝ ተጠናቋል*\n\nጥያቄዎ ተፈጽሟል።\n\nስለተጠቀሙ እናመሰግናለን።",
        'tool_delivered': "✅ *ግዢ ተጠናቋል*\n\n{name}\n\n📥 ማውረድ ዝግጁ ነው።\n\nስለገዙ እናመሰግናለን።",
        'ask_field': "{label}",
        'back': "« ተመለስ",
        'services_list': "የሚገኙ አገልግሎቶች:",
        'tools_list': "የሚገኙ መሳሪያዎች:",
        'choose_attack': "የጥቃት አይነት ይምረጡ:",
        'choose_duration': "ቆይታ ይምረጡ:",
        'choose_sms_duration': "ቆይታ ይምረጡ:",
        'choose_platform': "ፕላትፎርም ይምረጡ:",
        'orders': "📋 *የእርስዎ ትዕዛዞች*\n\n{orders}",
        'no_orders': "📋 እስካሁን ምንም ትዕዛዝ የለም። /start ይጫኑ"
    }
}

# ========== DATA MANAGEMENT ==========
def load_data(file):
    try:
        if os.path.exists(file):
            with open(file, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Error loading {file}: {e}")
    return {}

def save_data(data, file):
    try:
        with open(file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error saving {file}: {e}")

# Initialize data
user_data = load_data(USER_DATA_FILE)
order_data = load_data(ORDER_DATA_FILE)

def get_text(user_id, key, **kwargs):
    lang = user_data.get(str(user_id), {}).get('lang', 'en')
    text = TEXTS.get(lang, TEXTS['en']).get(key, TEXTS['en'].get(key, key))
    if kwargs and isinstance(text, str):
        try:
            text = text.format(**kwargs)
        except KeyError:
            pass
    return text

# ========== HELPERS ==========
ATTACK_TYPES = [
    ("Layer 7 - HTTP Flood", "l7_http"),
    ("Layer 4 - SYN Flood", "l4_syn"),
    ("UDP Amplification", "udp_amp"),
    ("DNS Flood", "dns_flood"),
    ("Mixed Attack (L4+L7)", "mixed")
]

DURATIONS = [
    ("1 Hour", "1"), ("3 Hours", "3"), ("6 Hours", "6"),
    ("12 Hours", "12"), ("24 Hours", "24")
]

SMS_DURATIONS = [
    ("5 Minutes", "5"), ("15 Minutes", "15"),
    ("30 Minutes", "30"), ("1 Hour", "60")
]

PLATFORMS = [
    ("Facebook", "fb"), ("Instagram", "ig"),
    ("TikTok", "tt"), ("Snapchat", "sc"),
    ("Telegram", "tg"), ("WhatsApp", "wa"),
    ("Twitter/X", "tw"), ("Gmail", "gm")
]

# ========== ERROR HANDLER ==========
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(f"Exception while handling an update: {context.error}")
    
    if isinstance(context.error, Conflict):
        logger.error("Conflict error - another instance might be running")
    elif isinstance(context.error, NetworkError):
        logger.error("Network error occurred")
    elif isinstance(context.error, TimedOut):
        logger.error("Request timed out")

# ========== BOT HANDLERS ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    
    if user_id not in user_data:
        user_data[user_id] = {
            'lang': None,
            'current_item': None,
            'current_item_type': None,
            'current_field': 0,
            'order_data': {},
            'pending_payment': None
        }
        save_data(user_data, USER_DATA_FILE)
    
    keyboard = [
        [InlineKeyboardButton("🇬🇧 English", callback_data='lang_en')],
        [InlineKeyboardButton("🇪🇹 አማርኛ", callback_data='lang_am')]
    ]
    
    await update.message.reply_text(
        get_text(user_id, 'welcome'),
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    user_id = str(update.effective_user.id)
    data = query.data
    
    try:
        if data.startswith('lang_'):
            lang = data.split('_')[1]
            user_data[user_id]['lang'] = lang
            save_data(user_data, USER_DATA_FILE)
            
            if lang == 'en':
                await query.edit_message_text("✅ Language: English")
            else:
                await query.edit_message_text("✅ ቋንቋ: አማርኛ")
            
            await show_main_menu(query, user_id)
        
        elif data == 'main_menu':
            reset_user(user_id)
            await show_main_menu(query, user_id)
        
        elif data == 'menu_services':
            await show_services_menu(query, user_id)
        
        elif data == 'menu_tools':
            await show_tools_menu(query, user_id)
        
        elif data == 'menu_orders':
            await show_orders(query, user_id)
        
        elif data.startswith('svc_'):
            service_key = data.replace('svc_', '')
            await show_payment(query, user_id, service_key, 'service')
        
        elif data.startswith('tool_'):
            tool_key = data.replace('tool_', '')
            await show_payment(query, user_id, tool_key, 'tool')
        
        elif data.startswith('pay_tb_'):
            item_key = data.replace('pay_tb_', '')
            await pay_telebirr(query, user_id, item_key)
        
        elif data.startswith('pay_ton_'):
            item_key = data.replace('pay_ton_', '')
            await pay_ton(query, user_id, item_key)
        
        elif data.startswith('opt_'):
            option_value = data.replace('opt_', '')
            item_key = user_data[user_id].get('current_item')
            item = SERVICES.get(item_key) or TOOLS.get(item_key)
            
            if item:
                fields = item.get('fields', [])
                current_field_idx = user_data[user_id].get('current_field', 0)
                
                if current_field_idx < len(fields):
                    field_name = fields[current_field_idx]
                    user_data[user_id]['order_data'][field_name] = option_value
                    save_data(user_data, USER_DATA_FILE)
                    
                    user_data[user_id]['current_field'] = current_field_idx + 1
                    save_data(user_data, USER_DATA_FILE)
                    
                    await ask_next_field(query, user_id, item_key)
        
        elif data == 'back_menu':
            reset_user(user_id)
            await show_main_menu(query, user_id)
    
    except Exception as e:
        logger.error(f"Button error: {e}")
        try:
            await query.edit_message_text("An error occurred. Please use /start to restart.")
        except:
            pass

async def show_main_menu(query, user_id):
    keyboard = [
        [InlineKeyboardButton("🛠 Services", callback_data='menu_services')],
        [InlineKeyboardButton("🛒 Tools Shop", callback_data='menu_tools')],
        [InlineKeyboardButton("📋 My Orders", callback_data='menu_orders')]
    ]
    
    await query.edit_message_text(
        get_text(user_id, 'main_menu'),
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def show_services_menu(query, user_id):
    keyboard = []
    for key, svc in SERVICES.items():
        keyboard.append([
            InlineKeyboardButton(
                f"{svc['name']} - {svc['price_etb']} Birr / {svc['price_usdt']}$",
                callback_data=f'svc_{key}'
            )
        ])
    
    keyboard.append([InlineKeyboardButton(get_text(user_id, 'back'), callback_data='main_menu')])
    
    await query.edit_message_text(
        get_text(user_id, 'services_list'),
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def show_tools_menu(query, user_id):
    keyboard = []
    for key, tool in TOOLS.items():
        keyboard.append([
            InlineKeyboardButton(
                f"{tool['name']} [{tool['category']}] - {tool['price_etb']} Birr",
                callback_data=f'tool_{key}'
            )
        ])
    
    keyboard.append([InlineKeyboardButton(get_text(user_id, 'back'), callback_data='main_menu')])
    
    await query.edit_message_text(
        get_text(user_id, 'tools_list'),
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def show_payment(query, user_id, item_key, item_type):
    item = SERVICES.get(item_key) if item_type == 'service' else TOOLS.get(item_key)
    if not item:
        return
    
    user_data[user_id]['current_item'] = item_key
    user_data[user_id]['current_item_type'] = item_type
    user_data[user_id]['pending_payment'] = None
    user_data[user_id]['current_field'] = 0
    user_data[user_id]['order_data'] = {}
    save_data(user_data, USER_DATA_FILE)
    
    keyboard = [
        [InlineKeyboardButton(
            f"📱 Telebirr ({item['price_etb']} Birr)",
            callback_data=f'pay_tb_{item_key}'
        )],
        [InlineKeyboardButton(
            f"💰 TON USDT ({item['price_usdt']}$)",
            callback_data=f'pay_ton_{item_key}'
        )],
        [InlineKeyboardButton(get_text(user_id, 'back'), callback_data='main_menu')]
    ]
    
    await query.edit_message_text(
        f"*{item['name']}*\n\n{item['desc']}\n\n" +
        get_text(user_id, 'payment_method').format(
            amount_etb=item['price_etb'],
            amount_usdt=item['price_usdt']
        ),
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def pay_telebirr(query, user_id, item_key):
    item = SERVICES.get(item_key) or TOOLS.get(item_key)
    if not item:
        return
    
    user_data[user_id]['pending_payment'] = {
        'item_key': item_key,
        'method': 'telebirr',
        'amount': item['price_etb'],
        'time': datetime.now().isoformat()
    }
    save_data(user_data, USER_DATA_FILE)
    
    await query.edit_message_text(
        get_text(user_id, 'telebirr_pay').format(
            amount_etb=item['price_etb'],
            number=TELEBIRR_NUMBER
        ),
        parse_mode='Markdown'
    )

async def pay_ton(query, user_id, item_key):
    item = SERVICES.get(item_key) or TOOLS.get(item_key)
    if not item:
        return
    
    user_data[user_id]['pending_payment'] = {
        'item_key': item_key,
        'method': 'ton',
        'amount': item['price_usdt'],
        'time': datetime.now().isoformat()
    }
    save_data(user_data, USER_DATA_FILE)
    
    await query.edit_message_text(
        get_text(user_id, 'ton_pay').format(
            amount_usdt=item['price_usdt'],
            wallet=TON_WALLET
        ),
        parse_mode='Markdown'
    )

async def handle_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    username = update.effective_user.username or "No username"
    first_name = update.effective_user.first_name or "Anonymous"
    
    try:
        if update.message.photo:
            photo = update.message.photo[-1]
            caption = update.message.caption or ""
            
            await update.message.reply_text(
                get_text(user_id, 'processing'),
                parse_mode='Markdown'
            )
            
            # Forward to admin
            for admin_id in ADMIN_IDS:
                try:
                    await context.bot.send_photo(
                        chat_id=admin_id,
                        photo=photo.file_id,
                        caption=f"📸 *New Payment*\n\n"
                               f"👤 {first_name} (@{username})\n"
                               f"🆔 `{user_id}`\n"
                               f"📝 {caption}\n\n"
                               f"/approve {user_id}",
                        parse_mode='Markdown'
                    )
                except Exception as e:
                    logger.error(f"Failed to send to admin {admin_id}: {e}")
            
            # Auto-process payment
            await asyncio.sleep(3)
            await process_payment(user_id, context)
            
    except Exception as e:
        logger.error(f"Screenshot error: {e}")

async def process_payment(user_id, context):
    try:
        pending = user_data.get(user_id, {}).get('pending_payment', {})
        item_key = pending.get('item_key')
        item_type = user_data[user_id].get('current_item_type', 'service')
        
        if not item_key:
            return
        
        item = SERVICES.get(item_key) if item_type == 'service' else TOOLS.get(item_key)
        if not item:
            return
        
        # Save order
        if user_id not in order_data:
            order_data[user_id] = []
        order_data[user_id].append({
            'item': item_key,
            'type': item_type,
            'amount': pending.get('amount'),
            'method': pending.get('method'),
            'time': datetime.now().isoformat(),
            'status': 'completed'
        })
        save_data(order_data, ORDER_DATA_FILE)
        
        # Send confirmation
        await context.bot.send_message(
            chat_id=user_id,
            text=get_text(user_id, 'confirmed').format(
                delivery_time=item.get('delivery', 'soon')
            ),
            parse_mode='Markdown'
        )
        
        if item_type == 'tool':
            # Tools: instant delivery
            await asyncio.sleep(2)
            await context.bot.send_message(
                chat_id=user_id,
                text=get_text(user_id, 'tool_delivered').format(name=item['name']),
                parse_mode='Markdown'
            )
            reset_user(user_id)
        else:
            # Services: ask for target details
            await asyncio.sleep(2)
            fields = item.get('fields', [])
            if fields:
                user_data[user_id]['current_field'] = 0
                user_data[user_id]['order_data'] = {}
                save_data(user_data, USER_DATA_FILE)
                await ask_next_field_direct(user_id, context, item_key)
        
        # Clear pending
        user_data[user_id]['pending_payment'] = None
        save_data(user_data, USER_DATA_FILE)
        
    except Exception as e:
        logger.error(f"Process payment error: {e}")

async def ask_next_field(query, user_id, item_key):
    item = SERVICES.get(item_key) or TOOLS.get(item_key)
    if not item:
        return
    
    fields = item.get('fields', [])
    current_idx = user_data[user_id].get('current_field', 0)
    
    if current_idx < len(fields):
        field_name = fields[current_idx]
        label = item['field_labels'].get(field_name, field_name)
        
        if field_name == 'attack_type':
            keyboard = [[InlineKeyboardButton(name, callback_data=f'opt_{val}')] for name, val in ATTACK_TYPES]
            keyboard.append([InlineKeyboardButton(get_text(user_id, 'back'), callback_data='main_menu')])
            await query.edit_message_text(
                get_text(user_id, 'choose_attack'),
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
        elif field_name == 'duration':
            durations = SMS_DURATIONS if 'sms' in item_key.lower() else DURATIONS
            keyboard = [[InlineKeyboardButton(name, callback_data=f'opt_{val}')] for name, val in durations]
            keyboard.append([InlineKeyboardButton(get_text(user_id, 'back'), callback_data='main_menu')])
            await query.edit_message_text(
                get_text(user_id, 'choose_duration'),
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
        elif field_name == 'platform':
            keyboard = [[InlineKeyboardButton(name, callback_data=f'opt_{val}')] for name, val in PLATFORMS]
            keyboard.append([InlineKeyboardButton(get_text(user_id, 'back'), callback_data='main_menu')])
            await query.edit_message_text(
                get_text(user_id, 'choose_platform'),
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
        else:
            await query.edit_message_text(
                get_text(user_id, 'ask_field').format(label=label),
                parse_mode='Markdown'
            )
    else:
        await complete_order(query, user_id, item_key)

async def ask_next_field_direct(user_id, context, item_key):
    item = SERVICES.get(item_key)
    if not item:
        return
    
    fields = item.get('fields', [])
    current_idx = user_data[user_id].get('current_field', 0)
    
    if current_idx < len(fields):
        field_name = fields[current_idx]
        label = item['field_labels'].get(field_name, field_name)
        
        await context.bot.send_message(
            chat_id=user_id,
            text=get_text(user_id, 'ask_field').format(label=label),
            parse_mode='Markdown'
        )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    text = update.message.text
    
    item_key = user_data[user_id].get('current_item')
    item_type = user_data[user_id].get('current_item_type', 'service')
    current_idx = user_data[user_id].get('current_field', 0)
    
    if not item_key:
        return
    
    item = SERVICES.get(item_key) if item_type == 'service' else TOOLS.get(item_key)
    if not item:
        return
    
    fields = item.get('fields', [])
    
    if current_idx < len(fields):
        field_name = fields[current_idx]
        
        if field_name in ['attack_type', 'duration', 'platform']:
            return
        
        user_data[user_id]['order_data'][field_name] = text
        user_data[user_id]['current_field'] = current_idx + 1
        save_data(user_data, USER_DATA_FILE)
        
        if user_data[user_id]['current_field'] < len(fields):
            next_field = fields[user_data[user_id]['current_field']]
            next_label = item['field_labels'].get(next_field, next_field)
            
            if next_field in ['attack_type', 'duration', 'platform']:
                await show_field_buttons(update, user_id, next_field, item_key)
            else:
                await update.message.reply_text(
                    get_text(user_id, 'ask_field').format(label=next_label),
                    parse_mode='Markdown'
                )
        else:
            await complete_order_direct(update, user_id, item_key)

async def show_field_buttons(update, user_id, field_name, item_key):
    if field_name == 'attack_type':
        keyboard = [[InlineKeyboardButton(name, callback_data=f'opt_{val}')] for name, val in ATTACK_TYPES]
        await update.message.reply_text(
            get_text(user_id, 'choose_attack'),
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    elif field_name == 'duration':
        durations = SMS_DURATIONS if 'sms' in item_key.lower() else DURATIONS
        keyboard = [[InlineKeyboardButton(name, callback_data=f'opt_{val}')] for name, val in durations]
        await update.message.reply_text(
            get_text(user_id, 'choose_duration'),
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    elif field_name == 'platform':
        keyboard = [[InlineKeyboardButton(name, callback_data=f'opt_{val}')] for name, val in PLATFORMS]
        await update.message.reply_text(
            get_text(user_id, 'choose_platform'),
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )

async def complete_order(query, user_id, item_key):
    order_details = user_data[user_id].get('order_data', {})
    
    if user_id in order_data and order_data[user_id]:
        order_data[user_id][-1]['details'] = order_details
        save_data(order_data, ORDER_DATA_FILE)
    
    reset_user(user_id)
    
    await query.edit_message_text(
        get_text(user_id, 'completed'),
        parse_mode='Markdown'
    )

async def complete_order_direct(update, user_id, item_key):
    order_details = user_data[user_id].get('order_data', {})
    
    if user_id in order_data and order_data[user_id]:
        order_data[user_id][-1]['details'] = order_details
        save_data(order_data, ORDER_DATA_FILE)
    
    reset_user(user_id)
    
    await update.message.reply_text(
        get_text(user_id, 'completed'),
        parse_mode='Markdown'
    )

async def show_orders(query, user_id):
    orders = order_data.get(user_id, [])
    
    if not orders:
        await query.edit_message_text(
            get_text(user_id, 'no_orders'),
            parse_mode='Markdown'
        )
        return
    
    msg = ""
    for i, order in enumerate(orders[-5:], 1):
        item = SERVICES.get(order['item']) or TOOLS.get(order['item'])
        name = item['name'] if item else order['item']
        time_str = order.get('time', '')[:10]
        msg += f"{i}. {name} - ✅ {time_str}\n"
    
    keyboard = [[InlineKeyboardButton(get_text(user_id, 'back'), callback_data='main_menu')]]
    
    await query.edit_message_text(
        get_text(user_id, 'orders').format(orders=msg),
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

def reset_user(user_id):
    if user_id in user_data:
        user_data[user_id]['current_item'] = None
        user_data[user_id]['current_item_type'] = None
        user_data[user_id]['current_field'] = 0
        user_data[user_id]['order_data'] = {}
        user_data[user_id]['pending_payment'] = None
        save_data(user_data, USER_DATA_FILE)

# ========== ADMIN COMMANDS ==========
async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    try:
        target_user = str(context.args[0])
        if target_user in user_data:
            await process_payment(target_user, context)
            await update.message.reply_text(f"✅ Processed payment for {target_user}")
        else:
            await update.message.reply_text("❌ User not found")
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /approve <user_id>")

async def reject(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    try:
        target_user = str(context.args[0])
        reset_user(target_user)
        try:
            await context.bot.send_message(
                chat_id=target_user,
                text="❌ Payment failed. Please try again or contact support."
            )
        except:
            pass
        await update.message.reply_text(f"✅ Rejected payment for {target_user}")
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /reject <user_id>")

async def orders_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    if not order_data:
        await update.message.reply_text("No orders yet.")
        return
    
    msg = "*All Orders:*\n\n"
    for uid, orders in order_data.items():
        msg += f"User `{uid}`: {len(orders)} orders\n"
        for order in orders[-3:]:
            msg += f"  - {order.get('item', '?')} ({order.get('method', '?')})\n"
    
    await update.message.reply_text(msg[:4000], parse_mode='Markdown')

# ========== HEALTH CHECK SERVER ==========
from http.server import HTTPServer, BaseHTTPRequestHandler

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Bot is running')
    
    def log_message(self, format, *args):
        pass

def run_health_server():
    server = HTTPServer(('0.0.0.0', PORT), HealthCheckHandler)
    logger.info(f"Health check server running on port {PORT}")
    server.serve_forever()

# ========== MAIN ==========
def main():
    logger.info("Starting bot initialization...")
    
    # Build application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("approve", approve))
    application.add_handler(CommandHandler("reject", reject))
    application.add_handler(CommandHandler("orders", orders_cmd))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.PHOTO, handle_screenshot))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    # Start health check server in a separate thread
    import threading
    health_thread = threading.Thread(target=run_health_server, daemon=True)
    health_thread.start()
    
    logger.info("Bot is starting polling...")
    
    # Run the bot with retry logic
    while True:
        try:
            application.run_polling(
                drop_pending_updates=True,
                allowed_updates=Update.ALL_TYPES
            )
        except Conflict as e:
            logger.error(f"Conflict error: {e}")
            logger.info("Waiting 15 seconds before retry...")
            time.sleep(15)
        except NetworkError as e:
            logger.error(f"Network error: {e}")
            logger.info("Waiting 10 seconds before retry...")
            time.sleep(10)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            logger.info("Waiting 10 seconds before retry...")
            time.sleep(10)

if __name__ == "__main__":
    main()
