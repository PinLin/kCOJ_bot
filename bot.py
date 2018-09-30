#! /usr/bin/env python3

import os
import sys
import time
import json
from random import choice

import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import ReplyKeyboardMarkup, ReplyKeyboardRemove
from pymongo import MongoClient
from KCOJ_api import KCOJ

sentences = [
    "你今天寫扣了嗎？",
    "多多參加系上活動程設課會加分哦！",
    "曾經有位學長寫了一個交作業網站，\n叫做郭老愛你。",
    "郭老說過，零分很危險。",
    "郭老說過，每週至少要花 87 小時練習寫程式。",
    "根據大數據分析，\n每年至少有 1/3 的同學明年會再修一次程設課",
    "給自由的狐狸一次機會owo\nhttps://www.mozilla.org/zh-TW/firefox/",
    "https://www.getgnulinux.org/zh-tw/",
    "<a href='https://zh.wikipedia.org/wiki/%E7%BC%96%E8%BE%91%E5%99%A8%E4%B9%8B%E6%88%98'>編輯器之戰</a>",
    "Visual Studio Code 讚讚\nhttps://code.visualstudio.com",
    "不要用 Windows 啦！",
    "互相傷害啊。",
    "天氣好的時候，天空是藍的。",
    "在非洲，每 60 秒過去就過了 1 分鐘。",
    "(ˊ・ω・ˋ)",
    "(ˊ・ω・ˋ)(ˊ・ω・ˋ)",
    "(ˊ・ω・ˋ)(ˊ・ω・ˋ)(ˊ・ω・ˋ)",
    "現在有網頁版本的 KCOJ 囉！\nhttps://kcoj.ntut.com.tw",
    "現在有網頁版本的 KCOJ 囉！\nhttps://kcoj.ntut.com.tw",
    "現在有網頁版本的 KCOJ 囉！\nhttps://kcoj.ntut.com.tw",
    "現在有網頁版本的 KCOJ 囉！\nhttps://kcoj.ntut.com.tw",
    "現在有網頁版本的 KCOJ 囉！\nhttps://kcoj.ntut.com.tw",
    "現在有網頁版本的 KCOJ 囉！\nhttps://kcoj.ntut.com.tw",
    "現在有網頁版本的 KCOJ 囉！\nhttps://kcoj.ntut.com.tw",
]

with open('config.json', 'r') as f:
    config = json.load(f)

# 取得 Bot 實體
bot = telepot.Bot(config['BOT']['TOKEN'])
# 取得資料庫實體
db = MongoClient().kcoj_bot


