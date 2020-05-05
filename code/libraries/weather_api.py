import requests
import pathlib
path = pathlib.Path(__file__).parent.absolute()
class DarkSkyApi:

    def __init__(self, verbose):
        with open(f'{path}/keys/darksky_api_key.txt', 'r') as f:
            self.key = f.read()
        
        self.base_url = 'https://api.darksky.net'
        self.verbose = verbose 

    def print_verbose(self, s):
        if self.verbose:
            print(s)

    def get_forecast(self, lat, lon):
        self.url = f'{self.base_url}/forecast/{self.key}/{lat},{lon}'
        self.print_verbose(f'Making request to url: {self.url}')
        resp = requests.get(self.url)
        if resp.status_code != 200:
            print(resp.status_code)
            print(resp.content)
        
        forecast = resp.json()
        return forecast 
    

class SolCastApi:

    def __init__(self, verbose):
        with open(f'{path}/keys/solcast_api_key.txt') as f:
            self.key = f.read() 
        
        self.base_url = 'https://api.solcast.com.au'
        self.verbose = verbose 

    def print_verbose(self, s):
        if self.verbose:
            print(s)

    def get_forecast(self, lat, lon):
        self.url = f'{self.base_url}/world_radiation/forecasts?latitude={lat}&longitude={lon}&api_key={self.key}&format=json'
        self.print_verbose(f'Making request to url: {self.url}')
        resp = requests.get(self.url)
        if resp.status_code != 200:
            print(resp.status_code)
            print(resp.content)

        forecast = resp.json()
        return forecast 
        
    