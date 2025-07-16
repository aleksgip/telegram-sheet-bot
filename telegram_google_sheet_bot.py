import gspread
from oauth2client.service_account import ServiceAccountCredentials
import telegram
import json
import time
from datetime import datetime
import pytz
import os

# Настройки
BOT_TOKEN = '7842166940:AAEnemYzw-8XnrW-y0RP9vMXdKBr0ADo6Ig'
CHAT_ID = None
SPREADSHEET_URL = 'https://docs.google.com/spreadsheets/d/1yIMg98s97dN0H_qDeKPewEx4cOka4ANe5mBaTGjyxPk/edit'
RECORD_FILE = 'last_row.txt'
CHECK_HOUR_MSK = 9

bot = telegram.Bot(token=BOT_TOKEN)

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('service_account.json', scope)
client = gspread.authorize(creds)

def get_current_row_count():
    sheet = client.open_by_url(SPREADSHEET_URL).sheet1
    records = sheet.get_all_values()
    return len(records)

def read_last_row():
    if not os.path.exists(RECORD_FILE):
        return 0
    with open(RECORD_FILE, 'r') as f:
        return int(f.read().strip())

def write_last_row(n):
    with open(RECORD_FILE, 'w') as f:
        f.write(str(n))

def send_update(new_rows, first_new_row):
    message = f'Появилось {new_rows} заказчиков, начиная с {first_new_row} строки.'
    if CHAT_ID:
        bot.send_message(chat_id=CHAT_ID, text=message)
    else:
        updates = bot.get_updates()
        if updates:
            chat_id = updates[-1].message.chat.id
            bot.send_message(chat_id=chat_id, text=message)

def main():
    tz = pytz.timezone('Europe/Moscow')
    while True:
        now = datetime.now(tz)
        if now.hour == CHECK_HOUR_MSK and now.minute == 0:
            try:
                current = get_current_row_count()
                last = read_last_row()
                if current > last:
                    send_update(current - last, last + 1)
                    write_last_row(current)
            except Exception as e:
                print(f"Ошибка: {e}")
            time.sleep(60)
        time.sleep(20)

if __name__ == '__main__':
    main()