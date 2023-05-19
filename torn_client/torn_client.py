import requests
import time
from .torn_statics.torn_endpoints import TornEndpoints as TE
from .torn_statics.torn_selections import TornSelctions as TS

# https://www.torn.com/api.html#
class TornClient:
    BASE_URL = 'https://api.torn.com/ENDPOINT/ID?selections=SELECTIONS&key=KEY'

    def __init__(self, client_config):
        self.LISTING_FEE = client_config['ITEM_MARKET_LISTING_FEE']
        self.API_KEY = client_config['API_KEY']
        self.MAX_RETRIES = client_config['MAX_RETRIES']

    # Returns a dict of all torn items
    # https://api.torn.com/torn/?selections=items&key={self.API_KEY}"
    def getTornItems(self):
        url = self.generateURL(TE.TORN, TS.Torn.ITEMS)
        return self.get_request(url)


    # Returns a dict of all Torn stocks available
    # Else just the one stock if an ID is passed in
    # https://api.torn.com/torn/25?selections=stocks&key=API_KEY
    def getTornStock(self, stock_id: str="", key:str =None):
        url = self.generateURL(TE.TORN, TS.Torn.STOCKS, stock_id, key)
        return self.get_request(url)['stocks']


    # Returns a specific users' stocks based on who owns the API key
    # Carful with this, you could leak your own stock info when using
    # a private API key with no user id.
    # https://api.torn.com/user/?selections=stocks&key={self.API_KEY}
    def getUserStock(self, user_id: str='', key: str=None):
        url = self.generateURL(TE.USER, TS.User.STOCKS, user_id, key)
        return self.get_request(url)['stocks']

    # Returns the status for a specific user
    # If no ID/API key provided it will use the owner user's ID and API key
    #   https://api.torn.com/user/{user_id}?selections=newevents&key={self.API_KEY}
    def getUserStatus(self, user_id: str='', key: str=None):
        url = self.generateURL(TE.USER, TS.User.BASIC, user_id, key)
        return self.get_request(url)


    # Returns new events for a specific user
    # If no ID/API key provided it will use the owner user's ID and API key
    #   https://api.torn.com/user/{user_id}?selections=newevents&key={self.API_KEY}
    def getUserNewEvents(self, user_id: str='', key: str=None):
        url = self.generateURL(TE.USER, TS.User.NEWEVENTS, user_id, key)
        return self.get_request(url)['events']


    # returns item market listings for an ID
    #   https://api.torn.com/market/180?selections=itemmarket&key={self.API_KEY}
    #	[{
    # 	    "ID": 163284850,
    # 	    "cost": 3450,
    # 	    "quantity": 1
    #   }, ... ]
    def getMarketItem(self, item_id: str='', key: str=None):
        url = self.generateURL(TE.MARKET, TS.Market.ITEMMARKET, item_id, key)
        return self.get_request(url)['itemmarket']


    # Returns a url string similar to:
    #   https://api.torn.com/ENDPOINT/{id}?selections=SELECTIONS&key={self.API_KEY}
    def generateURL(self, endpoint: str, selections: str, id:str='', key: str=None):
        return self.BASE_URL \
            .replace('ENDPOINT', endpoint) \
            .replace('SELECTIONS', selections) \
            .replace('ID', id) \
            .replace('KEY', key or self.API_KEY)


    def get_request(self, url:str):
        retry_count = 0
        while retry_count < self.MAX_RETRIES:
            retry_count+=1
            try:
                json_info = requests.get(url).json()
                if not json_info.get('error'):
                    return json_info
            except requests.exceptions.RequestException as e:
                print(f"Try: {retry_count} - {e}")
                if retry_count >= self.MAX_RETRIES:
                    raise e
                time.sleep(5)


def main():
    return False


if __name__ == '__main__':
    main()