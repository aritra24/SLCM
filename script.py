from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from html import unescape
from time import sleep
import getpass
import json
from datetime import datetime

from pyvirtualdisplay import Display


class SLCM():
	username = ''
	password = ''
	timeTable = {}
	semester = None
	grades = {}
	subjectList = {}
	browser = ''
	wait = ''
	baseSite = 'http://slcm.manipal.edu/'
	gradeSheet = 'GradeSheet.aspx'
	studentTimeTable = 'StudentTimeTable.aspx'

	def __init__(self,username = 'put_username_here', password = 'put_password_here'):
		self.username = username
		self.password = password
		capa = DesiredCapabilities.CHROME
		capa['pageLoadStrategy'] = 'none'
		self.browser = webdriver.Chrome(desired_capabilities=capa)
		self.wait = WebDriverWait(self.browser, 20)

	def login(self):
		self.load(self.baseSite,'btnLogin')
		self.browser.find_element_by_id('txtUserid').send_keys(self.username)
		self.browser.find_element_by_id('txtpassword').send_keys(self.password)
		self.browser.find_element_by_id('btnLogin').click()


	def load_marks(self,sem = None):
		semlist=['I','II','III','IV','V','VI','VII','VIII']
		self.load(self.baseSite+self.gradeSheet,'ContentPlaceHolder1_grvGradeSheet')
		subjects={}
		select = Select(self.browser.find_element_by_id('ContentPlaceHolder1_ddlSemester'))
		if not self.semester:
			self.semester = semlist.index(select.first_selected_option.text)+1
		if not sem:
			sem = self.semester
		select.select_by_visible_text(semlist[sem-1])
		sleep(1)
		count = self.browser.execute_script("return $(' #ContentPlaceHolder1_grvGradeSheet tr').length;")-1
		self.grades[sem]={}
		try:
			for i in range(count):
				subjects[self.get_val_id('ContentPlaceHolder1_grvGradeSheet_lblSubject_'+str(i))] = self.get_val_id('ContentPlaceHolder1_grvGradeSheet_lblGrade_'+str(i))
			self.grades[sem]['scores'] = subjects
			self.grades[sem]['success'] = True
		except:
			self.grades[sem]['scores'] = None
			self.grades[sem]['success'] = False
		finally:
			return self.grades[sem]

	def load_subject_list(self, sem = None):
		semlist=['I','II','III','IV','V','VI','VII','VIII']
		self.load(self.baseSite+self.gradeSheet,'ContentPlaceHolder1_grvGradeSheet')
		select = Select(self.browser.find_element_by_id('ContentPlaceHolder1_ddlSemester'))
		if not self.semester:
			self.semester = semlist.index(select.first_selected_option.text) + 1
		if not sem:
			sem = self.semester
		if sem not in self.subjectList:
			self.subjectList[sem]={}
			self.subjectList[sem]['subjects'] = []
		select.select_by_visible_text(semlist[sem-1])
		sleep(1)
		count = self.browser.execute_script("return $(' #ContentPlaceHolder1_grvGradeSheet tr').length;")-1
		try:
			for i in range(count):
				self.subjectList[sem]['subjects'].append(self.get_val_id('ContentPlaceHolder1_grvGradeSheet_lblSubject_'+str(i)))
			self.subjectList[sem]['success'] = True
		except:
			self.subjectList[sem]['success'] = False
			print("failed")
		finally:
			return self.subjectList[sem]

	def get_time_table(self):
		self.timeTable = json.loads(timeTable)

	def get_class(self):
		today = 1+(datetime.today().weekday() + 2)%7
		self.browser.execute_script('window.stop();')
		self.browser.get(self.baseSite+self.studentTimeTable)
		self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'.' + 'fc-bg')))
		sleep(2)
		basicFormat = '//*[@id="calendar"]/div[2]/div/table/tbody/tr/td/div[2]/div/div[3]/table/tbody/tr/td['+str(today)+']/div/div[2]/a[1]/div[1]/'
		try:
			time = self.browser.find_element_by_xpath(basicFormat+'div[1]/span').get_attribute('innerHTML')
			print(time)
			subject = self.browser.find_element_by_xpath(basicFormat+'div[2]').text.split(',')[0]
			print(subject)
		except Exception as e:
			time = None
			subject = None
			print("No class today! yay!")
		finally:
			pass
		return {'time' : time, 'subject': subject}

	def attendance(self,subject):
		print("Do Stuff")

	def load(self, url,id = None,ch = '#'):
		if id:
			self.browser.execute_script('window.stop();')
		self.browser.get(url)
		if id:
			self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,ch + id)))
			self.browser.execute_script('window.stop();')

	def get_val_id(self,id):
		return unescape(self.browser.find_element_by_id(id).text)

	def get_val_xpath(self,xpath):
		return unescape(self.browser.find_element_by_xpath(xpath).text)

	def close(self):
		self.browser.close()


if __name__ == '__main__':
	username = input("Username :")
	password = getpass.getpass("Password :")
	display = Display(visible=0, size=(800,600))	
	display.start()
	if username !='' and password!='':
		slcm = SLCM(username, password)
	else:
		slcm = SLCM()
	slcm.login()
	slcm.load_marks(4)
	slcm.load_subject_list()
	print(json.dumps(slcm.subjectList, indent=1))
	slcm.get_class()
	slcm.close()
	display.stop()