# hosting_bot.py
import telebot
import json
import os
import time
import shutil
import zipfile
import requests
from datetime import datetime
import threading

# Bot Configuration
BOT_TOKEN = '8365690960:AAH4KB5PMNnWQtfniVZrFllPsjYjNGScg2o'
ADMIN_ID = 8288404053
BOT_NAME = 'TELEGRAM BOT HOSTING'

# Directory setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BOTS_DIR = os.path.join(BASE_DIR, 'bots')
DATA_FILE = os.path.join(BASE_DIR, 'data.json')
TEMP_DIR = os.path.join(BASE_DIR, 'temp')

# Create directories
for dir_path in [BOTS_DIR, TEMP_DIR]:
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

# Initialize bot
bot = telebot.TeleBot(BOT_TOKEN)

# Load data
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {'users': [], 'bots': [], 'total_bots': 0, 'total_users': 0}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# Main menu keyboard
def main_keyboard():
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.row('🤖 NEW BOT', '📋 MY BOTS')
    keyboard.row('📊 STATS', '👤 PROFILE')
    keyboard.row('📢 CHANNEL', '❓ HELP')
    return keyboard

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    username = message.from_user.username or 'N/A'
    
    data = load_data()
    user_exists = False
    for user in data['users']:
        if user.get('user_id') == user_id:
            user_exists = True
            break
    
    if not user_exists:
        data['users'].append({
            'user_id': user_id,
            'name': first_name,
            'username': username,
            'joined': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'bots_count': 0
        })
        data['total_users'] = len(data['users'])
        save_data(data)
    
    user_bots = [bot for bot in data['bots'] if bot.get('user_id') == user_id]
    remaining = 10 - len(user_bots)
    
    msg = f"⭐ *Welcome, {first_name}!*\n\n"
    msg += f"### System Statistics\n"
    msg += f"- Total Users: {data['total_users']}\n"
    msg += f"- Total Bots: {data['total_bots']}\n"
    msg += f"- Active Bots: {len([b for b in data['bots'] if b.get('status') == 'running'])}\n"
    msg += f"- Version: 2.0.1\n\n"
    msg += f"### Your Statistics\n"
    msg += f"- Your Bots: {len(user_bots)}\n"
    msg += f"- Remaining: {remaining}\n\n"
    msg += f"Powered by @ASHUSHARMA_JIBOT"
    
    bot.send_message(message.chat.id, msg, parse_mode='Markdown', reply_markup=main_keyboard())

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    text = message.text
    data = load_data()
    
    if text == '🤖 NEW BOT':
        msg = "🔧 *DEPLOY NEW BOT*\n*Step 1/3 - Token*\n\nPlease send me your bot token:"
        bot.send_message(message.chat.id, msg, parse_mode='Markdown')
        
        session_file = os.path.join(TEMP_DIR, f"session_{user_id}.json")
        with open(session_file, 'w') as f:
            json.dump({'step': 'awaiting_token'}, f)
    
    elif text == '📋 MY BOTS':
        user_bots = [bot for bot in data['bots'] if bot.get('user_id') == user_id]
        
        if not user_bots:
            bot.send_message(message.chat.id, "📭 *No bots found!*\n\nUse '🤖 NEW BOT' to create one.", parse_mode='Markdown')
            return
        
        msg = f"📋 *YOUR BOTS*\nTotal: {len(user_bots)}\n\n"
        for i, bot_info in enumerate(user_bots, 1):
            status_emoji = "🟢" if bot_info['status'] == 'running' else "🔴"
            msg += f"### Bot {i}: {bot_info['name']}\n"
            msg += f"- Username: @{bot_info['username']}\n"
            msg += f"- Status: {status_emoji} {bot_info['status']}\n"
            msg += f"- Created: {bot_info['created']}\n\n"
        
        bot.send_message(message.chat.id, msg, parse_mode='Markdown')
    
    elif text == '📊 STATS':
        user_bots = [bot for bot in data['bots'] if bot.get('user_id') == user_id]
        active_bots = len([b for b in user_bots if b.get('status') == 'running'])
        
        msg = f"📊 *YOUR STATISTICS*\n\n"
        msg += f"👤 *User ID:* `{user_id}`\n"
        msg += f"🤖 *Total Bots:* {len(user_bots)}\n"
        msg += f"🟢 *Active Bots:* {active_bots}\n"
        msg += f"🔴 *Stopped Bots:* {len(user_bots) - active_bots}\n"
        msg += f"📈 *Remaining Slots:* {10 - len(user_bots)}\n\n"
        
        bot.send_message(message.chat.id, msg, parse_mode='Markdown', reply_markup=main_keyboard())
    
    elif text == '👤 PROFILE':
        user_data = next((u for u in data['users'] if u['user_id'] == user_id), None)
        user_bots = [bot for bot in data['bots'] if bot.get('user_id') == user_id]
        
        msg = f"👤 *PROFILE*\n\n"
        msg += f"📛 *Name:* {user_data['name'] if user_data else 'Unknown'}\n"
        msg += f"🆔 *User ID:* `{user_id}`\n"
        msg += f"🔗 *Username:* @{user_data['username'] if user_data else 'N/A'}\n"
        msg += f"🤖 *Bots Created:* {len(user_bots)}\n"
        msg += f"📅 *Joined:* {user_data['joined'] if user_data else 'Unknown'}\n\n"
        msg += f"💡 *Max Bots:* 10\n"
        msg += f"📊 *Remaining:* {10 - len(user_bots)}"
        
        bot.send_message(message.chat.id, msg, parse_mode='Markdown', reply_markup=main_keyboard())
    
    elif text == '📢 CHANNEL':
        msg = f"📢 *OUR CHANNELS*\n\n"
        msg += f"📡 *Updates Channel:* @ASHUSHARMA_JIBOT\n"
        msg += f"💬 *Support Group:* @RANDIAPEX\n\n"
        msg += f"Join our channels for updates and support!"
        
        bot.send_message(message.chat.id, msg, parse_mode='Markdown', reply_markup=main_keyboard())
    
    elif text == '❓ HELP':
        msg = f"❓ *HELP GUIDE*\n\n"
        msg += f"📌 *How to Deploy a Bot:*\n"
        msg += f"1. Click '🤖 NEW BOT'\n"
        msg += f"2. Send your bot token\n"
        msg += f"3. Upload your bot file (.php or .py)\n"
        msg += f"4. Bot will be deployed automatically\n\n"
        
        msg += f"📌 *Supported Files:*\n"
        msg += f"• PHP files (.php)\n"
        msg += f"• Python files (.py)\n"
        msg += f"• ZIP archives (auto-extract)\n\n"
        
        msg += f"📌 *Bot Management:*\n"
        msg += f"• Click '📋 MY BOTS' to see your bots\n"
        msg += f"• Start/Stop/Restart your bots\n"
        msg += f"• View logs and info\n"
        msg += f"• Delete bots when not needed\n\n"
        
        msg += f"📌 *Limits:*\n"
        msg += f"• Maximum 10 bots per user\n"
        msg += f"• File size limit: 10MB\n"
        msg += f"• 1 hour to upload after token\n\n"
        
        msg += f"📞 *Support:* @RANDIAPEX"
        
        bot.send_message(message.chat.id, msg, parse_mode='Markdown', reply_markup=main_keyboard())
    
    else:
        session_file = os.path.join(TEMP_DIR, f"session_{user_id}.json")
        if os.path.exists(session_file):
            with open(session_file, 'r') as f:
                session = json.load(f)
            
            if session.get('step') == 'awaiting_token':
                token = text.strip()
                if len(token) < 30:
                    bot.send_message(message.chat.id, "❌ *Invalid token!*", parse_mode='Markdown')
                    return
                
                session['token'] = token
                session['step'] = 'awaiting_file'
                with open(session_file, 'w') as f:
                    json.dump(session, f)
                
                try:
                    url = f"https://api.telegram.org/bot{token}/getMe"
                    response = requests.get(url)
                    bot_info = response.json()
                    
                    if bot_info.get('ok'):
                        bot_name = bot_info['result']['first_name']
                        bot_username = bot_info['result']['username']
                        
                        session['bot_name'] = bot_name
                        session['bot_username'] = bot_username
                        with open(session_file, 'w') as f:
                            json.dump(session, f)
                        
                        msg = f"✔ *TOKEN VERIFIED*\n*Step 2/3 - Upload*\n\n"
                        msg += f"**Bot Details:**\n"
                        msg += f"- Name: {bot_name}\n"
                        msg += f"- Username: @{bot_username}\n"
                        msg += f"- Token: {token[:10]}...\n\n"
                        msg += f"## Upload your bot file:\n"
                        msg += f"- Send .php or .py file\n"
                        msg += f"- Max size: 10MB\n\n"
                        msg += f"You have 1 hour to upload"
                        
                        bot.send_message(message.chat.id, msg, parse_mode='Markdown')
                    else:
                        bot.send_message(message.chat.id, "❌ *Invalid token!*", parse_mode='Markdown')
                        os.remove(session_file)
                except Exception as e:
                    bot.send_message(message.chat.id, f"❌ *Error: {str(e)}*", parse_mode='Markdown')
                    os.remove(session_file)

