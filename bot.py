#! /usr/bin/env python3

# necessary modules
import os, time, requests, telepot
from telepot.loop import MessageLoop
from pprint import pprint
# kCOJ API
import access
from interface import kuser
# configurations
import config

users = {}
bot = telepot.Bot(config.TOKEN)

def on_chat(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    from_id = msg['from']['id'] 
    pprint(msg) # for debug
    print('content_type:', content_type) # for debug
    print('chat_type:', chat_type) # for debug
    print('chat_id:', chat_id) # for debug
    print('from_id:', from_id) # for debug
    print() # for debug

    # create a user object
    user = kuser(from_id, bot)
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

        elif user.status == '舊的密碼' and chat_type == 'private':
            if user.check_online() == True:
                user.press_newpassword(msg['text'])

        elif user.status == '修改密碼' and chat_type == 'private':
            if user.check_online() == True:
                user.change_password(msg['text'])

        elif user.status == '上傳答案' and chat_type == 'private':
            if user.check_online() == True:
                user.send_answer(msg['text'], '')
        
        elif command[0] == '/start' or command[0] == '首頁🏠':
            if user.check_online() == True:
                user.display_main(chat_id)

        elif command[0] == '/question' or command[0] == '題庫📝' or command[0] == '更新🔃':
            if user.check_online() == True:
                if len(command) > 1:
                    user.display_question(chat_id, command[1])
                else:
                    user.display_questions(chat_id)

        elif command[0] == '/restart':
            if str(from_id) in config.ADMIN:
                bot.sendMessage(chat_id, "即將更新並重新啟動")
                print("Restarting...")
                time.sleep(1)
                os._exit(0)

        elif (command[0] == '/help' or command[0] == '幫助📚') and chat_type == 'private':
            if user.check_online() == True:
                user.help_you()

        elif (command[0] == '/password' or command[0] == '改密碼💱') and chat_type == 'private':
            if user.check_online() == True:
                user.press_oldpassword()

        elif (command[0] == '/logout' or command[0] == '登出🚪') and chat_type == 'private':
            user = kuser(from_id, bot)
            users[str(from_id)] = user
            user.logout_system()

        elif user.question != '題外':
            if user.check_online() == True:
                if (command[0] == '/upload' or command[0] == '交作業📮') and chat_type == 'private':
                    user.upload_answer()
                elif (command[0] == '/result' or command[0] == '看結果☑️') and chat_type == 'private':
                    user.list_results()
                elif (command[0] == '/passer' or command[0] == '通過者🌐') and chat_type == 'private':
                    user.list_passers()
                elif command[0] == '回題目📜':
                    user.display_question(chat_id ,user.question)
        else:
            if chat_type == 'private':
                bot.sendMessage(chat_id, "(ˊ・ω・ˋ)")
            
    elif content_type == 'document':
        if user.status == '上傳答案' or user.status == '查看題目':
            if user.check_online() == True:
                if msg['document']['file_size'] > 167770000:
                    user.fail_send()
                else:
                    user.send_answer('', msg['document']['file_id'])

MessageLoop(bot, on_chat).run_as_thread()
print("Started! Service is available.")
while True:
    time.sleep(1)
    bot.getMe()