#! /usr/bin/env python3

# necessary modules
import time, requests, telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
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
            bot.sendMessage(chat_id, "哇...登入失敗，讓我們重新開始一次", reply_markup=ReplyKeyboardRemove())
            time.sleep(0.6)
            bot.sendMessage(chat_id, "請輸入您的學號：", reply_markup=ReplyKeyboardRemove())
            return False
    def display_main(self, chat_id):
        self.status = 3
        q_list = self.api.list_questions()
        q_available = "📝<i>可繳交的作業</i>\n\n"
        q_unavailable = "📝<i>沒有可繳交的作業哦！</i>\n"
        if q_list == {}:
            q_str = q_unavailable
        else:
            q_str = q_available
            for key in q_list.keys():
                if q_list[key][1] == '期限未到':
                    q_str += "📗<b>" + key + "</b> (到 " + q_list[key][0] + ")\n [" + q_list[key][2] + "] /question_" + key + "\n\n"
            if q_str == q_available:
                q_str = q_unavailable
        bot.sendMessage(chat_id, "💁 <b>" + self.username + "</b> /logout\n"
                                 "➖➖➖➖➖\n" + q_str + "➖➖➖➖➖\n"
                                 "你今天寫扣了嗎？", parse_mode='HTML',
                                 reply_markup=ReplyKeyboardMarkup(keyboard=[
                                     [KeyboardButton(text="查看題庫📝"), KeyboardButton(text="重新整理🔃")],
                                     [KeyboardButton(text="登出帳號🚪"), KeyboardButton(text="提供幫助📚")]
                                 ]))
    def display_questions(self, chat_id):
        q_list = self.api.list_questions()
        q_str = ''
        for key in q_list.keys():
            if q_list[key][1] == '期限未到':
                q_str += "📗<b>" + key + "</b> (到 " + q_list[key][0] + ")\n [" + q_list[key][2] + "] /question_" + key + "\n\n"
            else:
                q_str += "📕<b>" + key + "</b> (到 " + q_list[key][0] + ")\n [" + q_list[key][2] + "] /question_" + key + "\n\n"
        bot.sendMessage(chat_id, "💁 <b>" + self.username + "</b> /logout\n"
                                 "➖➖➖➖➖\n"
                                 "📝<i>所有作業</i>\n\n" + q_str + 
                                 "➖➖➖➖➖\n"
                                 "你今天寫扣了嗎？", parse_mode='HTML',
                                 reply_markup=ReplyKeyboardMarkup(keyboard=[
                                     [KeyboardButton(text="回主畫面🏠"), KeyboardButton(text="重新載入🔃")],
                                     [KeyboardButton(text="登出帳號🚪"), KeyboardButton(text="提供幫助📚")]
                                 ]))
    def display_question(self, chat_id, number):
        content = self.api.show_question(number)
        q = self.api.list_questions()[number]
        q_str = "📗" if q[1] == '期限未到' else "📕"
        q_str += "<b>" + number + "</b> (到 " + q[0] + ")"
        bot.sendMessage(chat_id, q_str + "\n<code>" + content + "</code>\n" + q_str,
                         parse_mode='HTML',
                         reply_markup=ReplyKeyboardMarkup(keyboard=[
                                     [KeyboardButton(text="回主畫面🏠"), KeyboardButton(text="回到題庫📝")],
                                     [KeyboardButton(text="上傳解答📮"), KeyboardButton(text="查看結果☑️"), KeyboardButton(text="通過名單🌐")] if q[1] == '期限未到' else 
                                     [KeyboardButton(text="查看結果☑️"), KeyboardButton(text="通過名單🌐")],
                                     [KeyboardButton(text="登出帳號🚪"), KeyboardButton(text="提供幫助📚")]
                         ]))

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
        elif command[0] == '/start' or command[0] == '重新整理🔃' or command[0] == '回主畫面🏠':
            if me.status == 0:
                me.status = 1
                bot.sendMessage(chat_id, "是初次見面的朋友呢，設定一下吧！", reply_markup=ReplyKeyboardRemove())
                time.sleep(0.6)
                bot.sendMessage(chat_id, "請輸入您的學號：", reply_markup=ReplyKeyboardRemove())
            else:
                if me.test_login(chat_id) == True:
                    me.display_main(chat_id)
        elif command[0] == '/question' or command[0] == '查看題庫📝' or command[0] == '重新載入🔃' or command[0] == '回到題庫📝':
            if me.test_login(chat_id) == True:
                if len(command) > 1:
                    me.display_question(chat_id, command[1])
                else:
                    me.display_questions(chat_id)
        elif command[0] == '/help' or command[0] == '提供幫助📚':
            pass
        elif command[0] == '/logout' or command[0] == '登出帳號🚪':
            bot.sendMessage(chat_id, "您現在已經是登出的狀態。", reply_markup=ReplyKeyboardRemove())
            me = kuser()
            me.status = 1
            users[str(chat_id)] = me
            time.sleep(0.6)
            bot.sendMessage(chat_id, "請輸入您的學號：", reply_markup=ReplyKeyboardRemove())

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