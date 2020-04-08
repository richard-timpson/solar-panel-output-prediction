import requests
import datetime
from dateutil import relativedelta
from pathlib import Path

path = Path(__file__).parent


def month_range(start_date, end_date):
    while start_date <= end_date:
        old_date = datetime.datetime(start_date)
        start_date = start_date + datetime.timedelta(months=1)
        yield old_date

class SolarEdgeApi():

    def __init__(self, v):
        print(path)
        self.v = v
        with open(f'{path}/solar_edge_api_key.txt', 'r') as file:
            self.api_key = file.read()        

        self.base_url = 'https://monitoringapi.solaredge.com'
        self.url = ''

    #########################
    ######## Internal #######
    #########################
    def set_url(self, api_type, call, site_id=None):
        self.url = f'{self.base_url}/{api_type}{f"/{site_id}" if site_id else ""}/{call}'


    def verbose_print(self,s):
        if self.v:
            print(s)

    def make_request(self, params=None):
        self.verbose_print('Making SolarEdge Api call')
        if params:
            params['api_key'] = self.api_key
        else:
            params = {
                'api_key': self.api_key
            }

        resp = requests.get(self.url, params=params)

        if resp:
            self.verbose_print("Request succeeded!")
            return resp.json()
        else:
            self.verbose_print("Request failed")
            self.verbose_print(f'\tUrl: {self.url}')
            self.verbose_print(f'\tStatus code: {resp.status_code}')
            self.verbose_print(f'\tContent: {resp.content}')


    #########################
    ######## External #######
    #########################

    ## Api Calls ##
    def get_site_list(self):
        self.set_url('sites', 'list')
        return self.make_request()

    def get_site_inventory(self, site_id):
        self.set_url(api_type='site', call='inventory', site_id=site_id)
        return self.make_request()

    def get_data_period(self, site_id):
        self.set_url(api_type='site', call='dataPeriod', site_id=site_id)
        return self.make_request()

    def get_site_energy_detailed(self, site_id, params):
        self.set_url(api_type='site', call='energyDetails', site_id=site_id)
        return self.make_request(params=params)

    ## Helpers/Wrappers ##
    def get_site_consumption_half_hour_range(self, site_id, start_time, end_time):
        assert(isinstance(start_time, datetime.datetime))
        assert(isinstance(end_time, datetime.datetime))

        time_fmt = '%Y-%m-%d %H:%M:%S'
        curr_month = start_time
        next_month = start_time + relativedelta.relativedelta(months=1)
        all_data = []
        while next_month < end_time:
            params = {
                'timeUnit': 'QUARTER_OF_AN_HOUR',
                'meters': 'CONSUMPTION',
                'startTime': curr_month.strftime(time_fmt), 
                'endTime': next_month.strftime(time_fmt)
            }
            print(curr_month, next_month)
            curr_month = next_month
            next_month = next_month + relativedelta.relativedelta(months=1)
            data = self.get_site_energy_detailed(site_id, params)
            all_data.append(data)
            next_month = end_time if next_month > end_time else next_month

        return all_data
