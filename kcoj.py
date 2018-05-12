# modules
import requests
from bs4 import BeautifulSoup

class KCOJ:
    def __init__(self, url):
        self.url = url
        self.session = requests.Session()
    # login KCOJ
    def login(self, username, password, course):
        try:
            payload = {'name': username, 
                       'passwd': password,
                       'rdoCourse': course}
            return self.session.post(self.url + '/Login', data=payload, timeout=0.5, verify=False)
        except requests.exceptions.Timeout:
            return None

    # check online status
    def check_online(self):
        try:
            response = self.session.get(self.url + '/TopMenu', timeout=0.5, verify=False)
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup.find('a').get_text().strip() == '線上考試'
        except requests.exceptions.Timeout:
            return None

    # list all questions, deadline and hand-in status
    def list_questions(self):
        try:
            questions = {}
            response = self.session.get(self.url + '/HomeworkBoard', timeout=0.5, verify=False)
            soup = BeautifulSoup(response.text, 'html.parser')
            for tag in soup.find_all('tr'):
                if tag.find('a') == None:
                    continue
                else:
                    number = tag.find('a').get_text().strip()
                    deadline = tag.find_all('td')[3].get_text().strip()
                    submit = "期限已到" if tag.find_all('td')[4].get_text().strip() == "期限已過" else "期限未到"
                    status = tag.find_all('td')[6].get_text().strip()
                    language = tag.find_all('td')[5].get_text().strip()
                    questions[number] = (deadline, submit, status, language)
            return questions
        except requests.exceptions.Timeout:
            return {'Timeout':('Timeout', 'Timeout', 'Timeout', 'Timeout')}

    # show the content of the question
    def show_question(self, number):
        try:
            response = self.session.get(self.url + '/showHomework', params={'hwId': number}, timeout=0.5, verify=False)
            soup = BeautifulSoup(response.text, 'html.parser')
            raw = soup.find('body').get_text().replace('繳交作業', '').strip()
            content = ''
            for s in raw.split('\r'):
                content += s.strip() + '\n'
            return content
        except requests.exceptions.Timeout:
            return 'Timeout'

    # list passers of the question
    def list_passers(self, number):
        try:
            passers = []
            response = self.session.get(self.url + '/success.jsp', params={'HW_ID': number}, timeout=0.5, verify=False)
            soup = BeautifulSoup(response.text, 'html.parser')
            for tr in soup.find_all('tr'):
                passer = tr.get_text().replace('\n', '').strip()
                if passer != '學號':
                    passers += [passer]
            return passers
        except requests.exceptions.Timeout:
            return ['Timeout']

    # list results of the question
    def list_results(self, number, username):
        try:
            results = []
            response = self.session.get(self.url + '/CheckResult.jsp', params={'questionID': number, 'studentID': username}, timeout=0.5, verify=False)
            soup = BeautifulSoup(response.text, 'html.parser')
            for tr in soup.find_all('tr'):
                td = tr.find('td')
                if td.get_text().strip() != '測試編號':
                    results += [(td.get_text().strip(), tr.find_all('td')[1].get_text().strip())]
            return results
        except requests.exceptions.Timeout:
            return ['Timeout', 'Timeout']

    # change password
    def change_password(self, password):
        try:
            payload = {'pass': password, 
                       'submit': 'sumit'}
            response = self.session.post(self.url + '/changePasswd', data=payload, timeout=0.5, verify=False)
            soup = BeautifulSoup(response.text, 'html.parser')
            return str(soup.find('body')).split()[-2].strip() == 'Success'
        except requests.exceptions.Timeout:
            return False

    # delete the answer of the question
    def delete_answer(self, number):
        try:
            response = self.session.get(self.url + '/delHw', params={'title': number}, timeout=0.5, verify=False)
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup.find('body').get_text().replace('\n', '').strip() == 'delete success'
        except requests.exceptions.Timeout:
            return False

    # hand in a answer
    def upload_answer(self, number, file_path):
        try:
            self.session.get(self.url + '/upLoadHw', params={'hwId': number}, timeout=0.5, verify=False)
            response = self.session.post(self.url + '/upLoadFile', 
                data={'FileDesc': 'Send from kcoj_bot'},
                files={'hwFile': open(file_path, 'rb')},
                timeout=0.5)
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup.find('body').get_text().strip() != '您沒有上傳檔案 請重新操作'
        except requests.exceptions.Timeout:
            return False