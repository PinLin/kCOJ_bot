#! /usr/bin/env python3

# necessary modules
import time, requests, telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from pprint import pprint
# kCOJ API
import access
from interface import kuser
# configurations
import config

def on_chat(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    pprint(msg) # for debug
    print(content_type, chat_type, chat_id) # for debug

    # create a user object
    user = kuser(chat_id, bot)
    if str(chat_id) in users:
        user = users[str(chat_id)]
    else:
        users[str(chat_id)] = user

    if content_type == 'text':
        # pre-treat the command
        command = [msg['text']]
        if msg['text'][0] == '/':
            command = msg['text'].replace('_', ' ').lower().split(' ')

        # first-time user
        if user.status == '第一次用':
            user.new_user()

        # press password
        elif user.status == '輸入學號':
            user.press_password(msg['text'])

        # login
        elif user.status == '輸入密碼':
            user.login_kcoj(msg['text'])

        elif user.status == '舊的密碼':    
            if user.check_online() == True:
                user.press_newpassword(msg['text'])

        elif user.status == '修改密碼':
            if user.check_online() == True:
                user.change_password(msg['text'])

        elif command[0] == '/start' or command[0] == '重新整理🔃' or command[0] == '回主畫面🏠':
            if user.check_online() == True:
                user.display_main()

        elif command[0] == '/question' or command[0] == '查看題庫📝' or command[0] == '回到題庫📝' or command[0] == '重新載入🔃':
            if user.check_online() == True:
                if len(command) > 1:
                    user.display_question(command[1])
                else:
                    user.display_questions()

        elif command[0] == '/help' or command[0] == '提供幫助📚':
            if user.check_online() == True:
                user.help_you()

        elif command[0] == '/password' or command[0] == '修改密碼💱':
            if user.check_online() == True:
                user.press_oldpassword()

        elif command[0] == '/logout' or command[0] == '登出帳號🚪':
            user = kuser(chat_id, bot)
            users[str(chat_id)] = user
            user.logout_system()

    elif False:
        # receive a document
        pass

    else:
        bot.sendMessage(chat_id, "我不是來看這些的。")

users = {}
bot = telepot.Bot(config.TOKEN)
MessageLoop(bot, on_chat).run_as_thread()

# for debug
def main():
    pass

if __name__ == '__main__':
    main()
    while True:
        time.sleep(10)