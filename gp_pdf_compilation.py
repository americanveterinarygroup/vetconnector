import os
import shutil
import fitz
import logging
import pandas as pd
from modules import logging_config, reporting_dates


logging_config.logger('./logs/gp_pdf_compilation.log.log')
logging.info('START JOB')

prior_month_start = reporting_dates.exclude_date()
prior_month_end = reporting_dates.end_date()
file_date = prior_month_end.strftime('%Y-%m')

doctors = pd.read_csv('./source_docs/FullDoctorList.csv')
lead_dvm = doctors[ (doctors.lead_dvm == 'X') ]
lead_dvm.to_csv('TEST.csv', index=False)
doctors = doctors[~(doctors.main_location.str.contains('UrgentVet')) ]

doctors['hire_date'] = pd.to_datetime(doctors['hire_date'], errors='coerce').dt.date
logging.info("loaded genral practice doctor list")

############################################################################
###           GP DOCTORS HIRED WITHIN REPORTING MONTH            ###
############################################################################
exclude = doctors[ ( doctors.hire_date >= prior_month_start ) ]
exclude = exclude[ ( exclude.hire_date <= prior_month_end ) ]
logging.info("create list of doctors to exclude")

print(exclude)

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
    new_report_name = f"{loc}_{id}_{name}_DVM Monthly Report - {file_date}.pdf"
    monthly_report = f"./pdfs/gp_staging/monthly_report/{monthly_report_name}"
    exclude_report = f"./pdfs/dvm_monthly_report/exclude/gp/{new_report_name}"

    ### for monthly report
    is_exclude = os.path.isfile(monthly_report)
    if is_exclude:
        # shutil.move(monthly_report, exclude_report)
        logging.info(f"{id}_{name}_{hdate}_doctor hired in prior month - move monthly file")
    else:
        logging.info(f"{id}_{name}_{hdate}_file does not exist in monthly report - do nothing")

############################################################################
###             GP NEW HIRE, LEAD DVM, & PRODUCTION DETERMINATE          ###
############################################################################

new_hires = doctors[ (doctors.exp_level.isin(['Apprentice', 'New Grad', 'Early Career']) ) ]

### filter new hire table within the last 16 months ###
nh_start_date = reporting_dates.new_hire_start()
new_hires = new_hires[ ( new_hires['hire_date'] >= nh_start_date ) ]

lead_dvm = doctors[ (doctors.lead_dvm == 'X') ]

for idx in doctors.index:

    id = doctors['emp_id'][idx]
    name = doctors['full_name'][idx]
    loc = doctors['main_location_id'][idx]
    exp = doctors['exp_level'][idx]
    hdate = doctors['hire_date'][idx]
    prod = doctors['production'][idx]
    status = doctors['status'][idx]
    lead = doctors['lead_dvm'][idx]

    dvm_report = f"C:/dvm_monthly_distribution/pdfs/gp_staging/monthly_report/{id}_DvmMonthlyReport.pdf"
    vet_performance = f"C:/dvm_monthly_distribution/pdfs/dvm_monthly_report/vet_performance/{loc}_{id}_{name} AVG Vet Performance - {file_date}.pdf"
    # vet_lead_performance = f"C:/dvm_monthly_distribution/pdfs/dvm_monthly_report/vet_performance/{loc}_{id}_{name} AVG Lead Vet Performance - {prior_month_end}.pdf"

    is_lead = lead_dvm[(lead_dvm.emp_id.isin([id]))]
    exclude_lead = is_lead.empty

    is_report = os.path.isfile(dvm_report)

    if is_report:
        pdf_performance = fitz.open(dvm_report)
        pdf_report = fitz.open(dvm_report)

        # logging.info(f"EXCLUDE LEAD: {id, name, exp, hdate, prod, status, lead}")
        pdf_performance.select([1])
        pdf_performance.save(vet_performance)


        is_newhire = new_hires[(new_hires.emp_id.isin([id]))]
        exclude_newhire = is_newhire.empty

        prod_report = f"C:/dvm_monthly_distribution/pdfs/prd_staging/{id}_DvmProductionReport.pdf"
        # is_prodreport = os.path.isfile(prod_report)

        fp_newhire = f"C:/dvm_monthly_distribution/pdfs/dvm_monthly_report/general_practice/dvm_newhire/{loc}_{id}_{name} DVM Monthly Report - {file_date}.pdf"
        fp_not_newhire = f"C:/dvm_monthly_distribution/pdfs/dvm_monthly_report/general_practice/{loc}_{id}_{name} DVM Monthly Report - {file_date}.pdf"

        try:
            if exclude_newhire:
                pdf_report.select([0])
                pdf_report.save(fp_not_newhire)

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
                pdf_report.select([0, 2])
                pdf_report.save(fp_newhire)

                if prod == 'Yes':
                    result = fitz.open()

                    for pdf in [fp_newhire, prod_report]:
                        with fitz.open(pdf) as mfile:
                            result.insert_pdf(mfile)

                    result.save(fp_newhire)
                    logging.info(f"New Hire on Production: {id} - {name} | hire date: {hdate} experience: {exp} | onProduction: {prod}")
                else:
                    pdf_report.save(fp_newhire)
                    logging.info(f"New Hire NOT on Production: {id} - {name} | hire date: {hdate} experience: {exp} | onProduction: {prod}")
        except Exception as ex:
            logging.error(f"{id, name}{type(ex).__name__}: {ex}")
    else:
        logging.error(f"REPORT DOESNT EXIST: {dvm_report}")