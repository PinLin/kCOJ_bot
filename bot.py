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
        self.userid = userid
        self.username = username
        self.password = password
        self.status = status
        self.question = question
        self.api = KCOJ(URL)

    # 新使用者要登入
    def new_user(self):
        self.help()
        self.press_username()
    
    # 輸入學號
    def press_username(self):
        self.question = '題外'
        self.status = '輸入學號'
        bot.sendMessage(self.userid, "請輸入您的學號：", reply_markup=ReplyKeyboardRemove())

    # 輸入密碼
    def press_password(self, text):
        self.question = '題外'
        self.status = '輸入密碼'
        self.username = text
        bot.sendMessage(self.userid, 
            "輸入完可刪除訊息以策安全！\n"
            "請輸入您的密碼：",
            reply_markup=ReplyKeyboardRemove()
        )

    # 輸入舊密碼
    def press_oldpassword(self):
        self.question = '題外'
        self.status = '舊的密碼'
        bot.sendMessage(self.userid, 
            "請輸入要原本的舊密碼：",
            reply_markup=ReplyKeyboardMarkup(keyboard=[
                ["首頁🏠"]
            ], resize_keyboard=True)
        )

    # 輸入新密碼
    def press_newpassword(self, text):
        self.question = '題外'
        # 判斷舊密碼是否輸入正確
        if text == self.password:
            # 正確舊密碼
            self.status = '修改密碼'
            bot.sendMessage(self.userid, 
                "使用此功能請務必小心！\n"
                "請輸入要設定的新密碼：",
                reply_markup=ReplyKeyboardMarkup(keyboard=[
                    ["首頁🏠"]
                ], resize_keyboard=True)
            )
        else:
            # 錯誤舊密碼
            self.status = '正常使用'
            bot.sendMessage(self.userid, "密碼錯誤！",
                reply_markup=ReplyKeyboardMarkup(keyboard=[
                    ["首頁🏠"]
                ], resize_keyboard=True)
            )
    
    # 開始修改密碼
    def change_password(self, text):
        self.question = '題外'
        self.status = '正常使用'
        self.password = text
        bot.sendMessage(self.userid, 
            "修改成功！" if self.api.change_password(self.password) else "修改失敗。",
            reply_markup=ReplyKeyboardMarkup(keyboard=[
                ["首頁🏠"]
            ], resize_keyboard=True)
        )

    # 執行登入
    def login(self, text):
        self.question = '題外'
        self.status = '正常使用'
        self.password = text
        bot.sendMessage(self.userid, "登入中...", reply_markup=ReplyKeyboardRemove())
        if self.check_online(self.userid):
            self.show_homepage(self.userid)

    # 登入失敗
    def login_failed(self, chat_id, message_id):
        self.question = '題外'
        self.status = '正常使用'
        # 判斷使用者從哪操作
        if chat_id != self.userid:
            # 從群組操作
            bot.sendMessage(chat_id, "登入失敗，請先私訊我重新登入 KCOJ", reply_to_message_id=message_id)
        else:
            # 從私訊操作
            bot.sendMessage(self.userid, "哇...登入失敗，讓我們重新開始", reply_markup=ReplyKeyboardRemove())
        self.press_username()
        
    # 網站連接失敗
    def connect_failed(self, chat_id, message_id):
        self.question = '題外'
        self.status = '正常使用'
        # 群組操作
        if chat_id != self.userid:
            bot.sendMessage(chat_id, "KCOJ 離線中！請稍後再試", reply_to_message_id=message_id)
        # 私訊操作
        else:
            bot.sendMessage(self.userid, "KCOJ 離線中！請稍後再試",
                reply_markup=ReplyKeyboardMarkup(keyboard=[
                    ["首頁🏠", "幫助📚"]
                ], resize_keyboard=True)
            )

    # 確認登入是否正常
    def check_online(self, chat_id, message_id=''):
        result = self.api.check_online()
        # 判斷是否可連接上
        if result == None:
            # 連接失敗
            self.connect_failed(chat_id, message_id)
            return False
        else:
            # 連接成功
            # 判斷是否登入
            if result == False:
                # 沒有登入的話再嘗試重新登入一次
                self.api.login(self.username, self.password, 2)
                result = self.api.check_online()
            # 再次確認是否登入＆連接
            if result == None:
                # 連接失敗
                self.connect_failed(chat_id, message_id)
            elif result == False:
                # 登入失敗
                self.login_failed(chat_id, message_id)
            # 回傳登入狀態
            return result

    # 登出
    def logout(self):
        self.question = '題外'
        self.status = '正常使用'
        bot.sendMessage(self.userid, "您現在已經是登出的狀態。", reply_markup=ReplyKeyboardRemove())
        self.press_username()

    # 秀出主畫面
    def show_homepage(self, chat_id):
        self.question = '題外'
        self.status = '正常使用'
        # 題目列表字典
        q_dict = self.api.list_questions()
        # 題目列表字串
        q_str = ''
        # 將字典內容根據格式附加到字串上
        for key in q_dict.keys():
            # 只顯示期限未到的作業
            if q_dict[key][1] == '期限未到':
                q_str += (
                    "📗<b>{NUM}</b> (DL: {DL})\n"
                    " [[{LANG}]] [[{STATUS}]]{STAT_ICON}  /question_{NUM}\n"
                    "\n".format(
                        NUM=key,
                        DL=q_dict[key][0],
                        LANG=q_dict[key][3],
                        STATUS=q_dict[key][2],
                        STAT_ICON=("⚠️" if q_dict[key][2] == '未繳' else "✅")
                    )
                )
        # 顯示主頁面
        bot.sendMessage(chat_id,
            # 畫面格式
            "💁 <b>{NAME}</b> {BOT_NAME}\n"
            "➖➖➖➖➖\n"
            "📝<i>可繳交的作業</i>\n"
            "\n"
            "{Q_STR}"
            "➖➖➖➖➖\n"
            "{PROMOTE}"
            # 填入資訊
            "".format(NAME=self.username, BOT_NAME=NAME, Q_STR=q_str, PROMOTE=choice(promote.sentences)), 
            parse_mode='HTML',
            reply_markup=  
                # 群組內不顯示按鈕
                ReplyKeyboardRemove() if chat_id != self.userid else
                # 私訊內顯示按鈕
                ReplyKeyboardMarkup(keyboard=[
                    ["題庫📝"],
                    ["登出🚪", "改密碼💱", "幫助📚"]
                ], resize_keyboard=True),
            disable_web_page_preview=False
        )

    # 列出題目列表
    def list_questions(self, chat_id):
        self.question = '題外'
        self.status = '正常使用'
        # 題目列表字典
        q_dict = self.api.list_questions()
        # 題目列表字串
        q_str = ''
        # 將字典內容根據格式附加到字串上
        for key in q_dict.keys():
            q_str += (
                "{DL_ICON}<b>{NUM}</b> (DL: {DL})\n"
                " [[{LANG}]] [[{STATUS}]]{STAT_ICON}  /question_{NUM}\n"
                "\n".format(
                    DL_ICON=("📗" if q_dict[key][1] == '期限未到' else "📕"),
                    NUM=key,
                    DL=q_dict[key][0],
                    LANG=q_dict[key][3],
                    STATUS=q_dict[key][2],
                    STAT_ICON=("⚠️" if q_dict[key][2] == '未繳' else "✅")
                )
            )
        # 顯示題目列表並將訊息存起來
        last_msg = bot.sendMessage(chat_id,
            # 畫面格式
            "💁 <b>{NAME}</b> {BOT_NAME}\n"
            "➖➖➖➖➖\n"
            "📝<i>所有作業</i>\n"
            "\n"
            "{Q_STR}"
            "➖➖➖➖➖\n"
            "{PROMOTE}"
            # 填入資訊
            "".format(NAME=self.username, BOT_NAME=NAME, Q_STR=q_str, PROMOTE=choice(promote.sentences)),
            parse_mode='HTML',
            reply_markup=
                # 群組內不顯示按鈕
                ReplyKeyboardRemove() if chat_id != self.userid else 
                # 私訊內顯示按鈕
                ReplyKeyboardMarkup(keyboard=[
                    ["首頁🏠", "更新🔃"],
                    ["登出🚪", "改密碼💱", "幫助📚"]
                ], resize_keyboard=True) ,
            disable_web_page_preview=False
        )
        # 顯示點我到頂的訊息
        bot.sendMessage(chat_id, "點我到題庫頂", reply_to_message_id=last_msg['message_id'])

    # 顯示題目內容
    def show_question(self, number, chat_id):
        self.question = number
        self.status = '查看題目'
        # 如果外部有指定題目內容
        if number in external.QUESTION:
            # 顯示外部內容
            EXT = True
            content = external.QUESTION[number]
        else:
            # 顯示內部內容
            EXT = False
            content = '```' + self.api.show_question(number) + '```'
        # 題目資訊字典
        q_info = self.api.list_questions()[number]

        # 顯示題目內容並將訊息存起來
        last_msg = bot.sendMessage(chat_id, 
            "💁 *{NAME}* [{BOT_NAME}]\n"
            "➖➖➖➖➖\n"
            "{DL_ICON}*{NUM}* (DL: {DL})\n"
            " [[[{LANG}]]] [[[{STATUS}]]]{STAT_ICON}\n"
            "\n"
            "{CONTENT}\n".format(
                NAME=self.username,
                BOT_NAME=NAME,
                DL_ICON=("📗" if q_info[1] == '期限未到' else "📕"),
                NUM=number,
                DL=q_info[0],
                LANG=q_info[3],
                STATUS=q_info[2],
                STAT_ICON=("⚠️" if q_info[2] == '未繳' else "✅"),
                CONTENT=content
            ),
            parse_mode='Markdown',
            reply_markup=
                # 群組內不顯示按鈕
                ReplyKeyboardRemove() if chat_id != self.userid else
                # 私訊內顯示按鈕
                ReplyKeyboardMarkup(keyboard=[
                    ["首頁🏠", "題庫📝"],
                    ["交作業📮" if q_info[1] == '期限未到' else '', "看結果☑️" if q_info[2] == '已繳' else '', "通過者🌐"],
                    ["登出🚪", "改密碼💱", "幫助📚"]
                ], resize_keyboard=True)
        )
        if EXT == False:
            # 顯示點我到頂的訊息
            bot.sendMessage(chat_id, "點我到題目頂", reply_to_message_id=last_msg['message_id'])

    def help(self):
        # 印出幫助（？）和關於訊息
        bot.sendMessage(self.userid, 
            "這裡是 Kuo C Online Judge Bot！\n"
            "可以簡稱 KCOJ Bot，目前定居於 [{BOT_NAME}]\n"
            "作用是讓大家可以方便的透過我使用郭老程設課的 Online Judge\n"
            "➡️[OJ 傳送門]({URL})\n"
            "操作很簡單（？）\n\n"
            "還是稍微提幾個需要注意的地方：\n"
            "1. 📗代表還可以繳交的作業，📕代表已經不能繳交的作業\n"
            "2. ⚠️代表還沒有繳交的作業，✅代表已經繳交的作業\n"
            "3. 其實在查看題目的畫面就可以用「拖曳」的方式 *上傳作業📮*\n"
            "4. *刪除作業⚔️* 的功能被放在 *上傳作業📮* 裡面\n"
            "5. 學號與密碼將以「明文」方式儲存，因為....\n"
            "6. 郭老的 Online Judge 其實也是以「明文」方式儲存您的帳號密碼\n"
            "7. 我以我的人格擔保，不會使用您提供的資訊侵害您的權利\n\n"
            "本專案採用 *MIT License*\n"
            "聯絡我請私訊 @PinLin\n"
            "原始碼被託管於 GitHub，如果想要鼓勵我的話可以幫我按個星星> </\n"
            "網址如下：\n"
            "[https://github.com/PinLin/KCOJ_bot]".format(BOT_NAME=NAME, URL=URL),
            parse_mode='Markdown'
        )

    # 使用者選擇程式碼來上傳
    def upload_answer(self):
        self.status = '上傳答案'
        # 題目資訊字典
        q_info = self.api.list_questions()[self.question]
        bot.sendMessage(self.userid,
            "💁 <b>{NAME}</b> {BOT_NAME}\n"
            "➖➖➖➖➖\n"
            "{DL_ICON}<b>{NUM}</b> (DL: {DL})\n"
            " [[{LANG}]] [[{STATUS}]]{STAT_ICON}\n"
            "\n"
            "現在請把你的程式碼讓我看看（請別超過 20 MB）\n"
            "可以使用「文字訊息」或是「傳送檔案」的方式\n"
            "（注意：可在程式碼前後加上單獨成行的 ``` 避免可能的錯誤。）".format(
                NAME=self.username,
                BOT_NAME=NAME,
                DL_ICON=("📗" if q_info[1] == '期限未到' else "📕"),
                NUM=self.question,
                DL=q_info[0],
                LANG=q_info[3],
                STATUS=q_info[2],
                STAT_ICON=("⚠️" if q_info[2] == '未繳' else "✅")
            ), 
            parse_mode='HTML',
            reply_markup=
                ReplyKeyboardMarkup(keyboard=[
                    ["刪除作業⚔️"] if self.api.list_questions()[self.question][2] == '已繳' else [],
                    ["首頁🏠", "回題目📜"]
                ], resize_keyboard=True)
        )

    # 上傳程式碼
    def send_answer(self, text, file_id):
        self.status = '正常使用'
        # 定義檔名
        filename = sys.path[0] + '/' + self.username + self.question
        if self.api.list_questions()[self.question][3] == 'Python':
            filename += '.py'
        else:
            filename += '.c'
        # 判斷使用者要用什麼方式傳程式碼
        if text != '':
            # 傳送文字
            with open(filename, 'w') as f:
                f.write(text)
        else:
            # 傳送檔案
            bot.download_file(file_id, filename)
        # 先把原本的答案刪掉
        self.api.delete_answer(self.question)
        # 上傳並判斷是否成功
        if self.api.upload_answer(self.question, filename):
            # 上傳成功
            bot.sendMessage(self.userid, "上傳成功",
                reply_markup=ReplyKeyboardMarkup(keyboard=[
                    ["首頁🏠", "回題目📜"],
                    ["看結果☑️"],
                    ["登出🚪", "改密碼💱", "幫助📚"]
                ], resize_keyboard=True)
            )
        else:
            # 上傳失敗
            bot.sendMessage(self.userid, "上傳失敗",
                reply_markup=ReplyKeyboardMarkup(keyboard=[
                    ["首頁🏠", "回題目📜"],
                    ["登出🚪", "改密碼💱", "幫助📚"]
                ], resize_keyboard=True)
            )
        # 移除上傳的檔案
        os.remove(filename)    
    
    # 刪除之前繳交的程式碼
    def delete_answer(self):
        bot.sendMessage(self.userid, "移除成功" if self.api.delete_answer(self.question) else "移除失敗",
            reply_markup=ReplyKeyboardMarkup(keyboard=[
                ["首頁🏠", "回題目📜"],
                ["登出🚪", "改密碼💱", "幫助📚"]
            ], resize_keyboard=True)
        )

    # 上傳失敗（預設立場是檔案太大）
    def send_failed(self):
        self.status = '正常使用'
        bot.sendMessage(self.userid, "檔案不能超過 20 MB！上傳失敗",
            reply_markup=ReplyKeyboardMarkup(keyboard=[
                ["首頁🏠", "回題目📜"],
                ["登出🚪", "改密碼💱", "幫助📚"]
            ], resize_keyboard=True)
    )

    # 列出題目中已通過者的名單
    def list_passers(self):
        self.status = '正常使用'
        # 題目資訊字典
        q_info = self.api.list_questions()[self.question]
        # 題目資訊字串
        q_str = (
            "💁 <b>{NAME}</b> {BOT_NAME}\n"
            "➖➖➖➖➖\n"
            "{DL_ICON}<b>{NUM}</b> (DL: {DL})\n"
            " [[{LANG}]] [[{STATUS}]]{STAT_ICON}\n"
            "\n".format(
                NAME=self.username,
                BOT_NAME=NAME,
                DL_ICON=("📗" if q_info[1] == '期限未到' else "📕"),
                NUM=self.question,
                DL=q_info[0],
                LANG=q_info[3],
                STATUS=q_info[2],
                STAT_ICON=("⚠️" if q_info[2] == '未繳' else "✅")
            )
        )
        # 列出已通過者名單
        q_str += "<code>"
        for passer in self.api.list_passers(self.question):
            q_str += passer + "\n"
        q_str += "</code>"
        # 顯示題目內容並將訊息存起來
        last_msg = bot.sendMessage(self.userid, q_str, 
            parse_mode='HTML',
            reply_markup=ReplyKeyboardMarkup(keyboard=[
                ["首頁🏠", "回題目📜"],
                ["登出🚪", "改密碼💱", "幫助📚"]
            ], resize_keyboard=True)
        )
        # 顯示點我到頂的訊息
        bot.sendMessage(self.userid, "點我到名單頂", reply_to_message_id=last_msg['message_id'])

    # 顯示出成績
    def list_results(self):
        self.status = '正常使用'
        # 題目資訊字典
        q_info = self.api.list_questions()[self.question]
        # 題目資訊字串
        q_str = (
            "💁 <b>{NAME}</b> {BOT_NAME}\n"
            "➖➖➖➖➖\n"
            "{DL_ICON}<b>{NUM}</b> (DL: {DL})\n"
            " [[{LANG}]]\n"
            "\n".format(
                NAME=self.username,
                BOT_NAME=NAME,
                DL_ICON=("📗" if q_info[1] == '期限未到' else "📕"),
                NUM=self.question,
                DL=q_info[0],
                LANG=q_info[3]
            )
        )
        # 列出測試結果
        for result in self.api.list_results(self.question, self.username):
            q_str += "測試編號 <code>{}</code>：{} {}\n".format(
                result[0],
                "✔️ " if result[1] == '通過測試' else "❌ ",
                result[1]
            )
        bot.sendMessage(self.userid, q_str, 
            parse_mode='HTML', 
            reply_markup=ReplyKeyboardMarkup(keyboard=[
                ["首頁🏠", "回題目📜"],
                ["交作業📮" if q_info[1] == '期限未到' else '', "通過者🌐"],
                ["登出🚪", "改密碼💱", "幫助📚"]
            ], resize_keyboard=True)
        )

