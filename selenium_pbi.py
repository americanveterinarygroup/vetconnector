import time
import os.path
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


pbi_user = os.getenv('PBI_USER')
pbi_pass = os.getenv('PBI_PWD')
sec = 15

def set_chrome():
    # Set up the headless browser
    options = Options()
    options.headless = True
    options.add_argument("--start-maximized")
    chrome = webdriver.Chrome(options=options)
    return chrome



def pbi_login(browser):
    browser.get('https://app.powerbi.com/?noSignUpCheck=1')
    logging.info('navigate to power bi')

    WebDriverWait(browser, sec).until(EC.element_to_be_clickable((By.ID, 'i0116'))).send_keys(pbi_user)
    WebDriverWait(browser, sec).until(EC.element_to_be_clickable((By.ID,'idSIButton9'))).click()
    WebDriverWait(browser, sec).until(EC.element_to_be_clickable((By.ID,'i0118'))).send_keys(pbi_pass)
    WebDriverWait(browser, sec).until(EC.element_to_be_clickable((By.ID,'idSIButton9'))).click()
    WebDriverWait(browser, sec).until(EC.element_to_be_clickable((By.ID,'idBtn_Back'))).click()

    logging.info("power bi logged in successfully")
    time.sleep(5)



def navigate_url(browser, url):
    browser.get(url)
    time.sleep(15)
    logging.info("navigate to dvm monthly report dashboard")



def switch_frame(browser, i):
    # switch to selected iframe
    browser.switch_to.frame(i)
    time.sleep(1)



def xpath_click(browser, selector):
    WebDriverWait(browser, sec).until(EC.element_to_be_clickable((By.XPATH, selector))).click()



def xpath_send_text(browser, selector, text):    
    WebDriverWait(browser, sec).until(EC.element_to_be_clickable((By.XPATH, selector))).send_keys(text)



def xpath_send_enter(browser, selector):    
    WebDriverWait(browser, sec).until(EC.element_to_be_clickable((By.XPATH, selector))).send_keys(Keys.ENTER)



def xpath_delete_input(browser, selector):
    WebDriverWait(browser, sec).until(EC.element_to_be_clickable((By.XPATH, selector))).send_keys(Keys.CONTROL, "a")
    WebDriverWait(browser, sec).until(EC.element_to_be_clickable((By.XPATH, selector))).send_keys(Keys.DELETE)



def close_browser(browser):
    browser.quit()