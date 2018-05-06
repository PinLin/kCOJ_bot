#! /usr/bin/env python3

# modules
import os
import sys
import time
import json
from random import choice
from pprint import pprint
import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import ReplyKeyboardMarkup, ReplyKeyboardRemove
# config
from config import NAME, URL, TOKEN
from kcoj import KCOJ
import promote
import external

bot = telepot.Bot(TOKEN)
users = {}

class Kuser:
    def __init__(self, userid, username='', password='', status='第一次用', question='題外'):
        self._userid = userid
        self._username = username
        self._password = password
        self._status = status
        self._question = question
        self._api = KCOJ(URL)

    def new_user(self):
        self.help()
        self.press_username()
    
    def press_username(self):
        self._status = '輸入學號'
        self._question = '題外'
        bot.sendMessage(self._userid, "請輸入您的學號：", reply_markup=ReplyKeyboardRemove())

    def press_password(self, text):
        self._status = '輸入密碼'
        self._question = '題外'
        self._username = text
        bot.sendMessage(self._userid, "輸入完可刪除訊息以策安全！\n"
                                     "請輸入您的密碼：", reply_markup=ReplyKeyboardRemove())

    def press_oldpassword(self):
        self._status = '舊的密碼'
        self._question = '題外'
        bot.sendMessage(self._userid, "請輸入要原本的舊密碼：",
            reply_markup=ReplyKeyboardMarkup(keyboard=[
                ["首頁🏠"]
            ], resize_keyboard=True))

    def press_newpassword(self, text):
        if text != self._password:
            self._status = '正常使用'
            self._question = '題外'
            bot.sendMessage(self._userid, "密碼錯誤！",
                reply_markup=ReplyKeyboardMarkup(keyboard=[
                    ["首頁🏠"]
                ], resize_keyboard=True))
        else:
            self._status = '修改密碼'
            self._question = '題外'
            bot.sendMessage(self._userid, "使用此功能請務必小心！\n"
                                         "請輸入要設定的新密碼：",
                reply_markup=ReplyKeyboardMarkup(keyboard=[
                    ["首頁🏠"]
                ], resize_keyboard=True))
        
    def change_password(self, text):
        self._status = '正常使用'
        self._question = '題外'
        self._password = text
        bot.sendMessage(self._userid, "修改成功！" if self._api.change_password(self._password) == True else "修改失敗。",
            reply_markup=ReplyKeyboardMarkup(keyboard=[
                ["首頁🏠"]
            ], resize_keyboard=True))

    def login(self, text):
        self._status = '正常使用'
        self._question = '題外'
        self._password = text
        bot.sendMessage(self._userid, "登入中...", reply_markup=ReplyKeyboardRemove())
        if self.check_online(self._userid) == True:
            self.show_homepage(self._userid)

    def login_failed(self, chat_id, message_id):
        self._status = '正常使用'
        self._question = '題外'
        if chat_id != self._userid:
            bot.sendMessage(chat_id, "登入失敗，請先私訊我重新登入 KCOJ", reply_to_message_id=message_id)
        bot.sendMessage(self._userid, "哇...登入失敗，讓我們重新開始", reply_markup=ReplyKeyboardRemove())
        self.press_username()
        
    def connect_failed(self, chat_id, message_id):
        self._status = '正常使用'
        self._question = '題外'
        if chat_id != self._userid:
            bot.sendMessage(chat_id, "KCOJ 離線中！請稍後再試", reply_to_message_id=message_id)
        else:
            bot.sendMessage(self._userid, "KCOJ 離線中！請稍後再試",
                reply_markup=ReplyKeyboardMarkup(keyboard=[
                    ["首頁🏠", "幫助📚"]
                ], resize_keyboard=True))

    def check_online(self, chat_id, message_id=''):
        result = self._api.check_online()
        if result == None:
            self.connect_failed(chat_id, message_id)
            return False
        else:
            if result == False:
                self._api.login(self._username, self._password, 2)
                result = self._api.check_online()
            if result == False:
                self.login_failed(chat_id, message_id)
            elif result == None:
                self.connect_failed(chat_id, message_id)
            return result == True

    def logout(self):
        self._status = '正常使用'
        self._question = '題外'
        bot.sendMessage(self._userid, "您現在已經是登出的狀態。", reply_markup=ReplyKeyboardRemove())
        self.press_username()

    def show_homepage(self, chat_id):
        self._status = '正常使用'
        self._question = '題外'
        q_dict = self._api.list_questions()
        q_str = ''
        for key in q_dict.keys():
            if q_dict[key][1] == '期限未到':
                q_str += "📗<b>" + key + "</b> (DL: " + q_dict[key][0] + ")\n [[" + q_dict[key][3] + "]] [[" + q_dict[key][2] + "]]"
                q_str += "⚠️" if q_dict[key][2] == '未繳' else "✅"
                q_str += "  /question_" + key + "\n\n"
        bot.sendMessage(chat_id, "💁 <b>" + self._username + "</b> " + NAME + "\n"
                                 "➖➖➖➖➖\n"
                                 "📝<i>可繳交的作業</i>\n\n" + q_str + \
                                 "➖➖➖➖➖\n" + choice(promote.sentences),
                                 parse_mode='HTML',
                                 reply_markup=ReplyKeyboardMarkup(keyboard=[
                                     ["題庫📝"],
                                     ["登出🚪", "改密碼💱", "幫助📚"]
                                 ], resize_keyboard=True) if chat_id == self._userid else ReplyKeyboardRemove(),
                                 disable_web_page_preview=False)

    def list_questions(self, chat_id):
        self._status = '正常使用'
        self._question = '題外'
        q_dict = self._api.list_questions()
        q_str = ''
        for key in q_dict.keys():
            q_str += "📗" if q_dict[key][1] == '期限未到' else "📕"
            q_str += "<b>" + key + "</b> (DL: " + q_dict[key][0] + ")\n [[" + q_dict[key][3] + "]] [[" + q_dict[key][2] + "]]"
            q_str += "⚠️" if q_dict[key][2] == '未繳' else "✅"
            q_str += "  /question_" + key + "\n\n"
        reply = bot.sendMessage(chat_id, "💁 <b>" + self._username + "</b> " + NAME + "\n"
                                         "➖➖➖➖➖\n"
                                         "📝<i>所有作業</i>\n\n" + q_str + \
                                         "➖➖➖➖➖\n" + choice(promote.sentences),
                                         parse_mode='HTML',
                                         reply_markup=ReplyKeyboardMarkup(keyboard=[
                                             ["首頁🏠", "更新🔃"],
                                             ["登出🚪", "改密碼💱", "幫助📚"]
                                         ], resize_keyboard=True) if chat_id == self._userid else ReplyKeyboardRemove(),
                                         disable_web_page_preview=False)
        bot.sendMessage(chat_id, "點我到題庫頂", reply_to_message_id=reply['message_id'])

    def show_question(self, number, chat_id):
        self._status = '查看題目'
        self._question = number
        if number in external.QUESTION:
            ext_q = True
            content = external.QUESTION[number]
        else:
            ext_q = False
            content = '```\n' + self._api.show_question(number) + '\n```'
        q = self._api.list_questions()[number]
        q_str = "💁 *" + self._username + "* [" + NAME + "]\n"
        q_str += "➖➖➖➖➖\n"
        q_str += "📗" if q[1] == '期限未到' else "📕"
        q_str += "*" + number + "* (DL: " + q[0] + ")\n [[[" + q[3] + "]]] [[[" + q[2] + "]]]"
        q_str += "⚠️" if q[2] == '未繳' else "✅"
        reply = bot.sendMessage(chat_id, q_str + "\n\n" + content,
            parse_mode='Markdown',
            reply_markup=ReplyKeyboardMarkup(keyboard=[
                ["首頁🏠", "題庫📝"],
                ["交作業📮" if q[1] == '期限未到' else '', "看結果☑️" if q[2] == '已繳' else '', "通過者🌐"],
                ["登出🚪", "改密碼💱", "幫助📚"]
            ], resize_keyboard=True) if chat_id == self._userid else ReplyKeyboardRemove())
        if ext_q == False:
            bot.sendMessage(chat_id, "點我到題目頂", reply_to_message_id=reply['message_id'])

    def help(self):
        bot.sendMessage(self._userid, "這裡是 Kuo C Online Judge Bot！\n"
                                     "可以簡稱 KCOJ Bot，目前定居於 [" + NAME + "]\n"
                                     "作用是讓大家可以方便的透過我使用郭老程設課的 Online Judge\n"
                                     "➡️[OJ 傳送門](" + URL + ")\n"
                                     "操作很簡單（？）\n\n"
                                     "還是稍微提幾個需要注意的地方：\n"
                                     "1. 📗代表還可以繳交的作業，📕代表已經不能繳交的作業\n"
                                     "2. ⚠️代表還沒有繳交的作業，✅代表已經繳交的作業\n"
                                     "3. 其實在查看題目的畫面就可以用「拖曳」的方式 *上傳作業📮*\n"
                                     "4. *刪除作業⚔️* 的功能被放在 *上傳作業📮* 裡面\n"
                                     "5. 學號與密碼將以「明文」方式儲存\n"
                                     "6. 郭老的 Online Judge 其實也是以「明文」方式儲存您的帳號密碼\n"
                                     "7. 我以我的人格擔保，不會使用您提供的資訊侵害您的權利\n\n"
                                     "本專案採用 *MIT License*\n"
                                     "聯絡我請私訊 @PinLin\n"
                                     "原始碼被託管於 GitHub，如果想要鼓勵我的話可以幫我按個星星> </\n"
                                     "網址如下：\n"
                                     "[https://github.com/PinLin/KCOJ_bot]\n\n",
                                     parse_mode='Markdown')

    def upload_answer(self):
        self._status = '上傳答案'
        q = self._api.list_questions()[self._question]
        q_str = "💁 <b>" + self._username + "</b> " + NAME + "\n"
        q_str += "➖➖➖➖➖\n"
        q_str += "📗" if q[1] == '期限未到' else "📕"
        q_str += "<b>" + self._question + "</b> (DL: " + q[0] + ")\n [[" + q[3] + "]] [[" + q[2] + "]]"
        q_str += "⚠️" if q[2] == '未繳' else "✅"
        bot.sendMessage(self._userid, q_str + "\n\n現在請把你的程式碼讓我看看（請別超過 20 MB）\n"
                                             "可以使用「文字訊息」或是「傳送檔案」的方式\n"
                                             "（注意：可在程式碼前後加上單獨成行的 ``` 避免可能的錯誤。）", parse_mode='HTML',
                                             reply_markup=ReplyKeyboardMarkup(keyboard=[
                                                 ["刪除作業⚔️"] if self._api.list_questions()[self._question][2] == '已繳' else [],
                                                 ["首頁🏠", "回題目📜"]
                                             ], resize_keyboard=True))

    def send_answer(self, text, file_id):
        self._status = '正常使用'
        # define filename
        filename = sys.path[0] + '/' + self._username + self._question
        if self._api.list_questions()[self._question][3] == 'Python':
            filename += '.py'
        else:
            filename += '.c'

        if text != '':
            with open(filename, 'w') as f:
                f.write(text)
        else:
            bot.download_file(file_id, filename)
        self._api.delete_answer(self._question)
        if self._api.upload_answer(self._question, filename) == True:
            bot.sendMessage(self._userid, "上傳成功",
                reply_markup=ReplyKeyboardMarkup(keyboard=[
                    ["首頁🏠", "回題目📜"],
                    ["看結果☑️"],
                    ["登出🚪", "改密碼💱", "幫助📚"]
                ], resize_keyboard=True))
        else:
            bot.sendMessage(self._userid, "上傳失敗",
                reply_markup=ReplyKeyboardMarkup(keyboard=[
                    ["首頁🏠", "回題目📜"],
                    ["登出🚪", "改密碼💱", "幫助📚"]
                ], resize_keyboard=True))
        os.remove(filename)    
    
    def delete_answer(self):
        bot.sendMessage(self._userid, "移除成功" if self._api.delete_answer(self._question) == True else "移除失敗",
            reply_markup=ReplyKeyboardMarkup(keyboard=[
                ["首頁🏠", "回題目📜"],
                ["登出🚪", "改密碼💱", "幫助📚"]
            ], resize_keyboard=True))

    def send_failed(self):
        self._status = '正常使用'
        bot.sendMessage(self._userid, "檔案不能超過 20 MB！上傳失敗",
            reply_markup=ReplyKeyboardMarkup(keyboard=[
                ["首頁🏠", "回題目📜"],
                ["登出🚪", "改密碼💱", "幫助📚"]
            ], resize_keyboard=True))

    def list_passers(self):
        self._status = '正常使用'
        q = self._api.list_questions()[self._question]
        q_str = "💁 <b>" + self._username + "</b> " + NAME + "\n"
        q_str += "➖➖➖➖➖\n"
        q_str += "📗" if q[1] == '期限未到' else "📕"
        q_str += "<b>" + self._question + "</b> (DL: " + q[0] + ")\n [[" + q[3] + "]] [[" + q[2] + "]]"
        q_str += "⚠️" if q[2] == '未繳' else "✅"
        q_str += "<code>\n"
        for passer in self._api.list_passers(self._question):
            q_str += "\n" + passer
        reply = bot.sendMessage(self._userid, q_str + "</code>", 
            parse_mode='HTML',
            reply_markup=ReplyKeyboardMarkup(keyboard=[
                ["首頁🏠", "回題目📜"],
                ["登出🚪", "改密碼💱", "幫助📚"]
            ], resize_keyboard=True))
        bot.sendMessage(self._userid, "點我到名單頂", reply_to_message_id=reply['message_id'])

    def list_results(self):
        self._status = '正常使用'
        q = self._api.list_questions()[self._question]
        q_str = "💁 <b>" + self._username + "</b> " + NAME + "\n"
        q_str += "➖➖➖➖➖\n"
        q_str += "📗" if q[1] == '期限未到' else "📕"
        q_str += "<b>" + self._question + "</b> (DL: " + q[0] + ")\n"
        for result in self._api.list_results(self._question, self._username):
            q_str += "\n測試編號 <code>" + result[0] + "</code>："
            q_str += "✔️ " if result[1] == '通過測試' else "❌ "
            q_str += result[1]
        bot.sendMessage(self._userid, q_str, 
            parse_mode='HTML', 
            reply_markup=ReplyKeyboardMarkup(keyboard=[
                ["首頁🏠", "回題目📜"],
                ["交作業📮" if q[1] == '期限未到' else '', "通過者🌐"],
                ["登出🚪", "改密碼💱", "幫助📚"]
            ], resize_keyboard=True))

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

        # test connection
        if command[0] == '/ping':
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
                    user.send_answer(msg['text'], '')

            else:
                if user.check_online(chat_id, msg['message_id']) == True:
                    bot.sendMessage(chat_id, "(ˊ・ω・ˋ)")
            
    elif content_type == 'document':
        if user._status == '上傳答案' or user._status == '查看題目':
            if user.check_online(chat_id, msg['message_id']) == True:
                if msg['document']['file_size'] > 167770000:
                    user.send_failed()
                else:
                    user.send_answer('', msg['document']['file_id'])

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
    with open(sys.path[0] + '/users.json', 'w') as f:
        json.dump(users_backup, f, indent='  ')

def restore_db():
    with open(sys.path[0] + '/users.json', 'r') as f:
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