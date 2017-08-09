#! /usr/bin/env python3

# necessary modules
import requests
from bs4 import BeautifulSoup
from pprint import pprint
# configurations
import config

class kuser_api:
    def __init__(self):
        self.session = requests.Session()
    # login kCOJ
    def login_kcoj(self, username, password):
        try:
            payload = {'name': username, 
                       'passwd': password,
                       'rdoCourse': 1}
            return self.session.post(config.URL + '/Login', data=payload, timeout=0.1)
        except requests.exceptions.Timeout:
            return None

    # check online status
    def check_online(self):
        try:
            response = self.session.get(config.URL + '/TopMenu', timeout=0.1)
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup.find('a').get_text() == '線上考試'
        except requests.exceptions.Timeout:
            return True

    # list all questions, deadline and hand-in status
    def list_questions(self):
        try:
            questions = {}
            response = self.session.get(config.URL + '/HomeworkBoard', timeout=0.5)
            soup = BeautifulSoup(response.text, 'html.parser')
            for tag in soup.find_all('tr'):
                if tag.find('a') == None:
                    continue
                else:
                    number = tag.find('a').get_text()
                    deadline = tag.find_all('td')[3].get_text()
                    submit = "期限已到" if tag.find_all('td')[4].get_text().strip() == "期限已過" else "期限未到"
                    status = tag.find_all('td')[5].get_text().strip()
                    questions[number] = (deadline, submit, status)
            return questions
        except requests.exceptions.Timeout:
            return {'Timeout':('Timeout', 'Timeout', 'Timeout')}

    # show the content of the question
    def show_question(self, number):
        try:
            response = self.session.get(config.URL + '/showHomework', params={'hwId': number}, timeout=0.1)
            soup = BeautifulSoup(response.text, 'html.parser')
            content = str(soup.find('body'))
            content = content.replace('<body alink="#FFCCFF" bgcolor="#000000" link="#00FFFF" text="#FFFFFF" vlink="#CCFF33">\n', '')
            content = content.replace('<!DOCTYPE html>\n\n', '').replace('<meta charset="utf-8"/>\n', '')
            content = content.replace('<input onclick="history.go( -1 );return true;" type="button" value="上一頁"/>', '')
            content = content.replace('<a href="upLoadHw?hwId=' + number + '">  繳交作業 </a>', '')
            content = content.replace('</body>', '').replace('<br/>       ', '\n').replace('<br/>', '\n').replace('     ', '')
            return content
        except requests.exceptions.Timeout:
            return 'Timeout'

    # list passers of the question
    def list_passers(self, number):
        try:
            passers = []
            response = self.session.get(config.URL + '/success.jsp', params={'HW_ID': number}, timeout=0.5)
            soup = BeautifulSoup(response.text, 'html.parser')
            for tr in soup.find_all('tr'):
                passer = tr.get_text().replace('\n', '')
                if passer != '學號':
                    passers += [passer]
            return passers
        except requests.exceptions.Timeout:
            return ['Timeout']

    # list results of the question
    def list_results(self, number, username):
        try:
            results = []
            response = self.session.get(config.URL + '/CheckResult.jsp', params={'questionID': number, 'studentID': username}, timeout=0.1)
            soup = BeautifulSoup(response.text, 'html.parser')
            for tr in soup.find_all('tr'):
                td = tr.find('td')
                if td.get_text() != '測試編號':
                    results += [(td.get_text(), tr.find_all('td')[1].get_text())]
            return results
        except requests.exceptions.Timeout:
            return ['Timeout', 'Timeout']

    # change password
    def change_password(self, password):
        try:
            payload = {'pass': password, 
                       'submit': 'sumit'}
            response = self.session.post(config.URL + '/changePasswd', data=payload, timeout=0.1)
            soup = BeautifulSoup(response.text, 'html.parser')
            return str(soup.find('body')).split()[-2] == 'Success'
        except requests.exceptions.Timeout:
            return False

    # delete the answer of the question
    def delete_answer(self, number):
        try:
            response = self.session.get(config.URL + '/delHw', params={'title': number}, timeout=0.1)
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup.find('body').get_text().replace('\n', '') == 'delete success'
        except requests.exceptions.Timeout:
            return False

    # hand in a answer
    def upload_answer(self, number, file_path):
        try:
            self.session.get(config.URL + '/upLoadHw', params={'hwId': number}, timeout=0.1)
            response = self.session.post(config.URL + '/upLoadFile', 
                data={'FileDesc': 'Send from kcoj_bot'},
                files={'hwFile': open(file_path, 'rb')},
                timeout=0.1)
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup.find('body').get_text().strip() != '您沒有上傳檔案 請重新操作'
        except requests.exceptions.Timeout:
            return False

# for debug
def main():
    pass

if __name__ == '__main__':
    main()