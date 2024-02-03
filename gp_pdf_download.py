import time
import logging
import os.path
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from modules import solver_api_requests, logging_config


if __name__ == '__main__':
    try:
        logging_config.logger('./logs/gp_monthly_report_download.log')
        logging.info('START JOB')

        pbi_user = os.getenv('PBI_USER')
        pbi_pass = os.getenv('PBI_PWD')

        doctors = solver_api_requests.active_doctors()
        # doctors.to_csv('DoctorList.csv', index=False)
        # doctors = pd.read_csv('./DoctorList.csv')
        logging.info(f"active doctor list retrieved - rows: {len(doctors)} | columns: {len(doctors.columns)}")

    except Exception as ex:
        logging.error(f"{type(ex).__name__}: {ex}")

    # Set up the headless browser
    options = Options()
    options.headless = True
    options.add_argument("--start-maximized")
    chrome = webdriver.Chrome(options=options)
    logging.info('activate chrome')

    chrome.get('https://app.powerbi.com/?noSignUpCheck=1')
    logging.info('navigate to power bi')

    t = 15
    WebDriverWait(chrome, t).until(EC.element_to_be_clickable((By.ID, 'i0116'))).send_keys(pbi_user)
    WebDriverWait(chrome, t).until(EC.element_to_be_clickable((By.ID,'idSIButton9'))).click()
    WebDriverWait(chrome, t).until(EC.element_to_be_clickable((By.ID,'i0118'))).send_keys(pbi_pass)
    WebDriverWait(chrome, t).until(EC.element_to_be_clickable((By.ID,'idSIButton9'))).click()
    WebDriverWait(chrome, t).until(EC.element_to_be_clickable((By.ID,'idBtn_Back'))).click()

    logging.info("power bi logged in successfully")
    time.sleep(5)

    chrome.get('https://app.powerbi.com/groups/58a5001e-4b10-4c6e-a27f-05c157db4955/reports/e6492287-e727-4f8a-9fe1-b799adfee6e2/ReportSection3d15daab630d570b3efd?experience=power-bi')
    time.sleep(20)
    logging.info("navigate to dvm monthly report dashboard")

    filter_emp = '//*[@id="exploreFilterContainer"]/div[2]/div/filter/div/div[1]/div[1]/button[1]'
    dd = chrome.find_element(By.XPATH, filter_emp).click()

    input = '//*[@id="exploreFilterContainer"]/div[2]/div/filter/div/div[2]/div/filter-visual/div/visual-modern/div/div/div[2]/div/div[1]/input'
    tick_box = '//*[@id="exploreFilterContainer"]/div[2]/div/filter/div/div[2]/div/filter-visual/div/visual-modern/div/div/div[2]/div/div[2]/div/div[1]/div/div/div/div/div/span'
    export = '//*[@id="exportMenuBtn"]'
    pdf = '//*[@id="mat-menu-panel-2"]/div/button[3]'
    btn = '//*[@id="okButton"]'

    for idx in doctors.index:
        try:
            id = doctors['code'][idx]
            dr = doctors['full_name'][idx]
            print(id, dr)
            logging.info(f"{dr} [{id}] - enter in filter")

            time.sleep(3)
            enter_id = chrome.find_element(By.XPATH, input).send_keys(dr)

            time.sleep(3)    
            chk = chrome.find_element(By.XPATH, tick_box).click()

            time.sleep(3)    
            element = chrome.find_element(By.XPATH, export).click()

            time.sleep(1)    
            element = chrome.find_element(By.XPATH, pdf).click()

            time.sleep(1)    
            element = chrome.find_element(By.XPATH, btn).click()

            logging.info(f"{dr} [{id}] - export to pdf")

            i = 0
            duration = 0
            sec = 5
            check_file = False
            pbi_download = "C:/Users/RonaldEvans/Downloads/DVM Monthly Report - General Practice.pdf"
            save_pdf = f"C:/dvm_monthly_distribution/pdfs/gp_staging/monthly_report/{id}_DvmMonthlyReport.pdf"


            while check_file is False and i < 25:
                i +=1
                duration +=sec
                time.sleep(sec)
                check_file = os.path.isfile(pbi_download)
                print(f'[{i}] File exists: {check_file} - {duration} secs')

            logging.info(f"{dr} [{id}] - file downloaded successfully in {duration} secs")
            os.rename(pbi_download, save_pdf)
            logging.info(f"{dr} [{id}] - renamed file: {save_pdf}")
            print('\n')

            chrome.find_element(By.XPATH, tick_box).click()

        except Exception as ex:
            chrome.find_element(By.XPATH, input).send_keys(Keys.CONTROL + 'a', Keys.BACKSPACE)
            logging.info(f"{dr} - {type(ex).__name__}")

    chrome.quit()
    logging.info("JOB END")