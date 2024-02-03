import os
import shutil
import fitz
import logging
import pandas as pd
from modules import solver_api_requests, logging_config, reporting_dates


logging_config.logger('./logs/gp_pdf_compilation.log.log')
logging.info('START JOB')

prior_month_start = reporting_dates.exclude_date()
prior_month_end = reporting_dates.end_date()

doctors = solver_api_requests.active_doctors()
doctors = doctors[ (~doctors.location_name.str.contains('UrgentVet')) ]
logging.info("loaded genral practice doctor list")

############################################################################
###           GP DOCTORS HIRED WITHIN REPORTING MONTH            ###
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
    prod_report = f"./pdfs/gp_staging/production_report/{prod_report_name}"
    move_production = f"./pdfs/dvm_monthly_report/general_practice/production_only/{new_report_name}"
    exclude_report = f"./pdfs/dvm_monthly_report/exclude/gp/{new_report_name}"
    
    ### for production
    is_exclude = os.path.isfile(prod_report)
    if is_exclude:
        if prod == 'Yes':
            shutil.move(prod_report, move_production)
            logging.info(f"{id}_{name}_{hdate}_doctor hired in prior month and on production - move prod file")
        else:
            shutil.move(prod_report, exclude_report)
            logging.info(f"{id}_{name}_{hdate}_doctor hired in prior month and not on production - exclude prod file")
    else:
        logging.info(f"{id}_{name}_{hdate}_file does not exist in production - do nothing")

    monthly_report_name = f"{id}_DvmMonthlyReport.pdf"
    new_report_name = f"{loc}_{id}_{name}_DVM Monthly Report - {prior_month_end}.pdf"
    monthly_report = f"./pdfs/gp_staging/monthly_report/{monthly_report_name}"
    exclude_report = f"./pdfs/dvm_monthly_report/exclude/gp/{new_report_name}"

    ### for monthly report
    is_exclude = os.path.isfile(monthly_report)
    if is_exclude:
        shutil.move(monthly_report, exclude_report)
        logging.info(f"{id}_{name}_{hdate}_doctor hired in prior month - move monthly file")
    else:
        logging.info(f"{id}_{name}_{hdate}_file does not exist in monthly report - do nothing")

############################################################################
###                     GP NEW HIRE AND PRODUCTION COMPILATION           ###
############################################################################

new_hires = doctors[ (doctors.exp_level.isin(['New Grad', 'Early Career']) ) ]

### filter new hire table within the last 16 months ###
nh_start_date = reporting_dates.new_hire_start()
new_hires = new_hires[ ( new_hires['hire_date'] >= nh_start_date ) ]

directory = "C:/dvm_monthly_distribution/pdfs/gp_staging/monthly_report/"
for pdf_file in os.listdir(directory):
    dvm_report = os.path.join(directory, pdf_file)

    ## identify employee code from pdf filename and match against dataframe.
    id = pdf_file.split('_')[0]
    is_doctor = doctors[(doctors.code.isin([id]))]

    id = is_doctor['code'].values[0]
    name = is_doctor['full_name'].values[0]
    loc = is_doctor['location'].values[0]
    exp = is_doctor['exp_level'].values[0]
    hdate = is_doctor['hire_date'].values[0]
    prod = is_doctor['production'].values[0]

    is_newhire = new_hires[(new_hires.code.isin([id]))]
    exclude_newhire = is_newhire.empty

    prod_report = f"C:/dvm_monthly_distribution/pdfs/gp_staging/production_report/{id}_DvmProductionReport.pdf"
    is_prodreport = os.path.isfile(prod_report)

    fp_newhire = f"C:/dvm_monthly_distribution/pdfs/dvm_monthly_report/general_practice/dvm_newhire/{loc}_{id}_{name} DVM Monthly Report - {prior_month_end}.pdf"
    fp_not_newhire = f"C:/dvm_monthly_distribution/pdfs/dvm_monthly_report/general_practice/{loc}_{id}_{name} DVM Monthly Report - {prior_month_end}.pdf"

    try:
        if exclude_newhire:
            pdf_drop = fitz.open(dvm_report)
            pdf_drop.select([0, 1])
            pdf_drop.save(fp_not_newhire)

            if prod == 'Yes':
                result = fitz.open()

                for pdf in [fp_not_newhire, prod_report]:
                    with fitz.open(pdf) as mfile:
                        result.insert_pdf(mfile)

                result.save(fp_not_newhire)
                logging.info(f"NOT a New Hire on Production: {id} - {name} | hire date: {hdate} experience: {exp} | onProduction: {prod}")
            else:
                logging.info(f"NOT a New Hire NOT on Production: {id} - {name} | hire date: {hdate} experience: {exp} | onProduction: {prod}")
        else:
            if prod == 'Yes':
                result = fitz.open()

                for pdf in [dvm_report, prod_report]:
                    with fitz.open(pdf) as mfile:
                        result.insert_pdf(mfile)

                result.save(fp_newhire)
                logging.info(f"New Hire on Production: {id} - {name} | hire date: {hdate} experience: {exp} | onProduction: {prod}")
            else:
                shutil.copyfile(dvm_report, fp_newhire)
                logging.info(f"New Hire NOT on Production: {id} - {name} | hire date: {hdate} experience: {exp} | onProduction: {prod}")
    except Exception as ex:
        logging.info(f"ERROR: {id, name}{type(ex).__name__}: {ex}")