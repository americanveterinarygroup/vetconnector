import os
import pandas as pd
from modules import reporting_dates, sharepoint_api
from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext
import logging
from modules import solver_api_requests, reporting_dates, selenium_pbi, logging_config


logging_config.logger('./logs/sharepoint_upload.log')
logging.info('===== START JOB =====')

prior_month_start = reporting_dates.exclude_date()
prior_month_end = reporting_dates.end_date()
file_date = prior_month_end.strftime('%Y-%m')

usr = os.getenv('PBI_SHAREPOINT_USR')
pwd = os.getenv('PBI_SHAREPOINT_PWD')
sp_url = 'https://avgih.sharepoint.com/sites/PowerBiDatasets/'

ctx = sharepoint_api.sharepoint_auth(usr, pwd, sp_url)

doctors = pd.read_csv('./source_docs/uv_doctors.csv')
for idx in doctors.index:

    id = doctors['code'][idx]
    name = doctors['full_name'][idx]
    loc = doctors['location'][idx]
    
    vet_report = f"C:/dvm_monthly_distribution/pdfs/dvm_monthly_report/vet_performance/{loc}_{id}_{name} AVG Vet Performance - {file_date}.pdf"
    file_name = vet_report.split('/')[5]

    if os.path.exists(vet_report):

        dir = f'DataStorage/DVM_Performance_Transparency/{name}_{id}'
        sharepoint_api.create_sharepoint_directory(dir, ctx)
        logging.info('Directory Create: ' + dir)

        target_folder = ctx.web.get_folder_by_server_relative_url(dir)

        with open(vet_report, 'rb') as content_file:
            file_content = content_file.read()
            target_folder.upload_file(file_name, file_content).execute_query()
            logging.info('file loaded: ' + file_name)