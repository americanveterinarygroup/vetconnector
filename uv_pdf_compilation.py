import os
import shutil
import fitz
import logging
import pandas as pd
from modules import solver_api_requests, logging_config, reporting_dates


logging_config.logger('./logs/uv_pdf_compilation.log.log')
logging.info('START JOB')

prior_month_start = reporting_dates.exclude_date()
prior_month_end = reporting_dates.end_date()

doctors = solver_api_requests.active_doctors()
doctors = doctors[ (doctors.location_name.str.contains('UrgentVet')) ]
logging.info("loaded urgent vet doctor list")

############################################################################
###           URGENT VET DOCTORS HIRED WITHIN REPORTING MONTH            ###
############################################################################
exclude = doctors[ ( doctors.hire_date >= prior_month_start ) ]
exclude = exclude[ ( exclude.hire_date <= prior_month_end ) ]
logging.info("create list of doctors to exclude")

### for production, if doctor was hired within the reporting month they receive a production report, but not a dvm monthly report.
### for doctors in the exclude list, move prod files and dvm report files.
for idx in exclude.index:

    id = exclude['code'][idx]
    loc = exclude['location'][idx]
    name = exclude['full_name'][idx]
    hdate = exclude['hire_date'][idx]
    prod = exclude['production'][idx]

    prod_report_name = f"{id}_DvmProductionReport.pdf"
    new_report_name = f"{loc}_{id}_{name}_Production Report - {prior_month_end}.pdf"
    prod_report = f"./pdfs/uv_staging/production_report/{prod_report_name}"
    move_production = f"./pdfs/dvm_monthly_report/urgent_vet/production_only/{new_report_name}"
    exclude_report = f"./pdfs/dvm_monthly_report/exclude/uv/{new_report_name}"
    
    ### for production
    is_exclude = os.path.isfile(prod_report)
    if is_exclude:
        if prod == 'Yes':
            shutil.move(prod_report, move_production)
            logging.info(f"{id}_{name}_{hdate}_doctor hired in prior month and on production - move prod file")
        else:
            shutil.move(prod_report, exclude_report)
            logging.info(f"{id}_{name}_{hdate}_doctor hired in prior month and not on production - move to exclude")
    else:
        logging.info(f"{id}_{name}_{hdate}_file does not exist in production - do nothing")

    monthly_report_name = f"{id}_DvmMonthlyReport.pdf"
    new_report_name = f"{loc}_{id}_{name}_DVM Monthly Report - {prior_month_end}.pdf"
    monthly_report = f"./pdfs/uv_staging/monthly_report/{monthly_report_name}"
    exclude_report = f"./pdfs/dvm_monthly_report/exclude/uv/{new_report_name}"

    ### for monthly report
    is_exclude = os.path.isfile(monthly_report)
    if is_exclude:
        shutil.move(monthly_report, exclude_report)
        logging.info(f"{id}_{name}_{hdate}_doctor hired in prior month - move monthly file")
    else:
        logging.info(f"{id}_{name}_{hdate}_file does not exist in monthly report - do nothing")

############################################################################
###                     URGENT VET PRODUCTION REPORTS                    ###
############################################################################
directory = "C:/dvm_monthly_distribution/pdfs/uv_staging/production_report/"
for pdf_file in os.listdir(directory):
    prod_report = os.path.join(directory, pdf_file)

    ## identify employee code from pdf filename and match against dataframe.
    id = pdf_file.split('_')[0]
    is_doctor = doctors[(doctors.code.isin([id]))]

    dvm_report = f"C:/dvm_monthly_distribution/pdfs/uv_staging/monthly_report/{id}_DvmMonthlyReport.pdf"
    is_dvm_report = os.path.isfile(dvm_report)

    id = is_doctor['code'].values[0]
    name = is_doctor['full_name'].values[0]
    loc = is_doctor['location'].values[0]
    exp = is_doctor['exp_level'].values[0]
    hdate = is_doctor['hire_date'].values[0]
    prod = is_doctor['production'].values[0]

    logging.info(f"{id, name, exp, hdate, prod}")

    fp = f"C:/dvm_monthly_distribution/pdfs/dvm_monthly_report/urgent_vet/{loc}_{id}_{name} DVM Monthly Report - {prior_month_end}.pdf"

    if str(is_dvm_report) == 'True':
        if prod == 'Yes':
            result = fitz.open()

            for pdf in [dvm_report, prod_report]:
                with fitz.open(pdf) as mfile:
                    result.insert_pdf(mfile)

            result.save(fp)
            logging.info(f"dvm report merged with production and saved: {fp}")
        else:
            shutil.copyfile(dvm_report, fp)
            logging.info(f"not on production - copy dvm report to: {fp}")
    else:
        logging.error(f"dvm report not found: {dvm_report}")



logging.info('JOB END')