def on_chat(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    from_id = msg['from']['id']

    # create a user object
    user = Kuser(from_id)
    if str(from_id) in users:
        user = users[str(from_id)]
    else:
        users[str(from_id)] = user

    # debug message
    # ==========================================================
    pprint(msg)
    # name
    if 'last_name' in msg['from']:
        last_name = msg['from']['last_name']
    else:
        last_name = ''
    print("😊 student_name:", msg['from']['first_name'], last_name, "😊")
    # id
    print("😯 student_id:", user.username, "😯")
    print()
    # ==========================================================

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
        elif user.status == '第一次用':
            if chat_type == 'private':
                user.new_user()

        # press password
        elif user.status == '輸入學號':
            if chat_type == 'private':
                user.press_password(msg['text'])

        # login
        elif user.status == '輸入密碼':
            if chat_type == 'private':
                user.login(msg['text'])

        # homepage
        elif command[0] == '/start' or command[0] == '首頁🏠':
            if user.check_online(chat_id, msg['message_id']):
                user.show_homepage(chat_id)

        elif command[0] == '/question' or command[0] == '題庫📝' or command[0] == '更新🔃':
            if user.check_online(chat_id, msg['message_id']):
                if len(command) > 1:
                    user.show_question(command[1], chat_id)
                else:
                    user.list_questions(chat_id)

        elif chat_type == 'private':
            if command[0] == '/password' or command[0] == '改密碼💱':
                if user.check_online(chat_id, msg['message_id']):
                    user.press_oldpassword()

            elif command[0] == '/logout' or command[0] == '登出🚪':
                user = Kuser(from_id)
                users[str(from_id)] = user
                user.logout()

            elif (command[0] == '/delete' or command[0] == '刪除作業⚔️') and user.question != '題外':
                if user.check_online(chat_id, msg['message_id']):
                    user.delete_answer()

            elif (command[0] == '/upload' or command[0] == '交作業📮') and user.question != '題外':
                if user.check_online(chat_id, msg['message_id']):
                    user.upload_answer()

            elif (command[0] == '/result' or command[0] == '看結果☑️') and user.question != '題外':
                if user.check_online(chat_id, msg['message_id']):
                    user.list_results()

            elif (command[0] == '/passer' or command[0] == '通過者🌐') and user.question != '題外':
                if user.check_online(chat_id, msg['message_id']):
                    user.list_passers()

            elif command[0] == '回題目📜' and user.question != '題外':
                if user.check_online(chat_id, msg['message_id']):
                    user.show_question(user.question, chat_id)

            elif user.status == '舊的密碼':
                if user.check_online(chat_id, msg['message_id']):
                    user.press_newpassword(msg['text'])

            elif user.status == '修改密碼':
                if user.check_online(chat_id, msg['message_id']):
                    user.change_password(msg['text'])

            elif user.status == '上傳答案':
                if user.check_online(chat_id, msg['message_id']):
                    user.send_answer(msg['text'], '')

            else:
                if user.check_online(chat_id, msg['message_id']):
                    bot.sendMessage(chat_id, "(ˊ・ω・ˋ)")
            
    elif content_type == 'document':
        if user.status == '上傳答案' or user.status == '查看題目':
            if user.check_online(chat_id, msg['message_id']):
                if msg['document']['file_size'] > 167770000:
                    user.send_failed()
                else:
                    user.send_answer('', msg['document']['file_id'])

def backup_db():
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