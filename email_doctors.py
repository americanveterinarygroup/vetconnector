import os
import time
import logging
import pandas as pd
from modules import solver_api_requests, logging_config, reporting_dates, outlook_mail


try:
    logging_config.logger('./logs/send_emails.log')
    logging.info('START JOB')

    prior_month_start = reporting_dates.exclude_date()
    prior_month_end = reporting_dates.end_date()

    doctors = solver_api_requests.active_doctors()
    doctors = doctors.astype(str)

    regional_directors = pd.read_csv('./source_docs/regional_directors.csv')
    regional_directors = regional_directors.astype(str)

    df = doctors.merge(regional_directors, left_on='location', right_on='loc_id', how='left')
    df = df.filter(['code', 'full_name', 'location', 'location_name', 'exp_level', 'hire_date', 'production', 'email_address', 'email'])

    cnt = 0
    directory = "C:/dvm_monthly_distribution/pdfs/email/"
    for pdf_file in os.listdir(directory):
        dvm_report = os.path.join(directory, pdf_file)

        ## identify employee code from pdf filename and match against dataframe.
        id = pdf_file.split('_')[1]
        is_doctor = df[(df.code.isin([id]))]

        doctor_not_found = is_doctor.empty

        if not doctor_not_found:
            code = is_doctor['code'].values[0]
            name = is_doctor['full_name'].values[0]
            loc = is_doctor['location'].values[0]
            exp = is_doctor['exp_level'].values[0]
            hdate = is_doctor['hire_date'].values[0]
            prod = is_doctor['production'].values[0]
            email = is_doctor['email_address'].values[0]
            rd = is_doctor['email'].values[0]

            logging.info(f"doctor: {name} | location: {loc} | email: {email} | rd email: {rd}")
            logging.info(f"SEND EMAIL WITH: {dvm_report}")
            logging.info(" ")

            outlook_mail.send_email(code, name, email, rd, dvm_report)
            time.sleep(10)

            cnt += 1
        else:
            logging.error(f"{id} - email not sent")

    logging.info(f"{cnt} emails sent")
    logging.info('JOB END')

except Exception as ex:
    logging.info(f"ERROR: {id, name}{type(ex).__name__}: {ex}")