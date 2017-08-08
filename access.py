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
        payload = {'name': username, 
                   'passwd': password,
                   'rdoCourse': 1}
        return self.session.post(config.URL + '/Login', data=payload)
    # check online status
    def check_online(self):
        response = self.session.get(config.URL + '/TopMenu')
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.find('a').get_text() == '線上考試'
    # list all questions, deadline and hand-in status
    def list_questions(self):
        questions = {}
        response = self.session.get(config.URL + '/HomeworkBoard')
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
    # show the content of the question
    def show_question(self, number):
        response = self.session.get(config.URL + '/showHomework', params={'hwId': number})
        soup = BeautifulSoup(response.text, 'html.parser')
        content = str(soup.find('body'))
        content = content.replace('<body alink="#FFCCFF" bgcolor="#000000" link="#00FFFF" text="#FFFFFF" vlink="#CCFF33">\n', '')
        content = content.replace('<!DOCTYPE html>\n\n', '').replace('<meta charset="utf-8"/>\n', '')
        content = content.replace('<input onclick="history.go( -1 );return true;" type="button" value="上一頁"/>', '')
        content = content.replace('<a href="upLoadHw?hwId=' + number + '">  繳交作業 </a>', '')
        content = content.replace('</body>', '').replace('<br/>       ', '\n').replace('<br/>', '\n').replace('     ', '')
        return content
    # list passers of the question
    def list_passers(self, number):
        passers = []
        response = self.session.get(config.URL + '/success.jsp', params={'HW_ID': number})
        soup = BeautifulSoup(response.text, 'html.parser')
        for tr in soup.find_all('tr'):
            passer = tr.get_text().replace('\n', '')
            if passer != '學號':
                passers += [passer]
        return passers
    def list_results(self, number):
        results = []
        response = self.session.get(config.URL + '/CheckResult.jsp', params={'questionID': number, 'studentID': self.username})
        soup = BeautifulSoup(response.text, 'html.parser')
        for tr in soup.find_all('tr'):
            td = tr.find('td')
            if td.get_text() != '測試編號':
                results += [(td.get_text(), tr.find_all('td')[1].get_text())]
        return results
    # delete the answer of the question
    def delete_answer(self, number):
        response = self.session.get(config.URL + '/delHw', params={'title': number})
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.find('body').get_text().replace('\n', '') == 'delete success'
    # hand in a answer
    def upload_answer(self, number):
        self.session.get(config.URL + '/upLoadHw', params={'hwId': number})
        response = self.session.post(config.URL + '/upLoadFile')
        return response.text # unavailable

    def change_password(self, password):
        payload = {'pass': password, 
                   'submit': 'sumit'}
        response = self.session.post(config.URL + '/changePasswd', data=payload)
        soup = BeautifulSoup(response.text, 'html.parser')
        return str(soup.find('body')).split()[-2] == 'Success'

# for debug
def main():
    pass

if __name__ == '__main__':
    main()