class Kuser:
    def __init__(self, uid):
        self.uid = uid
        self.api = KCOJ(config['TARGET']['URL'])

    @property
    def username(self):
        obj = db.users.find_one({'uid': self.uid})
        return obj and obj['username']

    @username.setter
    def username(self, username):
        db.users.update({'uid': self.uid}, {
                        "$set": {"username": username}}, upsert=True)

    @property
    def password(self):
        obj = db.users.find_one({'uid': self.uid})
        return obj and obj['password']

    @password.setter
    def password(self, password):
        db.users.update({'uid': self.uid}, {
                        "$set": {"password": password}}, upsert=True)

    @property
    def status(self):
        obj = db.users.find_one({'uid': self.uid})
        return obj and obj['status']

    @status.setter
    def status(self, status):
        db.users.update({'uid': self.uid}, {
                        "$set": {"status": status}}, upsert=True)

    @property
    def question(self):
        obj = db.users.find_one({'uid': self.uid})
        return obj and obj['question']

    @question.setter
    def question(self, question):
        db.users.update({'uid': self.uid}, {
                        "$set": {"question": question}}, upsert=True)

    # 新使用者要登入
    def create_user(self):
        self.show_help()
        self.input_username()

    # 輸入學號
    def input_username(self):
        self.question = None
        self.status = '輸入學號'
        bot.sendMessage(self.uid, "請輸入您的學號：",
                        reply_markup=ReplyKeyboardRemove())

    # 輸入密碼
    def input_password(self, text):
        self.question = None
        self.status = '輸入密碼'
        self.username = text
        # 發送訊息
        bot.sendMessage(self.uid, "輸入完可刪除訊息以策安全！\n請輸入您的密碼：",
                        reply_markup=ReplyKeyboardRemove())

    # 輸入舊密碼
    def input_oldpassword(self):
        self.question = None
        self.status = '舊的密碼'
        bot.sendMessage(self.uid, "請輸入要原本的舊密碼：",
                        reply_markup=ReplyKeyboardMarkup(keyboard=[
                            ['首頁🏠']
                        ], resize_keyboard=True))

    # 輸入新密碼
    def input_newpassword(self, text):
        self.question = None
        # 判斷舊密碼是否輸入正確
        if text == self.password:
            # 正確舊密碼
            self.status = '修改密碼'
            bot.sendMessage(self.uid, "請輸入要設定的新密碼：",
                            reply_markup=ReplyKeyboardMarkup(keyboard=[
                                ['首頁🏠']
                            ], resize_keyboard=True))
        else:
            # 錯誤舊密碼
            self.status = '正常使用'
            bot.sendMessage(self.uid, "密碼錯誤！",
                            reply_markup=ReplyKeyboardMarkup(keyboard=[
                                ['首頁🏠']
                            ], resize_keyboard=True))

    # 開始修改密碼
    def change_password(self, text):
        self.question = None
        self.status = '正常使用'
        # 判斷是否修改
        if self.api.update_password(text):
            content = "修改成功！"
            # 修改紀錄的密碼
            self.password = text
        else:
            content = "修改失敗。"
        # 發送訊息
        bot.sendMessage(self.uid, content,
                        reply_markup=ReplyKeyboardMarkup(keyboard=[
                            ['首頁🏠']
                        ], resize_keyboard=True))

    # 執行登入
    def login(self, text):
        self.question = None
        self.status = '正常使用'
        self.password = text
        # 發送訊息
        bot.sendMessage(self.uid, "登入中...",
                        reply_markup=ReplyKeyboardRemove())
        # 嘗試登入
        if self.keep_online(self.uid):
            # 進入首頁
            self.show_home(self.uid)

    # 登入失敗
    def login_failed(self, chat_id, message_id):
        self.question = None
        self.status = '正常使用'
        # 判斷使用者從哪操作
        if chat_id != self.uid:
            # 從群組操作
            bot.sendMessage(chat_id, "登入失敗，請先私訊我重新登入 KCOJ",
                            reply_to_message_id=message_id)
        else:
            # 從私訊操作
            bot.sendMessage(self.uid, "哇...登入失敗，讓我們重新開始",
                            reply_markup=ReplyKeyboardRemove())
        self.input_username()

    # 網站連接失敗
    def connect_failed(self, chat_id, message_id):
        self.question = None
        self.status = '正常使用'
        # 群組操作
        if chat_id != self.uid:
            bot.sendMessage(chat_id, "KCOJ 離線中！請稍後再試",
                            reply_to_message_id=message_id)
        # 私訊操作
        else:
            bot.sendMessage(self.uid, "KCOJ 離線中！請稍後再試",
                            reply_markup=ReplyKeyboardMarkup(keyboard=[
                                ['首頁🏠', '幫助📚']
                            ], resize_keyboard=True))

    # 確認登入是否正常
    def keep_online(self, chat_id, message_id=''):
        active = self.api.active
        # 連接不上伺服器
        if active == None:
            self.connect_failed(chat_id, message_id)
            return False

        # 判斷是否登入
        if not active:
            # 沒有登入的話嘗試重新登入（4 為 107-1 郭老課的課程序號）
            self.api.login(self.username, self.password, 4)
            active = self.api.active
            # 再次確認是否登入
            if not active:
                # 登入失敗
                self.login_failed(chat_id, message_id)
        # 回傳登入狀態
        return active

    # 登出
    def logout(self):
        self.question = None
        self.status = '正常使用'
        bot.sendMessage(self.uid, "您現在已經是登出的狀態。",
                        reply_markup=ReplyKeyboardRemove())
        self.input_username()

    # 秀出主畫面
    def show_home(self, chat_id):
        self.question = None
        self.status = '正常使用'

        # 訊息內容
        content = '''
        💁 <b>{USERNAME}</b> {BOT_NAME}
        ➖➖➖➖➖
        📝<i>可繳交的作業</i>
        {QUESTIONS}
        ➖➖➖➖➖
        {SENTENCES}
        '''.replace('        ', '')

        # 題目資訊列表
        questions = ''
        data = self.api.get_question()
        for number in data.keys():
            # 跳過期限已到的作業
            if data[number]['expired']:
                continue
            # 題目資訊模板
            question = '''
            {DL_ICON}<b>{NUMBER}</b> (DL: {DL})
             [[{LANG}]] [[{STATUS}]]{STAT_ICON}  /question_{NUMBER}
            '''.replace('            ', '')
            # 串接到列表上
            questions += question.format(
                DL_ICON=("📕" if data[number]['expired'] else "📗"),
                NUMBER=number,
                DL=data[number]['deadline'],
                LANG=data[number]['language'],
                STATUS=("已繳" if data[number]['status'] else "未繳"),
                STAT_ICON=("✅" if data[number]['status'] else "⚠️"))

        content = content.format(USERNAME=self.username,
                                 BOT_NAME=config['BOT']['NAME'],
                                 QUESTIONS=questions,
                                 SENTENCES=choice(sentences))

        # 訊息鍵盤
        if chat_id != self.uid:
            # 群組內不顯示按鈕
            reply_markup = ReplyKeyboardRemove()
        else:
            # 私訊內顯示按鈕
            reply_markup = ReplyKeyboardMarkup(keyboard=[
                ['題庫📝'],
                ['登出🚪', '改密碼💱', '幫助📚']
            ], resize_keyboard=True)

        # 發送訊息
        bot.sendMessage(chat_id, content, parse_mode='HTML',
                        reply_markup=reply_markup)

    # 列出題目列表
    def show_questions(self, chat_id):
        self.question = None
        self.status = '正常使用'
        # 訊息內容
        content = '''
            💁 <b>{USERNAME}</b> {BOT_NAME}
            ➖➖➖➖➖
            📝<i>所有作業</i>
            {QUESTIONS}
            ➖➖➖➖➖
            {SENTENCES}
            '''.replace('            ', '')

        # 題目資訊列表
        questions = ''
        data = self.api.get_question()
        # 將字典內容根據格式附加到字串上
        for number in data.keys():
            # 題目資訊模板
            question = '''
            {DL_ICON}<b>{NUMBER}</b> (DL: {DL})
             [[{LANG}]] [[{STATUS}]]{STAT_ICON}  /question_{NUMBER}
            '''.replace('            ', '')
            # 串接到列表上
            questions += question.format(
                DL_ICON=("📕" if data[number]['expired'] else "📗"),
                NUMBER=number,
                DL=data[number]['deadline'],
                LANG=data[number]['language'],
                STATUS=("已繳" if data[number]['status'] else "未繳"),
                STAT_ICON=("✅" if data[number]['status'] else "⚠️"))

        content = content.format(USERNAME=self.username,
                                 BOT_NAME=config['BOT']['NAME'],
                                 QUESTIONS=questions,
                                 SENTENCES=choice(sentences))

        # 訊息鍵盤
        if chat_id != self.uid:
            # 群組內不顯示按鈕
            reply_markup = ReplyKeyboardRemove()
        else:
            # 私訊內顯示按鈕
            reply_markup = ReplyKeyboardMarkup(keyboard=[
                ['首頁🏠', '更新🔃'],
                ['登出🚪', '改密碼💱', '幫助📚']
            ], resize_keyboard=True)

        # 顯示題目列表並將訊息存起來
        msg = bot.sendMessage(chat_id, content, parse_mode='HTML',
                              reply_markup=reply_markup)
        # 顯示點我到頂的訊息
        bot.sendMessage(chat_id, "點我到題庫頂",
                        reply_to_message_id=msg['message_id'])

    # 顯示題目內容
    def show_question_content(self, number, chat_id):
        self.question = number
        self.status = '查看題目'
        # 訊息內容
        content = '''
        💁 *{NAME}* [{BOT_NAME}]
        ➖➖➖➖➖
        {DL_ICON}*{NUM}* (DL: {DL})
         [[[{LANG}]]] [[[{STATUS}]]]{STAT_ICON}
        
        ```{QUESTION_CONTENT}```
        '''.replace('        ', '')
        # 取得題目資訊
        info = self.api.get_question()[number]
        content = content.format(
            NAME=self.username,
            BOT_NAME=config['BOT']['NAME'],
            DL_ICON=("📕" if info['expired'] else "📗"),
            NUM=number,
            DL=info['deadline'],
            LANG=info['language'],
            STATUS=("已繳" if info['status'] else "未繳"),
            STAT_ICON=("✅" if info['status'] else "⚠️"),
            QUESTION_CONTENT=self.api.get_question_content(number))

        if chat_id != self.uid:
            # 群組內不顯示按鈕
            reply_markup = ReplyKeyboardRemove()
        else:
            # 私訊內顯示按鈕
            reply_markup = ReplyKeyboardMarkup(keyboard=[
                ['首頁🏠', '題庫📝'],
                ['交作業📮' if not info['expired'] else '',
                    '看結果☑️' if info['status'] else '',
                    '通過者🌐'],
                ['登出🚪', '改密碼💱', '幫助📚']
            ], resize_keyboard=True)

        # 顯示題目內容並將訊息存起來
        msg = bot.sendMessage(chat_id, content, parse_mode='Markdown',
                              reply_markup=reply_markup)
        # 顯示點我到頂的訊息
        bot.sendMessage(chat_id, "點我到題目頂",
                        reply_to_message_id=msg['message_id'])

    def show_help(self):
        # 幫助（？）和關於訊息
        content = """
        這裡是 Kuo C Online Judge Bot！
        可以簡稱 KCOJ Bot，目前定居於 [{BOT_NAME}]
        作用是讓大家可以方便的透過我使用郭老程設課的 Online Judge
        ➡️[OJ 傳送門]({TARGET_URL})
        操作很簡單（？）

        還是稍微提幾個需要注意的地方：
        1. 📗代表還可以繳交的作業，📕代表已經不能繳交的作業
        2. ⚠️代表還沒有繳交的作業，✅代表已經繳交的作業
        3. 其實在查看題目的畫面就可以用「拖曳」的方式 *上傳作業📮*
        4. *刪除作業⚔️* 的功能被放在 *上傳作業📮* 裡面
        5. 學號與密碼將以「明文」方式儲存，因為....
        6. 郭老的 Online Judge 其實也是以「明文」方式儲存您的帳號密碼
        7. 我以我的人格擔保，不會使用您提供的資訊侵害您的權利

        本專案採用 *MIT License*
        聯絡我請私訊 @PinLin
        原始碼被託管於 GitHub，如果想要鼓勵我的話可以幫我按個星星> </
        網址如下：
        [https://github.com/PinLin/KCOJ_bot]
        """.replace('        ', '').format(
            BOT_NAME=config['BOT']['NAME'],
            TARGET_URL=config['TARGET']['URL'])
        # 傳送訊息
        bot.sendMessage(self.uid, content, parse_mode='Markdown')

    # 使用者選擇程式碼來上傳
    def upload_answer(self):
        self.status = '上傳答案'
        # 訊息內容
        content = """
        💁 <b>{NAME}</b> {BOT_NAME}
        ➖➖➖➖➖
        {DL_ICON}<b>{NUMBER}</b> (DL: {DL})
         [[{LANG}]] [[{STATUS}]]{STAT_ICON}
        
        現在請把你的程式碼讓我看看（2 MB 以下）
        可以使用「文字訊息」或是「傳送檔案」的方式
        （可在程式碼前後加上單獨成行的 ``` 避免可能的錯誤。）
        """.replace('        ', '')
        # 取得題目資訊
        info = self.api.get_question()[self.question]
        content = content.format(
            NAME=self.username,
            BOT_NAME=config['BOT']['NAME'],
            DL_ICON=("📕" if info['expired'] else "📗"),
            NUMBER=self.question,
            DL=info['deadline'],
            LANG=info['language'],
            STATUS=("已繳" if info['status'] else "未繳"),
            STAT_ICON=("✅" if info['status'] else "⚠️"))
        # 訊息鍵盤
        keyboard = [
            ['刪除作業⚔️'] if info['status'] else [],
            ['首頁🏠', '回題目📜']
        ]
        # 發送訊息
        bot.sendMessage(self.uid, content, parse_mode='HTML',
                        reply_markup=ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True))

    # 上傳程式碼
    def send_answer(self, text, file_id):
        self.status = '正常使用'
        # 定義檔名
        filename = sys.path[0] + '/' + self.username + self.question
        if self.api.get_question()[self.question]['language'] == 'Python':
            filename += '.py'
        if self.api.get_question()[self.question]['language'] == 'C':
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
        self.api.delete_question_answer(self.question)
        # 上傳並判斷是否成功
        if self.api.post_question_answer(self.question, "Send from KCOJ_bot", filename):
            # 上傳成功
            bot.sendMessage(self.uid, "上傳成功",
                            reply_markup=ReplyKeyboardMarkup(keyboard=[
                                ['首頁🏠', '回題目📜'],
                                ['看結果☑️'],
                                ['登出🚪', '改密碼💱', '幫助📚']
                            ], resize_keyboard=True)
                            )
        else:
            # 上傳失敗
            bot.sendMessage(self.uid, "上傳失敗",
                            reply_markup=ReplyKeyboardMarkup(keyboard=[
                                ['首頁🏠', '回題目📜'],
                                ['登出🚪', '改密碼💱', '幫助📚']
                            ], resize_keyboard=True)
                            )
        # 移除上傳的檔案
        os.remove(filename)

    # 刪除之前繳交的程式碼
    def delete_answer(self):
        # 訊息內容
        if self.api.delete_question_answer(self.question):
            content = "移除成功"
        else:
            content = "移除失敗"
        # 發送訊息
        bot.sendMessage(self.uid, content,
                        reply_markup=ReplyKeyboardMarkup(keyboard=[
                            ['首頁🏠', '回題目📜'],
                            ['登出🚪', '改密碼💱', '幫助📚']
                        ], resize_keyboard=True))

    # 上傳失敗（預設立場是檔案太大）
    def send_failed(self):
        self.status = '正常使用'
        bot.sendMessage(self.uid, "檔案不能超過 2 MB！上傳失敗",
                        reply_markup=ReplyKeyboardMarkup(keyboard=[
                            ['首頁🏠', '回題目📜'],
                            ['登出🚪', '改密碼💱', '幫助📚']
                        ], resize_keyboard=True)
                        )

    # 列出題目中已通過者的名單
    def list_passers(self):
        self.status = '正常使用'
        # 訊息內容
        content = '''
        💁 <b>{NAME}</b> {BOT_NAME}
        ➖➖➖➖➖
        {DL_ICON}<b>{NUMBER}</b> (DL: {DL})
         [[{LANG}]] [[{STATUS}]]{STAT_ICON}

        <code>{PASSERS}</code>
        '''.replace('        ', '')
        # 取得題目資訊
        info = self.api.get_question()[self.question]
        # 列出已通過者名單
        passers = ''
        for passer in self.api.get_question_passers(self.question):
            passers += passer + "\n"
        content = content.format(
            NAME=self.username,
            BOT_NAME=config['BOT']['NAME'],
            DL_ICON=("📕" if info['expired'] else "📗"),
            NUMBER=self.question,
            DL=info['deadline'],
            LANG=info['language'],
            STATUS=("已繳" if info['status'] else "未繳"),
            STAT_ICON=("✅" if info['status'] else "⚠️"),
            PASSERS=passers)
        # 發送訊息
        msg = bot.sendMessage(self.uid, content, parse_mode='HTML',
                              reply_markup=ReplyKeyboardMarkup(keyboard=[
                                  ['首頁🏠', '回題目📜'],
                                  ['登出🚪', '改密碼💱', '幫助📚']
                              ], resize_keyboard=True))
        # 顯示點我到頂的訊息
        bot.sendMessage(self.uid, "點我到名單頂",
                        reply_to_message_id=msg['message_id'])

    # 顯示出成績
    def list_results(self):
        self.status = '正常使用'
        # 訊息內容
        content = '''
        💁 <b>{NAME}</b> {BOT_NAME}
        ➖➖➖➖➖
        {DL_ICON}<b>{NUMBER}</b> (DL: {DL})
         [[{LANG}]] [[{STATUS}]]{STAT_ICON}

        {RESULTS}
        '''.replace('        ', '')
        # 取得題目資訊
        info = self.api.get_question()[self.question]
        # 列出測試結果
        results = ''
        for index, status in self.api.get_question_results(self.question, self.username).items():
            results += "測試編號 <code>{}</code>：{} {}\n".format(
                index, "✔️ " if status == '通過測試' else "❌ ", status)
        content = content.format(
            NAME=self.username,
            BOT_NAME=config['BOT']['NAME'],
            DL_ICON=("📕" if info['expired'] else "📗"),
            NUMBER=self.question,
            DL=info['deadline'],
            LANG=info['language'],
            STATUS=("已繳" if info['status'] else "未繳"),
            STAT_ICON=("✅" if info['status'] else "⚠️"),
            RESULTS=results)
        # 發送訊息
        bot.sendMessage(self.uid, content, parse_mode='HTML',
                        reply_markup=ReplyKeyboardMarkup(keyboard=[
                            ['首頁🏠', '回題目📜'],
                            ['交作業📮' if not info['expired'] else '', '通過者🌐'],
                            ['登出🚪', '改密碼💱', '幫助📚']
                        ], resize_keyboard=True))


