import os
import time
import logging
from modules import solver_api_requests, reporting_dates, selenium_pbi, logging_config


logging_config.logger('./logs/gp_report_download.log')
logging.info('===== START JOB =====')

dt = reporting_dates.exclude_date()

df = solver_api_requests.transparency_report_list(dt)

uv_doctors = df[ ~df['location_name'].str.contains('UrgentVet') & (~df.location.isin(['None']))]
uv_doctors.to_csv('./source_docs/gp_doctors.csv', index=False)
logging.info('uv doctor list retrieved')

chrome = selenium_pbi.set_chrome()
selenium_pbi.pbi_login(chrome)

pbi_uv_url = 'https://app.powerbi.com/groups/58a5001e-4b10-4c6e-a27f-05c157db4955/reports/2a71d8c1-7050-4b91-8366-eb889c34aa2d/ReportSection3d15daab630d570b3efd?experience=power-bi'
selenium_pbi.navigate_url(chrome, pbi_uv_url)

filter_emp = '//*[@id="exploreFilterContainer"]/div[2]/div/filter/div/div[1]/div[1]/button[1]'
input = '//*[@id="exploreFilterContainer"]/div[2]/div/filter/div/div[2]/div/filter-visual/div/visual-modern/div/div/div[2]/div/div[1]/input'
tick_box = '//*[@id="exploreFilterContainer"]/div[2]/div/filter/div/div[2]/div/filter-visual/div/visual-modern/div/div/div[2]/div/div[2]/div/div[1]/div/div/div/div/div/span'
export = '//*[@id="exportMenuBtn"]'
pdf = '//*[@id="mat-menu-panel-2"]/div/button[3]'
btn = '//*[@id="okButton"]'

selenium_pbi.xpath_click(chrome, filter_emp)
pbi_download = "C:/Users/RonaldEvans/Downloads/DVM Monthly Report - General Practice.pdf"

for idx in uv_doctors.index:
    try:
        id = uv_doctors['code'][idx]
        dr = uv_doctors['full_name'][idx]
        logging.info(f"{dr} [{id}] - enter in filter")

        time.sleep(3)
        selenium_pbi.xpath_send_text(chrome, input, dr)

        time.sleep(3)
        selenium_pbi.xpath_click(chrome, tick_box)

        time.sleep(3)
        selenium_pbi.xpath_click(chrome, export)

        time.sleep(3)
        selenium_pbi.xpath_click(chrome, pdf)

        time.sleep(3)
        selenium_pbi.xpath_click(chrome, btn)

        logging.info(f"Dr. {dr} [{id}] - export to pdf")

        i = 0
        duration = 0
        sec = 5
        check_file = False
        save_pdf = f"C:/dvm_monthly_distribution/pdfs/gp_staging/{id}_DvmMonthlyReport.pdf"

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

        selenium_pbi.xpath_click(chrome, tick_box)

    except Exception as ex:
        selenium_pbi.xpath_delete_input(chrome, input)
        logging.info(f"{dr} - {type(ex).__name__}")

selenium_pbi.close_browser(chrome)
logging.info("===== JOB END =====")