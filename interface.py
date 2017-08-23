#! /usr/bin/env python3

# necessary modules
import os, requests, telepot
from telepot.namedtuple import ReplyKeyboardMarkup, ReplyKeyboardRemove
from random import choice
# kCOJ API
import access
# configurations
import config, promote

class kuser:
    def __init__(self, chat_id, bot):
        self.chat_id = chat_id
        self.bot = bot
        self.username = ''
        self.password = ''
        self.status = '第一次用'
        self.question = '題外'
        self.api = access.kuser_api()

    def new_user(self):
        self.help_you()
        self.press_username()
    
    def press_username(self):
        self.status = '輸入學號'
        self.question = '題外'
        self.bot.sendMessage(self.chat_id, "請輸入您的學號：", reply_markup=ReplyKeyboardRemove())

    def press_password(self, text):
        self.status = '輸入密碼'
        self.question = '題外'
        self.username = text
        self.bot.sendMessage(self.chat_id, "輸入完可刪除訊息以策安全！\n"
                                           "請輸入您的密碼：", reply_markup=ReplyKeyboardRemove())

    def press_oldpassword(self):
        self.status = '舊的密碼'
        self.question = '題外'
        self.bot.sendMessage(self.chat_id, "請輸入要原本的舊密碼：",
            reply_markup=ReplyKeyboardMarkup(keyboard=[
                ["首頁🏠"]
            ], resize_keyboard=True))

    def press_newpassword(self, text):
        self.status = '修改密碼'
        self.question = '題外'
        if text != self.password:
            self.display_main()
        else:
            self.bot.sendMessage(self.chat_id, "使用此功能請務必小心！\n"
                                               "請輸入要設定的新密碼：", reply_markup=ReplyKeyboardRemove())
        
    def change_password(self, text):
        self.status = '正常使用'
        self.question = '題外'
        if text == "首頁🏠":
            self.display_main()
        else:
            self.password = text
            self.bot.sendMessage(self.chat_id, "修改成功" if self.api.change_password(self.password) == True else "修改失敗",
                reply_markup=ReplyKeyboardMarkup(keyboard=[
                    ["首頁🏠"]
                ], resize_keyboard=True))

    def login_kcoj(self, text):
        self.status = '正常使用'
        self.question = '題外'
        self.password = text
        self.bot.sendMessage(self.chat_id, "登入中...", reply_markup=ReplyKeyboardRemove())
        if self.check_online() == True:
            self.display_main()

    def fail_login(self):
        self.status = '正常使用'
        self.question = '題外'
        self.bot.sendMessage(self.chat_id, "哇...登入失敗，讓我們重新開始一次", reply_markup=ReplyKeyboardRemove())
        self.press_username()

    def check_online(self): # edit
        self.status = '正常使用'
        result = self.api.check_online()
        if result == None:
            self.question = '題外'
            self.bot.sendMessage(self.chat_id, "郭老 Online Judge 離線中！",
                reply_markup=ReplyKeyboardMarkup(keyboard=[
                    ["首頁🏠"]
                ], resize_keyboard=True))
            return False
        elif result == True:
            return True
        else:
            self.api.login_kcoj(self.username, self.password)
            if self.api.check_online() == False:
                self.fail_login()
                return False
            else:
                return True

    def logout_system(self):
        self.status = '正常使用'
        self.question = '題外'
        self.bot.sendMessage(self.chat_id, "您現在已經是登出的狀態。", reply_markup=ReplyKeyboardRemove())
        self.press_username()

    def display_main(self):
        self.status = '正常使用'
        self.question = '題外'
        q_dict = self.api.list_questions()
        q_str = ''
        for key in q_dict.keys():
            if q_dict[key][1] == '期限未到':
                q_str += "📗<b>" + key + "</b> (DL: " + q_dict[key][0] + ")\n [[" + q_dict[key][2] + "]]"
                q_str += "⚠️" if q_dict[key][2] == '未繳' else "✅"
                q_str += "  /question_" + key + "\n\n"
        self.bot.sendMessage(self.chat_id, "💁 <b>" + self.username + "</b> " + config.NAME + "\n"
                                           "➖➖➖➖➖\n"
                                           "📝<i>可繳交的作業</i>\n\n" + q_str + \
                                           "➖➖➖➖➖\n" + choice(promote.sentences),
                                           parse_mode='HTML',
                                           reply_markup=ReplyKeyboardMarkup(keyboard=[
                                               ["題庫📝"],
                                               ["登出🚪", "改密碼💱", "幫助📚"]
                                           ], resize_keyboard=True))

    def display_questions(self):
        self.status = '正常使用'
        self.question = '題外'
        q_dict = self.api.list_questions()
        q_str = ''
        for key in q_dict.keys():
            q_str += "📗" if q_dict[key][1] == '期限未到' else "📕"
            q_str += "<b>" + key + "</b> (DL: " + q_dict[key][0] + ")\n [[" + q_dict[key][2] + "]]"
            q_str += "⚠️" if q_dict[key][2] == '未繳' else "✅"
            q_str += "  /question_" + key + "\n\n"
        reply = self.bot.sendMessage(self.chat_id, "💁 <b>" + self.username + "</b> " + config.NAME + "\n"
                                                   "➖➖➖➖➖\n"
                                                   "📝<i>所有作業</i>\n\n" + q_str + \
                                                   "➖➖➖➖➖\n" + choice(promote.sentences),
                                                   parse_mode='HTML',
                                                   reply_markup=ReplyKeyboardMarkup(keyboard=[
                                                       ["首頁🏠", "更新🔃"],
                                                       ["登出🚪", "改密碼💱", "幫助📚"]
                                                   ], resize_keyboard=True))
        self.bot.sendMessage(self.chat_id, "點我到題庫頂", reply_to_message_id=reply['message_id'])

    def display_question(self, number):
        self.status = '查看題目'
        self.question = number
        content = self.api.show_question(number)
        q = self.api.list_questions()[number]
        q_str = "💁 *" + self.username + "* [" + config.NAME + "]\n"
        q_str += "➖➖➖➖➖\n"
        q_str += "📗" if q[1] == '期限未到' else "📕"
        q_str += "*" + number + "* (DL: " + q[0] + ")\n [[[" + q[2] + "]]]"
        q_str += "⚠️" if q[2] == '未繳' else "✅"
        reply = self.bot.sendMessage(self.chat_id, q_str + "\n\n```\n" + content + "\n```",
            parse_mode='Markdown',
            reply_markup=ReplyKeyboardMarkup(keyboard=[
                ["首頁🏠", "題庫📝"],
                ["交作業📮" if q[1] == '期限未到' else '', "看結果☑️" if q[2] == '已繳' else '', "通過者🌐"],
                ["登出🚪", "改密碼💱", "幫助📚"]
            ], resize_keyboard=True))
        self.bot.sendMessage(self.chat_id, "點我到題目頂", reply_to_message_id=reply['message_id'])

    def help_you(self):
        self.question = '題外'
        self.bot.sendMessage(self.chat_id, "這裡是 kC Online Judge Bot！\n"
                                           "可以簡稱 kCOJ Bot，目前定居於 [" + config.NAME + "]\n"
                                           "作用是讓大家可以方便的透過我使用郭老程設課的 Online Judge\n"
                                           "➡️[傳送門](" + config.URL + ")\n"
                                           "操作很簡單（？）\n\n"
                                           "還是稍微提幾個需要注意的地方：\n"
                                           "1. 📗代表還可以繳交的作業，📕代表已經不能繳交的作業\n"
                                           "2. ⚠️代表還沒有繳交的作業，✅代表已經繳交的作業\n"
                                           "3. 其實在查看題目的畫面就可以用「拖曳」的方式 *上傳作業📮*\n"
                                           "4. *刪除作業⚔️* 的功能被放在 *上傳作業📮* 裡面\n"
                                           "5. 學號與密碼將以「明文」方式儲存\n"
                                           "6. 郭老的 Online Judge 其實也是以「明文」方式儲存您的帳號密碼\n"
                                           "7. 我以我的人格擔保，不會使用您提供的資訊侵害您的權利\n\n"
                                           "本專案授權方式採用 GPLv3\n"
                                           "非常歡迎發 issue 送 PR owooo\n"
                                           "原始碼被託管於 GitHub，大大們有空的話可以按個星星支持一下> </\n"
                                           "網址如下：\n"
                                           "[https://github.com/PinLin/kcoj_bot]\n\n",
                                           parse_mode='Markdown',
                                           reply_markup=ReplyKeyboardMarkup(keyboard=[
                                               ["首頁🏠"],
                                               ["登出🚪", "改密碼💱", "幫助📚"]
                                           ], resize_keyboard=True) if self.status == '正常使用' else ReplyKeyboardRemove())

    def upload_answer(self):
        self.status = '上傳答案'
        q = self.api.list_questions()[self.question]
        q_str = "💁 <b>" + self.username + "</b> " + config.NAME + "\n"
        q_str += "➖➖➖➖➖\n"
        q_str += "📗" if q[1] == '期限未到' else "📕"
        q_str += "<b>" + self.question + "</b> (DL: " + q[0] + ")\n [[" + q[2] + "]]"
        q_str += "⚠️" if q[2] == '未繳' else "✅"
        self.bot.sendMessage(self.chat_id, q_str + "\n\n現在請把你的程式碼讓我看看（請別超過 20 MB）\n"
                                                   "可以使用「文字訊息」或是「傳送檔案」的方式", parse_mode='HTML',
                                                   reply_markup=ReplyKeyboardMarkup(keyboard=[
                                                       ["刪除作業⚔️"] if self.api.list_questions()[self.question][2] == '已繳' else [],
                                                       ["首頁🏠", "回題目📜"]
                                                   ], resize_keyboard=True))

    def send_answer(self, text, file_id):
        self.status = '正常使用'
        if text != '':
            if text == '首頁🏠':
                if self.check_online() == True:
                    self.display_main()
                    return
            elif text == '回題目📜':
                if self.check_online() == True:
                    self.display_question(self.question)
                    return
            elif text == '刪除作業⚔️':
                self.bot.sendMessage(self.chat_id, "移除成功" if self.api.delete_answer(self.question) == True else "移除失敗",
                    reply_markup=ReplyKeyboardMarkup(keyboard=[
                        ["首頁🏠", "回題目📜"],
                        ["登出🚪", "改密碼💱", "幫助📚"]
                    ], resize_keyboard=True))
                return
            else:
                f = open(self.username + self.question + '.c', 'w')
                f.write(text)
                f.close()
        else:
            self.bot.download_file(file_id, self.username + self.question + '.c')
        self.api.delete_answer(self.question)
        if self.api.upload_answer(self.question, self.username + self.question + '.c') == True:
            self.bot.sendMessage(self.chat_id, "上傳成功",
                reply_markup=ReplyKeyboardMarkup(keyboard=[
                    ["首頁🏠", "回題目📜"],
                    ["看結果☑️"],
                    ["登出🚪", "改密碼💱", "幫助📚"]
                ], resize_keyboard=True))
        else:
            self.bot.sendMessage(self.chat_id, "上傳失敗",
                reply_markup=ReplyKeyboardMarkup(keyboard=[
                    ["首頁🏠", "回題目📜"],
                    ["登出🚪", "改密碼💱", "幫助📚"]
                ], resize_keyboard=True))
        os.remove(self.username + self.question + '.c')    
    
    def fail_send(self):
        self.status = '正常使用'
        self.bot.sendMessage(self.chat_id, "檔案不能超過 20 MB！上傳失敗",
            reply_markup=ReplyKeyboardMarkup(keyboard=[
                ["首頁🏠", "回題目📜"],
                ["登出🚪", "改密碼💱", "幫助📚"]
            ], resize_keyboard=True))

    def list_passers(self):
        self.status = '正常使用'
        q = self.api.list_questions()[self.question]
        q_str = "💁 <b>" + self.username + "</b> " + config.NAME + "\n"
        q_str += "➖➖➖➖➖\n"
        q_str += "📗" if q[1] == '期限未到' else "📕"
        q_str += "<b>" + self.question + "</b> (DL: " + q[0] + ")\n [[" + q[2] + "]]"
        q_str += "⚠️" if q[2] == '未繳' else "✅"
        q_str += "<code>\n"
        for passer in self.api.list_passers(self.question):
            q_str += "\n" + passer
        reply = self.bot.sendMessage(self.chat_id, q_str + "</code>", 
            parse_mode='HTML',
            reply_markup=ReplyKeyboardMarkup(keyboard=[
                ["首頁🏠", "回題目📜"],
                ["登出🚪", "改密碼💱", "幫助📚"]
            ], resize_keyboard=True))
        self.bot.sendMessage(self.chat_id, "點我到名單頂", reply_to_message_id=reply['message_id'])

    def list_results(self):
        self.status = '正常使用'
        q = self.api.list_questions()[self.question]
        q_str = "💁 <b>" + self.username + "</b> " + config.NAME + "\n"
        q_str += "➖➖➖➖➖\n"
        q_str += "📗" if q[1] == '期限未到' else "📕"
        q_str += "<b>" + self.question + "</b> (DL: " + q[0] + ")\n"
        for result in self.api.list_results(self.question, self.username):
            q_str += "\n測試編號 <code>" + result[0] + "</code>："
            q_str += "✔️ " if result[1] == '通過測試' else "❌ "
            q_str += result[1]
        self.bot.sendMessage(self.chat_id, q_str, 
            parse_mode='HTML', 
            reply_markup=ReplyKeyboardMarkup(keyboard=[
                ["首頁🏠", "回題目📜"],
                ["交作業📮" if q[1] == '期限未到' else '', "通過者🌐"],
                ["登出🚪", "改密碼💱", "幫助📚"]
            ], resize_keyboard=True))