# 使用者物件字典
users = {}


def on_chat(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    from_id = msg['from']['id']

    # 新增一個使用者物件
    user = Kuser(from_id)
    # 判斷字典是否已存在該使用者
    if str(from_id) in users:
        # 已存在所以改用字典的
        user = users[str(from_id)]
    else:
        # 不存在所以放進字典裡
        users[str(from_id)] = user

    # 如果是文字訊息
    if content_type == 'text':
        # 指令預處理
        command = [msg['text']]
        if msg['text'].startswith('/'):
            command = msg['text'].replace(config['BOT']['NAME'], '')
            command = command.replace('_', ' ').lower().split(' ')

        # PING 這個 Bot
        if command[0] == '/ping':
            bot.sendMessage(chat_id, "*PONG*",
                            parse_mode='Markdown',
                            reply_to_message_id=msg['message_id'])

        # 幫助
        elif command[0] == '/help' or command[0] == '幫助📚':
            if chat_type == 'private':
                user.show_help()

        # 如果是第一次用
        elif user.status == None:
            if chat_type == 'private':
                user.create_user()

        # 輸完學號換輸入密碼
        elif user.status == '輸入學號':
            if chat_type == 'private':
                user.input_password(msg['text'])

        # 登入
        elif user.status == '輸入密碼':
            if chat_type == 'private':
                user.login(msg['text'])

        # 顯示首頁
        elif command[0] == '/start' or command[0] == '首頁🏠':
            if user.keep_online(chat_id, msg['message_id']):
                user.show_home(chat_id)

        # 顯示題庫或特定題目
        elif command[0] == '/question' or command[0] == '題庫📝' or command[0] == '更新🔃':
            if user.keep_online(chat_id, msg['message_id']):
                # 判斷要顯示題庫還是特定題目
                if len(command) > 1:
                    # 顯示特定題目
                    user.show_question_content(command[1], chat_id)
                else:
                    # 顯示題庫
                    user.show_questions(chat_id)

        # 只有私訊才可使用的功能
        elif chat_type == 'private':
            # 修改密碼
            if command[0] == '/password' or command[0] == '改密碼💱':
                if user.keep_online(chat_id, msg['message_id']):
                    user.input_oldpassword()

            # 登出
            elif command[0] == '/logout' or command[0] == '登出🚪':
                user = Kuser(from_id)
                users[str(from_id)] = user
                user.logout()

            # 刪除作業
            elif (command[0] == '/delete' or command[0] == '刪除作業⚔️') and user.question:
                if user.keep_online(chat_id, msg['message_id']):
                    user.delete_answer()

            # 選擇要上傳的作業
            elif (command[0] == '/upload' or command[0] == '交作業📮') and user.question:
                if user.keep_online(chat_id, msg['message_id']):
                    user.upload_answer()

            # 看作業執行結果
            elif (command[0] == '/result' or command[0] == '看結果☑️') and user.question:
                if user.keep_online(chat_id, msg['message_id']):
                    user.list_results()

            # 看本題已通過者
            elif (command[0] == '/passer' or command[0] == '通過者🌐') and user.question:
                if user.keep_online(chat_id, msg['message_id']):
                    user.list_passers()

            # 回到題目內容
            elif command[0] == '回題目📜' and user.question:
                if user.keep_online(chat_id, msg['message_id']):
                    user.show_question_content(user.question, chat_id)

            # 輸完舊密碼要輸新密碼
            elif user.status == '舊的密碼':
                if user.keep_online(chat_id, msg['message_id']):
                    user.input_newpassword(msg['text'])

            # 修改密碼
            elif user.status == '修改密碼':
                if user.keep_online(chat_id, msg['message_id']):
                    user.change_password(msg['text'])

            # 上傳程式碼中
            elif user.status == '上傳答案':
                if user.keep_online(chat_id, msg['message_id']):
                    user.send_answer(msg['text'], '')

            # 使用者傳了其他東西
            else:
                if user.keep_online(chat_id, msg['message_id']):
                    bot.sendMessage(chat_id, "(ˊ・ω・ˋ)")

    # 如果是上傳檔案
    elif content_type == 'document':
        # 如果正要上傳程式碼的狀態
        if user.status == '上傳答案' or user.status == '查看題目':
            if user.keep_online(chat_id, msg['message_id']):
                # 判斷有沒有超過限制大小
                if msg['document']['file_size'] > 2097152:
                    # 超過了
                    user.send_failed()
                else:
                    # 沒超過，上傳
                    user.send_answer('', msg['document']['file_id'])

    # 操作記錄
    print("=====================================")
    # 使用者資訊
    print("😊 INFO")
    # 使用者學號
    print("    student_id:", user.username)
    # telegram ID
    if 'username' in msg['from']:
        print("    telegram_id:", "@" + msg['from']['username'])
    # 使用者名稱
    if 'last_name' in msg['from']:
        last_name = msg['from']['last_name']
    else:
        last_name = ''
    print("    name:", msg['from']['first_name'], last_name)
    # 使用者狀態
    print("😆 STATUS")
    print("    status:", user.status)
    print("    question:", user.question)
    # 聊天種類
    print("😎 CHAT")
    print("    type:", msg['chat']['type'])
    if msg['chat']['type'] != 'private':
        print("    title:", msg['chat']['title'])
    # 使用者傳送文字
    if 'text' in msg:
        print("😯 TEXT")
        print("    text:", msg['text'])
    if 'caption' in msg:
        print("😯 TEXT")
        print("    text: ", msg['caption'])
    # 使用者傳送檔案
    if 'document' in msg:
        print("😠 DOCUMENT")
        print("    file_name:", msg['document']['file_name'])
        print("    file_id:", msg['document']['file_id'])


# 開始執行
MessageLoop(bot, on_chat).run_as_thread()
print("Started! Service is available.")

while True:
    time.sleep(60)

    # 定期敲 Telegram 讓 Bot 不要死掉
    bot.getMe()
