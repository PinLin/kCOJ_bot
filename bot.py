#! /usr/bin/env python3

# necessary modules
import os, time, json, requests, telepot
from telepot.loop import MessageLoop
from pprint import pprint
# kCOJ API
import access
from interface import kuser, bot
# configurations
import config

users = {}

def on_chat(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    from_id = msg['from']['id'] 
    pprint(msg)
    print('content_type:', content_type)
    print('chat_type:', chat_type)
    print('chat_id:', chat_id)
    print('from_id:', from_id)
    print()

    # create a user object
    user = kuser(from_id)
    if str(from_id) in users:
        user = users[str(from_id)]
    else:
        users[str(from_id)] = user

    if content_type == 'text':
        # pre-treat the command
        command = [msg['text']]
        if msg['text'][0] == '/':
            command = msg['text'].replace(config.NAME, '').replace('_', ' ').lower().split(' ')

        # first-time user
        if user.status == '第一次用':
            if chat_type == 'private':
                user.new_user()
            else:
                bot.sendMessage(chat_id, "請先私訊我登入 kCOJ", reply_to_message_id=msg['message_id'])

        # press password
        elif user.status == '輸入學號':
            if chat_type == 'private':
                user.press_password(msg['text'])
            else:
                bot.sendMessage(chat_id, "請先私訊我登入 kCOJ", reply_to_message_id=msg['message_id'])

        # login
        elif user.status == '輸入密碼':
            if chat_type == 'private':
                user.login_kcoj(msg['text'])
            else:
                bot.sendMessage(chat_id, "請先私訊我登入 kCOJ", reply_to_message_id=msg['message_id'])

        elif command[0] == '/start' or command[0] == '首頁🏠':
            if user.check_online(chat_id, msg['message_id']) == True:
                user.display_main(chat_id)

        elif command[0] == '/question' or command[0] == '題庫📝' or command[0] == '更新🔃':
            if user.check_online(chat_id, msg['message_id']) == True:
                if len(command) > 1:
                    user.display_question(command[1], chat_id)
                else:
                    user.display_questions(chat_id)

        elif command[0] == '/restart':
            if str(from_id) in config.ADMIN:
                bot.sendMessage(chat_id, "即將更新並重新啟動")
                print("Restarting...")
                time.sleep(1)
                os._exit(0)

        elif command[0] == '/ping':
            bot.sendMessage(chat_id, "*PONG*",
            parse_mode='Markdown',
            reply_to_message_id=msg['message_id'])

        elif chat_type == 'private':
            if command[0] == '/help' or command[0] == '幫助📚':
                if user.check_online(chat_id, msg['message_id']) == True:
                    user.help_you()

            elif command[0] == '/password' or command[0] == '改密碼💱':
                if user.check_online(chat_id, msg['message_id']) == True:
                    user.press_oldpassword()

            elif command[0] == '/logout' or command[0] == '登出🚪':
                user = kuser(from_id)
                users[str(from_id)] = user
                user.logout_system()

            elif (command[0] == '/delete' or command[0] == '刪除作業⚔️') and user.question != '題外':
                if user.check_online(chat_id, msg['message_id']) == True:
                    user.delete_answer()

            elif (command[0] == '/upload' or command[0] == '交作業📮') and user.question != '題外':
                if user.check_online(chat_id, msg['message_id']) == True:
                    user.upload_answer()

            elif (command[0] == '/result' or command[0] == '看結果☑️') and user.question != '題外':
                if user.check_online(chat_id, msg['message_id']) == True:
                    user.list_results()

            elif (command[0] == '/passer' or command[0] == '通過者🌐') and user.question != '題外':
                if user.check_online(chat_id, msg['message_id']) == True:
                    user.list_passers()

            elif command[0] == '回題目📜' and user.question != '題外':
                if user.check_online(chat_id, msg['message_id']) == True:
                    user.display_question(user.question, chat_id)

            elif user.status == '舊的密碼':
                if user.check_online(chat_id, msg['message_id']) == True:
                    user.press_newpassword(msg['text'])

            elif user.status == '修改密碼':
                if user.check_online(chat_id, msg['message_id']) == True:
                    user.change_password(msg['text'])

            elif user.status == '上傳答案':
                if user.check_online(chat_id, msg['message_id']) == True:
                    user.send_answer(msg['text'], '')

            else:
                if user.check_online(chat_id, msg['message_id']) == True:
                    bot.sendMessage(chat_id, "(ˊ・ω・ˋ)")
            
    elif content_type == 'document':
        if user.status == '上傳答案' or user.status == '查看題目':
            if user.check_online(chat_id, msg['message_id']) == True:
                if msg['document']['file_size'] > 167770000:
                    user.fail_send()
                else:
                    user.send_answer('', msg['document']['file_id'])

# restore
with open('users.json', 'r') as f:
    users_restore = json.load(f)
    for key in users_restore.keys():
        user = users_restore[key]
        users[key] = kuser(user['userid'], user['username'], user['password'], user['status'], user['question'])

MessageLoop(bot, on_chat).run_as_thread()
print("Started! Service is available.")
count = 0
while True:
    time.sleep(1)
    count += 1
    if count == 5:
        bot.getMe()
        count = 0

    # backup
    users_backup = {}
    for key in users.keys():
        user = users[key]
        users_backup[key] = {
            'userid': user.userid,
            'username': user.username,
            'password': user.password,
            'status': user.status,
            'question': user.question
        }
    with open('users.json', 'w') as f:
        json.dump(users_backup, f)