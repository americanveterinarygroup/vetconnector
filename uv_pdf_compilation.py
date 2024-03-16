import os
import shutil
import fitz
import logging
import pandas as pd
from modules import logging_config, reporting_dates


logging_config.logger('./logs/uv_pdf_compilation.log.log')
logging.info('START JOB')

prior_month_start = reporting_dates.exclude_date()
prior_month_end = reporting_dates.end_date()
file_date = prior_month_end.strftime('%Y-%m')

doctors = pd.read_csv('./source_docs/FullDoctorList.csv')
doctors = doctors[ (doctors.main_location.str.contains('UrgentVet')) ]
logging.info("loaded urgent vet doctor list")


doctors['hire_date'] = pd.to_datetime(doctors['hire_date'], errors='coerce').dt.date

############################################################################
###           URGENT VET DOCTORS HIRED WITHIN REPORTING MONTH            ###
############################################################################
exclude = doctors[ ( doctors.hire_date >= prior_month_start ) ]
exclude = exclude[ ( exclude.hire_date <= prior_month_end ) ]
logging.info("create list of doctors to exclude")

### for production, if doctor was hired within the reporting month they receive a production report, but not a dvm monthly report.
### for doctors in the exclude list, move prod files and dvm report files.
for idx in exclude.index:

    id = exclude['emp_id'][idx]
    loc = exclude['main_location_id'][idx]
    name = exclude['full_name'][idx]
    hdate = exclude['hire_date'][idx]
    prod = exclude['production'][idx]

    prod_report_name = f"{id}_DvmProductionReport.pdf"
    new_report_name = f"{loc}_{id}_{name}_Production Report - {file_date}.pdf"
    prod_report = f"./pdfs/prd_staging/{prod_report_name}"
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
    new_report_name = f"{loc}_{id}_{name}_DVM Monthly Report - {file_date}.pdf"
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

for idx in doctors.index:

    id = doctors['emp_id'][idx]
    name = doctors['full_name'][idx]
    loc = doctors['main_location_id'][idx]
    exp = doctors['exp_level'][idx]
    hdate = doctors['hire_date'][idx]
    prod = doctors['production'][idx]
    status = doctors['status'][idx]
    logging.info(f"{id, name, exp, hdate, prod, status}")

    dvm_report = f"C:/dvm_monthly_distribution/pdfs/uv_staging/monthly_report/{id}_DvmMonthlyReport.pdf"
    prod_report = f"C:/dvm_monthly_distribution/pdfs/prd_staging/{id}_DvmProductionReport.pdf"
    
    ## identify employee code from pdf filename and match against dataframe. 
    is_dvm_report = os.path.isfile(dvm_report)
    is_prod_report = os.path.isfile(prod_report)

    vet_performance = f"C:/dvm_monthly_distribution/pdfs/dvm_monthly_report/vet_performance/{loc}_{id}_{name} AVG Vet Performance - {file_date}.pdf"
    fp = f"C:/dvm_monthly_distribution/pdfs/dvm_monthly_report/urgent_vet/{loc}_{id}_{name} DVM Monthly Report - {file_date}.pdf"

    if is_dvm_report:
        pdf_report = fitz.open(dvm_report)
        pdf_performance = fitz.open(dvm_report)

        pdf_report.select([0])
        pdf_report.save(fp)

        pdf_performance.select([1])
        pdf_performance.save(vet_performance)

        if is_prod_report:

            result = fitz.open()
            for pdf in [fp, prod_report]:
                with fitz.open(pdf) as mfile:
                    result.insert_pdf(mfile)

            result.save(fp)
            logging.info(f"dvm report merged with production and saved: {fp}")
        else:
            logging.info(f"not on production - report saved: {fp}")
    else:
        logging.error(f"DO NOTHING: {dvm_report}")

logging.info('JOB END')