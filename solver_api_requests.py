import logging
import requests
import pandas as pd

def get_request(url):
    payload = {}
    headers = {'Content-Type': 'application/json',
                'Authorization': 'Bearer TFRCT0VsZG5QR3hSQ1VaZGZEVlB1aXpXQjdySS94cGFVNlhOSGUxT0tRa0k0ZU9RRE51ODRTUU94b1ZkUllUbjZUdnJ3Y0oyVlZMVU5WbnVSSGR6OWxFbUpiS1c0OGZnRFlUblZFbW1Nd1JnejFibWg2Tjd4cTdubWdTc2VlTlQzTUM2czk1OW51eFZ0TlJESndlUG9RPT0kVzVXazhhU0grQU5WamNUWW9ta3ZqZz09'
            }

    response = requests.request("GET", url, headers=headers, data=payload)
    sc = response.status_code

    if sc != 200: 
        logging.error(f'unexpected status code: {sc} | {url}')
    else: 
        logging.info(f'status code: {sc} | {url}')

    return response.json()


def production_list(end_date):
    # fp = './source_docs/doctorlist.parquet'
    url = 'https://us.app.solverglobal.com/api/v1/data/Dim2'

    ### Get Employee Master Table from Solver API
    json_response = get_request(url)
    df = pd.json_normalize(json_response['data'])

    ### Normalize column names
    df = df.astype(str)
    df.columns = df.columns.str.replace('\s', '_', regex=True).map(str.lower)

    ### Filter only Active Doctors that do not work for UrgentVet, and weren't hired after reporting month end.
    df = df[ (df.status.isin(['A'])) & (df.department == 'DOC') & (~df.hire_date.isin(['None']))]

    df['hire_date'] = pd.to_datetime(df['hire_date'])
    df['hire_date'] = df['hire_date'].dt.date

    df = df.loc[(df['hire_date'] <= end_date)]

    ### Add Full Doctor Name
    df['full_name'] = df['first_name'] + ' ' + df['last_name']
    prod_doctors = df.filter(['code', 'full_name', 'location', 'location_name', 'exp_level', 'status', 'hire_date', 'production', 'email_address'])

    return prod_doctors



def transparency_report_list(end_date):
    # fp = './source_docs/doctorlist.parquet'
    url = 'https://us.app.solverglobal.com/api/v1/data/Dim2'

    ### Get Employee Master Table from Solver API
    json_response = get_request(url)
    df = pd.json_normalize(json_response['data'])

    ### Normalize column names
    df = df.astype(str)
    df.columns = df.columns.str.replace('\s', '_', regex=True).map(str.lower)

    ### Filter only Active Doctors that do not work for UrgentVet, and weren't hired after reporting month end.
    df = df[ (df.status.isin(['A'])) & (df.department == 'DOC') & (~df.hire_date.isin(['None']))]

    df['hire_date'] = pd.to_datetime(df['hire_date'])
    df['hire_date'] = df['hire_date'].dt.date

    df = df.loc[(df['hire_date'] < end_date)]

    ### Add Full Doctor Name
    df['full_name'] = df['first_name'] + ' ' + df['last_name']
    prod_doctors = df.filter(['code', 'full_name', 'location', 'location_name', 'exp_level', 'status', 'hire_date', 'production', 'email_address'])

    return prod_doctors