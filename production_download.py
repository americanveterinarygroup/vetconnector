import os
import time
import logging
from modules import solver_api_requests, reporting_dates, selenium_pbi, logging_config


logging_config.logger('./logs/production_report_download.log')
logging.info('===== START JOB =====')

dt = reporting_dates.end_date()
df = solver_api_requests.production_list(dt)

prod_doctors = df[ (df.production == 'Yes') ]
prod_doctors.to_csv('./source_docs/production_doctors.csv', index=False)
logging.info('production list retrieved')

chrome = selenium_pbi.set_chrome()
selenium_pbi.pbi_login(chrome)

pbi_production_url = 'https://app.powerbi.com/groups/58a5001e-4b10-4c6e-a27f-05c157db4955/rdlreports/b4d07f23-e87a-4abb-a5b2-568cabdc2587?experience=power-bi'
selenium_pbi.navigate_url(chrome, pbi_production_url)

selenium_pbi.switch_frame(chrome, 0)

pbi_download = "C:/Users/RonaldEvans/Downloads/DVM Production Report.pdf"

for idx in prod_doctors.index:
    id = prod_doctors['code'][idx]
    dr = prod_doctors['full_name'][idx]
    logging.info(f"{dr} [{id}] - enter in filter")

    input = "/html/body/div[2]/div/div/div/div/div[2]/div/form/div[1]/div/div/div/div/input"
    view_report = "/html/body/div[2]/div/div/div/div/div[2]/div/form/div[2]/button"
    export = "/html/body/div[2]/div/div/div/div/div[2]/div/div[1]/div/div[2]/div/div/div/div/div/div[1]/button"
    pdf = "//*[contains(@id, 'id__')]/div/ul/li[2]/button"

    time.sleep(5)
    selenium_pbi.xpath_delete_input(chrome, input)
    selenium_pbi.xpath_send_text(chrome, input, dr)
    selenium_pbi.xpath_send_enter(chrome, input)

    time.sleep(5)
    selenium_pbi.xpath_click(chrome, view_report)

    time.sleep(5)
    selenium_pbi.xpath_click(chrome, export)

    time.sleep(1)
    selenium_pbi.xpath_click(chrome, pdf)

    i = 0
    duration = 0
    sec = 5
    check_file = False
    save_pdf = f"C:/dvm_monthly_distribution/pdfs/prd_staging/{id}_DvmMonthlyReport.pdf"

    while check_file is False and i < 25:
        i +=1
        duration +=sec
        time.sleep(sec)

        check_file = os.path.isfile(pbi_download)
        logging.info(f'[{i}] File exists: {check_file} - {duration} secs')

    os.rename(pbi_download, save_pdf)

selenium_pbi.close_browser(chrome)
logging.info("chrome browser closed")

logging.info('===== JOB END =====')