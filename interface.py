#! /usr/bin/env python3

# necessary modules
import os, requests, telepot
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
        self.question = '題外'
        self.api = access.kuser_api()

    def new_user(self):
        self.bot.sendMessage(self.chat_id, "是初次見面的朋友呢，設定一下吧！", reply_markup=ReplyKeyboardRemove())
        self.press_username()
    
    def press_username(self):
        self.status = '輸入學號'
        self.question = '題外'
        self.bot.sendMessage(self.chat_id, "請輸入您的學號：", reply_markup=ReplyKeyboardRemove())

    def press_password(self, text):
        self.status = '輸入密碼'
        self.question = '題外'
        self.username = text
        self.bot.sendMessage(self.chat_id, "輸入完可刪除訊息以策安全！\n請輸入您的密碼：", reply_markup=ReplyKeyboardRemove())

    def press_oldpassword(self):
        self.status = '舊的密碼'
        self.question = '題外'
        self.bot.sendMessage(self.chat_id, "請輸入要原本的舊密碼：",
                                           reply_markup=ReplyKeyboardMarkup(keyboard=[
                                               [KeyboardButton(text="回主畫面🏠")]
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
        if text == "回主畫面🏠":
            self.display_main()
        else:
            self.password = text
            self.bot.sendMessage(self.chat_id, "修改成功" if self.api.change_password(self.password) == True else "修改失敗",
                reply_markup=ReplyKeyboardMarkup(keyboard=[
                    [KeyboardButton(text="回主畫面🏠")]
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

    def check_online(self):
        self.status = '正常使用'
        if self.api.login_kcoj(self.username, self.password) == None:
            self.question = '題外'
            self.bot.sendMessage(self.chat_id, "郭老網站離線中！",
                                           reply_markup=ReplyKeyboardMarkup(keyboard=[
                                               [KeyboardButton(text="回主畫面🏠")]
                                           ], resize_keyboard=True))
            return False
        elif self.api.check_online() == True:
            return True
        else:
            self.fail_login()
            return False

    def logout_system(self):
        self.status = '正常使用'
        self.question = '題外'
        self.bot.sendMessage(self.chat_id, "您現在已經是登出的狀態。", reply_markup=ReplyKeyboardRemove())
        self.press_username()

    def display_main(self):
        self.status = '正常使用'
        self.question = '題外'
        q_dict = self.api.list_questions()
        q_available = "📝<i>可繳交的作業</i>\n\n"
        q_unavailable = "📝<i>沒有可繳交的作業哦！</i>\n"
        if q_dict == {}:
            q_str = q_unavailable
        else:
            q_str = q_available
            for key in q_dict.keys():
                if q_dict[key][1] == '期限未到':
                    q_str += "📗<b>" + key + "</b> (到 " + q_dict[key][0] + ")\n [[" + q_dict[key][2] + "]] /question_" + key + "\n\n"
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
        self.question = '題外'
        q_dict = self.api.list_questions()
        q_str = ''
        for key in q_dict.keys():
            q_str += "📗" if q_dict[key][1] == '期限未到' else "📕"
            q_str += "<b>" + key + "</b> (到 " + q_dict[key][0] + ")\n [[" + q_dict[key][2] + "]] /question_" + key + "\n\n"
        self.bot.sendMessage(self.chat_id, "💁 <b>" + self.username + "</b> /logout\n"
                                           "➖➖➖➖➖\n📝<i>所有作業</i>\n\n" + q_str + "➖➖➖➖➖\n"
                                           "你今天寫扣了嗎？", 
                                           parse_mode='HTML',
                                           reply_markup=ReplyKeyboardMarkup(keyboard=[
                                               [KeyboardButton(text="回主畫面🏠"), KeyboardButton(text="重新載入🔃")],
                                               [KeyboardButton(text="登出帳號🚪"), KeyboardButton(text="修改密碼💱"), KeyboardButton(text="提供幫助📚")]
                                           ]))

    def display_question(self, number):
        self.status = '查看題目'
        self.question = number
        content = self.api.show_question(number)
        q = self.api.list_questions()[number]
        q_str = "📗" if q[1] == '期限未到' else "📕"
        q_str += "<b>" + number + "</b> (到 " + q[0] + ")\n [[" + q[2] + "]]\n"

        k = [[KeyboardButton(text="回主畫面🏠"), KeyboardButton(text="回到題庫📝")]]
        k2 = []
        if q[1] == '期限未到':
            k2 += [KeyboardButton(text="上傳答案📮")]
        if q[2] == '已繳': 
            k2 += [KeyboardButton(text="查看結果☑️")]
        k2 += [KeyboardButton(text="通過名單🌐")]
        k += [k2]
        k += [[KeyboardButton(text="登出帳號🚪"), KeyboardButton(text="修改密碼💱"), KeyboardButton(text="提供幫助📚")]]

        self.bot.sendMessage(self.chat_id, q_str + "\n\n<code>" + content + "</code>",
            parse_mode='HTML',
            reply_markup=ReplyKeyboardMarkup(keyboard=k))

    def help_you(self):
        self.status = '正常使用'
        self.question = '題外'
        self.bot.sendMessage(self.chat_id, "這裡是 kC Online Judge Bot！\n"
                                           "可以簡稱我為 kCOJ Bot，目前定居於 `@kcoj_bot`\n"
                                           "作用是讓大家可以方便的透過我使用郭老程設課的 Online Judge\n"
                                           "操作很簡單（？）我想大家應該都不會有問題吧～\n\n"
                                           "<b>不過還是稍微提幾個需要注意的地方：</b>\n"
                                           "1. 太久沒有用點下去反應會有點慢，可能要等一下\n"
                                           "1. 📗代表還可以繳交的作業，📕代表已經不能繳交的作業\n"
                                           "3. 其實在查看題目的畫面就可以用「拖曳」的方式 上傳作業📮\n"
                                           "2. 刪除作業⚔️ 的功能被放在 上傳作業📮 裡面\n"
                                           "3. 學號與密碼將以「明文」方式儲存在記憶體裡，不會儲存在我的硬碟中\n"
                                           "4. 郭老的 Online Judge 其實也是以「明文」的方式存您的帳號密碼哦\n"
                                           "5. 我以我的人格擔保，不會使用您提供的資訊侵害您的權利。\n\n"
                                           "然後，附上 [郭老 Online Judge 傳送門](" + config.URL + ")", parse_mode='Markdown',
                                           reply_markup=ReplyKeyboardMarkup(keyboard=[
                                               [KeyboardButton(text="回主畫面🏠")],
                                               [KeyboardButton(text="登出帳號🚪"), KeyboardButton(text="修改密碼💱"), KeyboardButton(text="提供幫助📚")]
                                           ]))
        self.bot.sendMessage(self.chat_id, "\n原始碼被託管於 GitHub，網址如下：\n"
                                           "https://github.com/PinLin/kcoj_bot")
    def upload_answer(self):
        self.status = '上傳答案'
        q = self.api.list_questions()[self.question]
        q_str = "📗" if q[1] == '期限未到' else "📕"
        q_str += "<b>" + self.question + "</b> (到 " + q[0] + ")\n [[" + q[2] + "]]\n"
        self.bot.sendMessage(self.chat_id, q_str + "\n現在請把你的程式碼讓我看看（請別超過 20 MB）\n"
                                           "可以使用「文字訊息」或是「傳送檔案」的方式", parse_mode='HTML',
                                           reply_markup=ReplyKeyboardMarkup(keyboard=[
                                               [KeyboardButton(text="刪除作業⚔️")],
                                               [KeyboardButton(text="回主畫面🏠"), KeyboardButton(text="回到題目📜")]] if self.api.list_questions()[self.question][2] == '已繳' else [
                                               [KeyboardButton(text="回主畫面🏠"), KeyboardButton(text="回到題目📜")]
                                           ], resize_keyboard=True))

    def send_answer(self, text, file_id):
        self.status = '正常使用'
        if text != '':
            if text == '回主畫面🏠':
                if self.check_online() == True:
                    self.display_main()
                    return
            elif text == '回到題目📜':
                if self.check_online() == True:
                    self.display_question(self.question)
                    return
            elif text == '刪除作業⚔️':
                self.bot.sendMessage(self.chat_id, "移除成功" if self.api.delete_answer(self.question) == True else "移除失敗",
                    reply_markup=ReplyKeyboardMarkup(keyboard=[
                        [KeyboardButton(text="回主畫面🏠"), KeyboardButton(text="回到題目📜")],
                        [KeyboardButton(text="登出帳號🚪"), KeyboardButton(text="修改密碼💱"), KeyboardButton(text="提供幫助📚")]
                    ]))
                return
            else:
                if os.path.exists('answers') == False:
                    os.mkdir('answers')
                f = open('answers/' + self.username + self.question + '.c', 'w')
                f.write(text)
                f.close()
        else:
            self.bot.download_file(file_id, 'answers/' + self.username + self.question + '.c')
        self.api.delete_answer(self.question)
        if self.api.upload_answer(self.question, 'answers/' + self.username + self.question + '.c') == True:
            self.bot.sendMessage(self.chat_id, "上傳成功",
                reply_markup=ReplyKeyboardMarkup(keyboard=[
                    [KeyboardButton(text="回主畫面🏠"), KeyboardButton(text="回到題目📜")],
                    [KeyboardButton(text="查看結果☑️")],
                    [KeyboardButton(text="登出帳號🚪"), KeyboardButton(text="修改密碼💱"), KeyboardButton(text="提供幫助📚")]
                ]))
        else:
            self.bot.sendMessage(self.chat_id, "上傳失敗",
                reply_markup=ReplyKeyboardMarkup(keyboard=[
                    [KeyboardButton(text="回主畫面🏠"), KeyboardButton(text="回到題目📜")],
                    [KeyboardButton(text="登出帳號🚪"), KeyboardButton(text="修改密碼💱"), KeyboardButton(text="提供幫助📚")]
                ]))
        os.remove('answers/' + self.username + self.question + '.c')    
    
    def fail_send(self):
        self.status = '正常使用'
        self.bot.sendMessage(self.chat_id, "檔案不能超過 20 MB！上傳失敗",
                                           reply_markup=ReplyKeyboardMarkup(keyboard=[
                                               [KeyboardButton(text="回主畫面🏠"), KeyboardButton(text="回到題目📜")]
                                           ]))
    def list_passers(self):
        self.status = '正常使用'
        q = self.api.list_questions()[self.question]
        q_str = "📗" if q[1] == '期限未到' else "📕"
        q_str += "<b>" + self.question + "</b> (到 " + q[0] + ")\n [[" + q[2] + "]]\n<code>"
        for passer in self.api.list_passers(self.question):
            q_str += "\n" + passer
        self.bot.sendMessage(self.chat_id, q_str + "</code>", parse_mode='HTML',
                                           reply_markup=ReplyKeyboardMarkup(keyboard=[
                                               [KeyboardButton(text="回主畫面🏠"), KeyboardButton(text="回到題目📜")],
                                               [KeyboardButton(text="登出帳號🚪"), KeyboardButton(text="修改密碼💱"), KeyboardButton(text="提供幫助📚")]
                                           ]))

    def list_results(self):
        self.status = '正常使用'
        q = self.api.list_questions()[self.question]
        q_str = "📗" if q[1] == '期限未到' else "📕"
        q_str += "<b>" + self.question + "</b> (到 " + q[0] + ")\n"
        for result in self.api.list_results(self.question, self.username):
            q_str += "\n測試編號 <code>" + result[0] + "</code>："
            q_str += "✔️ " if result[1] == '通過測試' else "❌ "
            q_str += result[1]
        k = [[KeyboardButton(text="回主畫面🏠"), KeyboardButton(text="回到題目📜")]]
        k2 = []
        if q[1] == '期限未到':
            k2 += [KeyboardButton(text="上傳答案📮")]
        k2 += [KeyboardButton(text="通過名單🌐")]
        k += [k2]
        k += [[KeyboardButton(text="登出帳號🚪"), KeyboardButton(text="修改密碼💱"), KeyboardButton(text="提供幫助📚")]]
        self.bot.sendMessage(self.chat_id, q_str, parse_mode='HTML', reply_markup=ReplyKeyboardMarkup(keyboard=k))