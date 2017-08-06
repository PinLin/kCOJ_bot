#! /usr/bin/env python3

# necessary modules
import telepot, time, requests
from telepot.loop import MessageLoop
from pprint import pprint
# kCOJ API
import access
# configurations
import config

def on_chat(msg):
    pprint(msg)
    content_type, chat_type, chat_id = telepot.glance(msg)

    # me = users[str(chat_id)]
    me = users[config.DEBUG_ID] # for debug
    me.login()

    if (msg['text'] in me.list_questions()):
        content = me.show_question(msg['text'])
        bot.sendMessage(chat_id, '<code>' + content + '</code>', parse_mode='HTML')
    else:
        bot.sendMessage(chat_id, '```\n' + str(msg) + '\n```', parse_mode='Markdown')

users = {}
bot = telepot.Bot(config.TOKEN)
MessageLoop(bot, {'chat': on_chat}).run_as_thread()

# for debug
def main():
    users[config.DEBUG_ID] = access.kuser(config.DEBUG_USER, config.DEBUG_PSWD)

main()
while True:
    time.sleep(10)