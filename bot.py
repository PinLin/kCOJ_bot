#! /usr/bin/env python3

# necessary modules
import time, requests, telepot
from telepot.loop import MessageLoop
from pprint import pprint
# kCOJ API
import access
# configurations
import config

users = {}
class kuser:
    def __init__(self, un='', pw='', st=0):
        self.username = un
        self.password = pw
        self.status = st
        self.api = access.kuser_api()

    def test_login(self, chat_id):
        self.api.login(self.username, self.password)
        if self.api.check_online() == True:
            return True
        else:
            self.status = 1
            bot.sendMessage(chat_id, "哇...登入失敗，讓我們重新開始一次")
            time.sleep(0.6)
            bot.sendMessage(chat_id, "請輸入您的學號：")
            return False
    def display_main(self, chat_id):
        self.status = 3
        q_list = self.api.list_questions()
        q_available = "📝<i>可繳交的作業</i>\n"
        q_unavailable = "📝<i>沒有可繳交的作業哦！</i>\n"
        if q_list == {}:
            q_str = q_unavailable
        else:
            q_str = q_available
            for key in q_list.keys():
                if q_list[key][1] == '期限未到':
                    q_str += "第 <b>" + key + "</b> 題到 <b>" + q_list[key][0] + "</b>\n/question_" + key + "\n"
            if q_str == q_available:
                q_str = q_unavailable
        bot.sendMessage(chat_id, "💁 <b>" + self.username + "</b> /logout\n"
                                 "➖➖➖➖➖\n" + q_str + "➖➖➖➖➖\n"
                                 "你今天寫扣了嗎？", parse_mode='HTML')


def split_cmd(text):
    if text[0] != '/':
        return [text]
    else:
        cmd = text.replace('_', ' ').strip().lower().split(' ')
        return cmd


def on_chat(msg):
    pprint(msg)
    content_type, chat_type, chat_id = telepot.glance(msg)
    print(content_type, chat_type, chat_id)

    me = kuser()
    if str(chat_id) in users:
        me = users[str(chat_id)]
    else:
        users[str(chat_id)] = me

    if content_type == 'text':
        command = split_cmd(msg['text'])

        if me.status == 1:
            me.status = 2
            me.username = msg['text']
            bot.sendMessage(chat_id, "請輸入您的密碼：")
        elif me.status == 2:
            me.password = msg['text']
            bot.sendMessage(chat_id, "登入中...")
            if me.test_login(chat_id) == True:
                me.display_main(chat_id)
        elif command[0] == '/start':
            if me.status == 0:
                me.status = 1
                bot.sendMessage(chat_id, "是初次見面的朋友呢，設定一下吧！\n")
                time.sleep(0.6)
                bot.sendMessage(chat_id, "請輸入您的學號：")
            else:
                if me.test_login(chat_id) == True:
                    me.display_main(chat_id)

    else:
        bot.sendMessage(chat_id, "我不是來看這些的。")

bot = telepot.Bot(config.TOKEN)
MessageLoop(bot, on_chat).run_as_thread()

# for debug
def main():
    pass
    # over 20MB will stop this bot!
    # bot.download_file('BQADBQADHQADPAc5VEZQejGkM9C4Ag', '../wa.txt')
main()

while True:
    time.sleep(10)