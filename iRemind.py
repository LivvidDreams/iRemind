import sqlite3
import os
import time
import re
import threading
import subprocess

DB_PATH = os.path.expanduser('~/Library/Messages/chat.db')

def connect_db():
    conn = sqlite3.connect(DB_PATH)
    return conn

def get_new_messages(processed_ids):
    conn = connect_db()
    cursor = conn.cursor()
    query = """
    SELECT 
        message.rowid, 
        message.text, 
        chat.chat_identifier AS chat_id
    FROM 
        message
    JOIN 
        chat_message_join ON message.rowid = chat_message_join.message_id
    JOIN 
        chat ON chat_message_join.chat_id = chat.rowid
    WHERE 
        message.is_from_me = 1
    ORDER BY 
        message.date DESC
    LIMIT 50;
    """
    cursor.execute(query)
    messages = cursor.fetchall()
    conn.close()

    new_messages = []
    for msg_id, text, chat_id in messages:
        try:
            if msg_id not in processed_ids and '!remindme' in text.lower():
                new_messages.append((msg_id, text, chat_id))
                processed_ids.add(msg_id)
        except:
            continue
    return new_messages

def parse_time_interval(message):
    pattern = r"!remindme\s+(\d+)\s*(h|hr|hrs|hour|hours|m|min|mins|minute|minutes)"
    match = re.search(pattern, message.lower())
    if match:
        value = int(match.group(1))
        unit = match.group(2)
        if unit.startswith('h'):
            return value * 3600  # Convert hours to seconds
        elif unit.startswith('m'):
            return value * 60    # Convert minutes to seconds
    return None

def send_reminder(chat_id):
    applescript = f'''
    tell application "Messages"
        set targetChat to first chat whose id contains "{chat_id}"
        send "Reminder!" to targetChat
    end tell
    '''
    result = subprocess.run(['osascript', '-e', applescript], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error sending reminder: {result.stderr}")
    else:
        print(f"Reminder sent to chat_id: {chat_id}")

def schedule_reminder(delay, chat_id):
    threading.Timer(delay, send_reminder, args=(chat_id,)).start()

def main():
    processed_ids = set()
    while True:
        new_messages = get_new_messages(processed_ids)
        print("Messages set: ", new_messages)
        for msg_id, text, chat_id in new_messages:
            delay = parse_time_interval(text)
            if delay:
                print(f"handle new msg -- {delay} for {msg_id} {chat_id} {text}")
                schedule_reminder(delay, chat_id)
        time.sleep(30)

if __name__ == '__main__':
    main()
