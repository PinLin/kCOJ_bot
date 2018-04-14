#! /usr/bin/env python3

# modules
import os
import time
import json
from pprint import pprint
import telepot
from telepot.loop import MessageLoop
# config
from config import NAME, TOKEN, ADMIN
from interface import Kuser

bot = telepot.Bot(TOKEN)
users = {}

def on_chat(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    from_id = msg['from']['id']

    # debug message
    pprint(msg)
    print('content_type:', content_type)
    print('chat_type:', chat_type)
    print('chat_id:', chat_id)
    print('from_id:', from_id)
    print()

    # create a user object
    user = Kuser(from_id)
    if str(from_id) in users:
        user = users[str(from_id)]
    else:
        users[str(from_id)] = user

    # just want to know
    print('student_id:', user._username)

    if content_type == 'text':
        # pre-treat the command
        command = [msg['text']]
        if msg['text'].startswith('/'):
            command = msg['text'].replace(NAME, '').replace('_', ' ').lower().split(' ')

        # restart this bot
        if command[0] == '/restart' and str(from_id) in ADMIN:
            bot.sendMessage(chat_id, "即將更新並重新啟動")
            print("Restarting...")
            backup_db()
            time.sleep(1)
            os._exit(0)

        # test connection
        elif command[0] == '/ping':
            bot.sendMessage(chat_id, "*PONG*",
            parse_mode='Markdown',
            reply_to_message_id=msg['message_id'])

        # help message
        elif command[0] == '/help' or command[0] == '幫助📚':
            if chat_type == 'private':
                user.help()

        # first-time user
        elif user._status == '第一次用':
            if chat_type == 'private':
                user.new_user()

        # press password
        elif user._status == '輸入學號':
            if chat_type == 'private':
                user.press_password(msg['text'])

        # login
        elif user._status == '輸入密碼':
            if chat_type == 'private':
                user.login(msg['text'])

        # homepage
        elif command[0] == '/start' or command[0] == '首頁🏠':
            if user.check_online(chat_id, msg['message_id']) == True:
                user.show_homepage(chat_id)

        elif command[0] == '/question' or command[0] == '題庫📝' or command[0] == '更新🔃':
            if user.check_online(chat_id, msg['message_id']) == True:
                if len(command) > 1:
                    user.show_question(command[1], chat_id)
                else:
                    user.list_questions(chat_id)

        elif chat_type == 'private':
            if command[0] == '/password' or command[0] == '改密碼💱':
                if user.check_online(chat_id, msg['message_id']) == True:
                    user.press_oldpassword()

            elif command[0] == '/logout' or command[0] == '登出🚪':
                user = Kuser(from_id)
                users[str(from_id)] = user
                user.logout()

            elif (command[0] == '/delete' or command[0] == '刪除作業⚔️') and user._question != '題外':
                if user.check_online(chat_id, msg['message_id']) == True:
                    user.delete_answer()

            elif (command[0] == '/upload' or command[0] == '交作業📮') and user._question != '題外':
                if user.check_online(chat_id, msg['message_id']) == True:
                    user.upload_answer()

            elif (command[0] == '/result' or command[0] == '看結果☑️') and user._question != '題外':
                if user.check_online(chat_id, msg['message_id']) == True:
                    user.list_results()

            elif (command[0] == '/passer' or command[0] == '通過者🌐') and user._question != '題外':
                if user.check_online(chat_id, msg['message_id']) == True:
                    user.list_passers()

            elif command[0] == '回題目📜' and user._question != '題外':
                if user.check_online(chat_id, msg['message_id']) == True:
                    user.show_question(user._question, chat_id)

            elif user._status == '舊的密碼':
                if user.check_online(chat_id, msg['message_id']) == True:
                    user.press_newpassword(msg['text'])

            elif user._status == '修改密碼':
                if user.check_online(chat_id, msg['message_id']) == True:
                    user.change_password(msg['text'])

            elif user._status == '上傳答案':
                if user.check_online(chat_id, msg['message_id']) == True:
                    user.send_answer(msg['text'], '', user.list_questions(chat_id)[user._question][3])

            else:
                if user.check_online(chat_id, msg['message_id']) == True:
                    bot.sendMessage(chat_id, "(ˊ・ω・ˋ)")
            
    elif content_type == 'document':
        if user._status == '上傳答案' or user._status == '查看題目':
            if user.check_online(chat_id, msg['message_id']) == True:
                if msg['document']['file_size'] > 167770000:
                    user.send_failed()
                else:
                    user.send_answer('', msg['document']['file_id'], user.list_questions(chat_id)[user._question][3])

def backup_db():
    users_backup = {}
    for key in users.keys():
        user = users[key]
        users_backup[key] = {
            'userid': user._userid,
            'username': user._username,
            'password': user._password,
            'status': user._status,
            'question': user._question
        }
    with open('users.json', 'w') as f:
        json.dump(users_backup, f, indent='  ')

def restore_db():
    with open('users.json', 'r') as f:
        users_restore = json.load(f)
        for key in users_restore.keys():
            user = users_restore[key]
            users[key] = Kuser(user['userid'], user['username'], user['password'], user['status'], user['question'])

# restore
restore_db()

# start this bot
MessageLoop(bot, on_chat).run_as_thread()
print("Started! Service is available.")

while True:
    time.sleep(60)

    # keep bot alive
    bot.getMe()

    # backup
    backup_db()