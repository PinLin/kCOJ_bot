#! /usr/bin/env python3

# necessary modules
import requests, telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from pprint import pprint
# kCOJ API
import access
# configurations
import config

class kuser:
    def __init__(self, chat_id, bot):
        self.chat_id = chat_id
        self.bot = bot
        self.username = ''
        self.password = ''
        self.status = '第一次用'
        self.api = access.kuser_api()

    def new_user(self):
        self.bot.sendMessage(self.chat_id, "是初次見面的朋友呢，設定一下吧！", reply_markup=ReplyKeyboardRemove())
        self.press_username()
    
    def press_username(self):
        self.status = '輸入學號'
        self.bot.sendMessage(self.chat_id, "請輸入您的學號：", reply_markup=ReplyKeyboardRemove())

    def press_password(self, text):
        self.status = '輸入密碼'
        self.username = text
        self.bot.sendMessage(self.chat_id, "輸入完可刪除訊息以策安全！\n請輸入您的密碼：", reply_markup=ReplyKeyboardRemove())

    def press_oldpassword(self):
        self.status = '舊的密碼'
        self.bot.sendMessage(self.chat_id, "輸入錯誤將取消操作\n"
                                           "請輸入要原本的舊密碼：", reply_markup=ReplyKeyboardRemove())

    def press_newpassword(self, text):
        self.status = '修改密碼'
        if text != self.password:
            self.display_main()
        else:
            self.bot.sendMessage(self.chat_id, "使用此功能請務必小心！\n"
                                               "請輸入要設定的新密碼：", reply_markup=ReplyKeyboardRemove())
        
    def change_password(self, text):
        self.status = '正常使用'
        self.password = text
        self.bot.sendMessage(self.chat_id, "修改成功" if self.api.change_password(self.password) == True else "修改失敗",
            reply_markup=ReplyKeyboardMarkup(keyboard=[
                [KeyboardButton(text="回主畫面🏠")]
            ]))

    def login_kcoj(self, text):
        self.status = '正常使用'
        self.password = text
        self.bot.sendMessage(self.chat_id, "登入中...", reply_markup=ReplyKeyboardRemove())
        if self.check_online() == True:
            self.display_main()

    def fail_login(self):
        self.bot.sendMessage(self.chat_id, "哇...登入失敗，讓我們重新開始一次", reply_markup=ReplyKeyboardRemove())
        self.press_username()

    def check_online(self):
        self.api.login_kcoj(self.username, self.password)
        if self.api.check_online() == True:
            return True
        else:
            self.fail_login()
            return False

    def logout_system(self):
        self.bot.sendMessage(self.chat_id, "您現在已經是登出的狀態。", reply_markup=ReplyKeyboardRemove())
        self.press_username()

    def display_main(self):
        self.status = '正常使用'
        q_dict = self.api.list_questions()
        q_available = "📝<i>可繳交的作業</i>\n\n"
        q_unavailable = "📝<i>沒有可繳交的作業哦！</i>\n"
        if q_dict == {}:
            q_str = q_unavailable
        else:
            q_str = q_available
            for key in q_dict.keys():
                if q_dict[key][1] == '期限未到':
                    q_str += "📗<b>" + key + "</b> (到 " + q_dict[key][0] + ")\n [" + q_dict[key][2] + "] /question_" + key + "\n\n"
            if q_str == q_available:
                q_str = q_unavailable
        self.bot.sendMessage(self.chat_id, "💁 <b>" + self.username + "</b> /logout\n"
                                           "➖➖➖➖➖\n" + q_str + "➖➖➖➖➖\n"
                                           "你今天寫扣了嗎？",
                                           parse_mode='HTML',
                                           reply_markup=ReplyKeyboardMarkup(keyboard=[
                                               [KeyboardButton(text="查看題庫📝"), KeyboardButton(text="重新整理🔃")],
                                               [KeyboardButton(text="登出帳號🚪"), KeyboardButton(text="修改密碼💱"), KeyboardButton(text="提供幫助📚")]
                                           ]))

    def display_questions(self):
        self.status = '正常使用'
        q_dict = self.api.list_questions()
        q_str = ''
        for key in q_dict.keys():
            q_str += "📗" if q_dict[key][1] == '期限未到' else "📕"
            q_str += "<b>" + key + "</b> (到 " + q_dict[key][0] + ")\n [" + q_dict[key][2] + "] /question_" + key + "\n\n"
        self.bot.sendMessage(self.chat_id, "💁 <b>" + self.username + "</b> /logout\n"
                                           "➖➖➖➖➖\n📝<i>所有作業</i>\n\n" + q_str + "➖➖➖➖➖\n"
                                           "你今天寫扣了嗎？", 
                                           parse_mode='HTML',
                                           reply_markup=ReplyKeyboardMarkup(keyboard=[
                                               [KeyboardButton(text="回主畫面🏠"), KeyboardButton(text="重新載入🔃")],
                                               [KeyboardButton(text="登出帳號🚪"), KeyboardButton(text="修改密碼💱"), KeyboardButton(text="提供幫助📚")]
                                           ]))

    def display_question(self, number):
        self = '正常使用'
        content = self.api.show_question(number)
        q = self.api.list_questions()[number]
        q_str = "📗" if q[1] == '期限未到' else "📕"
        q_str += "<b>" + number + "</b> (到 " + q[0] + ")"
        self.bot.sendMessage(self.chat_id, q_str + "\n<code>" + content + "</code>",
            parse_mode='HTML',
            reply_markup=ReplyKeyboardMarkup(keyboard=[
                [KeyboardButton(text="回主畫面🏠"), KeyboardButton(text="回到題庫📝")],
                [KeyboardButton(text="上傳解答📮"), KeyboardButton(text="查看結果☑️"), KeyboardButton(text="通過名單🌐")] if q[1] == '期限未到' else 
                [KeyboardButton(text="查看結果☑️"), KeyboardButton(text="通過名單🌐")],
                [KeyboardButton(text="登出帳號🚪"), KeyboardButton(text="修改密碼💱"), KeyboardButton(text="提供幫助📚")]
            ]))

    def help_you(self):
        self.status = '正常使用'
        self.bot.sendMessage(self.chat_id, "這裡是 kC Online Judge Bot！\n"
                                           "可以簡稱我為 kCOJ Bot，目前定居於 `@kcoj_bot`\n"
                                           "作用是讓大家可以方便的透過我使用郭老程設課的 Online Judge\n"
                                           "操作很簡單（？）我想大家應該都不會有問題吧～\n\n"
                                           "不過還是有些需要注意的地方：\n"
                                           "1. 學號與密碼將以「明文」方式儲存在記憶體裡，不會儲存在我的硬碟中。\n"
                                           "2. 反正郭老的 Online Judge 也是「明文」存您的帳號密碼。\n"
                                           "3. 我以我的人格擔保，不會使用您提供的資訊侵害您的權利。\n\n"
                                           "然後，附個[郭老 Online Judge 傳送門](" + config.URL + ")", parse_mode="Markdown",
                                           reply_markup=ReplyKeyboardMarkup(keyboard=[
                                               [KeyboardButton(text="回主畫面🏠")]
                                           ]))
        self.bot.sendMessage(self.chat_id, "\n原始碼被託管於 GitHub，網址如下：\n"
                                           "https://github.com/PinLin/kcoj_bot")