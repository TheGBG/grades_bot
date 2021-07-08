import time
import pandas as pd
from selenium.webdriver.chrome.options import Options
import yaml

from pathlib import Path
from selenium import webdriver


# Gather keys
with open('credentials.yml', 'r') as file:
    credentials = yaml.safe_load(file)

LINK = credentials['LINK']
USERNAME = credentials['USERNAME']
PASSWORD = credentials['PASSWORD']

# It needs to gather your keys the first time
if USERNAME is None:
    
    print('Please, type in your CUNEF email')
    USERNAME = input()
    credentials['USERNAME'] = USERNAME
    
    print('Now type your password')
    PASSWORD = input()
    credentials['PASSWORD'] = PASSWORD
    
    with open ('credentials.yml', 'w') as file:
        yaml.safe_dump(credentials, file)
    
    
    print("Credentials saved. Next time you won't have to provide them")


# Shut down harmless error msg
options = Options()
options.add_experimental_option('excludeSwitches', ['enable-logging'])

# Path to chrome driver, it has to be updated and match your Chrome 
# browser version
browser = webdriver.Chrome('chromedriver/chromedriver.exe', options=options)

# Set max size to avoid getting into mobile version
browser.set_window_size(1024, 600)
browser.maximize_window()


# --------------------------- Get grades -------------------------------------

# Goes to page and uses yout keys to get inside
browser.get(LINK)

user = browser.find_element_by_id('txtUsuario')
user.send_keys(USERNAME)

password = browser.find_element_by_id('txtContrasena')
password.send_keys(PASSWORD)

print('Gettin access...')

login = browser.find_element_by_id('btnEntrar')
login.click()

# Just in case your network is not fast enough
time.sleep(5)

print('Access granted')


# First menu 
academic_info = browser.find_element_by_css_selector(
    
    '#nav > ul > li:nth-child(2)'
    
    )

academic_info.click()

time.sleep(5)

print('Loading grades...')

 
grades = browser.find_element_by_id('ctl00_calificaciones')
grades.click()

# Name of each subject
def get_subject_name(n):
    
    name = browser.find_element_by_css_selector(
        
        f'#ctl00_ContentPlaceHolder1_RadGrid1_ctl00 > tbody > tr:nth-child({n}) > td:nth-child(4) > p'
        
        )
    
    return name.text
    
subject_names = [get_subject_name(i) for i in range(3, 60, 2)]

def get_numeric_grade(n):
    
    grade = browser.find_element_by_css_selector(
        
        f'#ctl00_ContentPlaceHolder1_RadGrid1_ctl00__{n} > td:nth-child(6)'
        
        )
    
    return grade.text
    
# They go from 1 to 28
numeric_grades = [get_numeric_grade(i) for i in range(0, 29)]

# Grades, but with name
def get_grade_name(n):
    
    garde_name = browser.find_element_by_css_selector(
        
        f'#ctl00_ContentPlaceHolder1_RadGrid1_ctl00__{n} > td:nth-child(7)'
        
        )
    
    return garde_name.text

grade_names = [get_grade_name(i) for i in range(0, 29)]

# Table with grades
grades = pd.DataFrame(
    
    {'Subject': subject_names,
    'Numeric grade': numeric_grades,
    'Grade name': grade_names}
    
    )

second_quarter = grades.iloc[[0, 3, 5, 6, 10, 11, 12, 15, 16, 21, 22, 28]]

print('This are your 2nd quarter marks')
print(second_quarter)

# Saves them and prints location
grades.to_csv('grades.csv', index=False)
current_dir = Path.cwd()

print(rf'Complete grades saved at {current_dir}\grades.csv')

# ------------------- Average grade and ranking position ---------------------

# Need to go to this menu again
academic_info = browser.find_element_by_css_selector(
    
    '#nav > ul > li:nth-child(2)'
    
    )

academic_info.click()

time.sleep(5)

# Ranking
ranking = browser.find_element_by_id('ctl00_MenuRankingYNotaMedia')
ranking.click()

print('Getting average grade and rakning position...')

time.sleep(10)

ranking_position = browser.find_element_by_id(
    
    'ctl00_ContentPlaceHolder1_lblPosRanking'
    
    ).text

avg_grade = browser.find_element_by_id(
    
    'ctl00_ContentPlaceHolder1_notaMediaParentesis'
    
    ).text

print(f'Average grade: {avg_grade}')
print(f'Ranking position: {ranking_position}')

browser.close()
browser.quit()