@bot.message_handler(content_types=['document'])
def handle_file(message):
    user_id = message.from_user.id
    session_file = os.path.join(TEMP_DIR, f"session_{user_id}.json")
    
    if not os.path.exists(session_file):
        return
    
    with open(session_file, 'r') as f:
        session = json.load(f)
    
    if session.get('step') != 'awaiting_file':
        return
    
    file_id = message.document.file_id
    file_name = message.document.file_name
    file_size = message.document.file_size
    
    if file_size > 10 * 1024 * 1024:
        bot.send_message(message.chat.id, "❌ *File too large!*", parse_mode='Markdown')
        return
    
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    
    temp_file = os.path.join(TEMP_DIR, file_name)
    with open(temp_file, 'wb') as f:
        f.write(downloaded_file)
    
    if file_name.endswith('.php'):
        file_type = 'php'
    elif file_name.endswith('.py'):
        file_type = 'python'
    else:
        bot.send_message(message.chat.id, "❌ *Unsupported file type!*", parse_mode='Markdown')
        os.remove(temp_file)
        return
    
    bot_id = f"bot_{int(time.time())}"
    bot_folder = os.path.join(BOTS_DIR, bot_id)
    os.makedirs(bot_folder, exist_ok=True)
    
    dest_path = os.path.join(bot_folder, file_name)
    shutil.copy2(temp_file, dest_path)
    
    bot_info = {
        'bot_id': bot_id,
        'token': session['token'],
        'username': session['bot_username'],
        'name': session['bot_name'],
        'file_path': dest_path,
        'file_type': file_type,
        'status': 'running',
        'created': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'user_id': user_id
    }
    
    data = load_data()
    data['bots'].append(bot_info)
    data['total_bots'] = len(data['bots'])
    save_data(data)
    
    msg = f"✔ *BOT DEPLOYED*\nSuccessfully!\n\n"
    msg += f"## Bot Details:\n"
    msg += f"- **Name:** {bot_info['name']}\n"
    msg += f"- **Username:** @{bot_info['username']}\n"
    msg += f"- **Status:** 🟢 Running\n"
    msg += f"- **File:** {file_name}\n\n"
    msg += f"Use '📋 MY BOTS' to manage your bot."
    
    bot.send_message(message.chat.id, msg, parse_mode='Markdown')
    
    os.remove(temp_file)
    session['step'] = 'completed'
    with open(session_file, 'w') as f:
        json.dump(session, f)
    time.sleep(5)
    os.remove(session_file)

if __name__ == '__main__':
    print(f"🤖 {BOT_NAME} is running...")
    bot.remove_webhook()
    time.sleep(1)
    bot.infinity_polling()
