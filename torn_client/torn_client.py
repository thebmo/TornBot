import requests
from .torn_statics.torn_endpoints import TornEndpoints as TE
from .torn_statics.torn_selections import TornSelctions as TS

# https://www.torn.com/api.html#
class TornClient:
    BASE_URL = 'https://api.torn.com/ENDPOINT/ID?selections=SELECTIONS&key=KEY'

    def __init__(self, client_config):
        self.LISTING_FEE = client_config['ITEM_MARKET_LISTING_FEE']
        self.API_KEY = client_config['API_KEY']

    # TODO thse helpers dont really belong here, move them
    def findListingForProfit(self, target_profit):
        listing = target_profit
        while(True):
            profit = (listing - (self.LISTING_FEE * listing))
            if (profit != target_profit and profit < target_profit):
                listing+=1
            else:
                break
        return listing


    def findProfitForListing(self, listing):
        return (listing - (self.LISTING_FEE * listing))


    def findNetProfitForlistings(self, listing, purchase_cost, quantity):
        gross = (listing - (self.LISTING_FEE * listing)) * quantity
        return gross - (purchase_cost * quantity)

    # End TODO

    # Returns a dict of all torn items
    # https://api.torn.com/torn/?selections=items&key={self.API_KEY}"
    def getTornItems(self):
        url = self.generateURL(TE.TORN, TS.Torn.ITEMS)
        r = requests.get(url)
        return r.json()


    # Returns a dict of all Torn stocks available
    # Else just the one stock if an ID is passed in
    # https://api.torn.com/torn/25?selections=stocks&key=API_KEY
    def getTornStock(self, id: str="", key:str =None):
        url = self.generateURL(TE.TORN, TS.Torn.STOCKS, id, key)
        r = requests.get(url)
        return r.json()['stocks']


    # Returns a specific users' stocks based on who owns the API key
    # Carful with this, you could leak your own stock info when using
    # a private API key with no user id.
    # https://api.torn.com/user/?selections=stocks&key={self.API_KEY}
    def getUserStock(self, user_id: str='', key: str=None):
        url = self.generateURL(TE.USER, TS.User.STOCKS, user_id, key)
        r = requests.get(url)
        return r.json()['stocks']


    # Returns a url string similar to:
    #   https://api.torn.com/ENDPOINT/ID?selections=SELECTIONS&key={self.API_KEY}
    def generateURL(self, endpoint: str, selections: str, id:str='', key: str=None):
        return self.BASE_URL \
            .replace('ENDPOINT', endpoint) \
            .replace('SELECTIONS', selections) \
            .replace('ID', id) \
            .replace('KEY', key or self.API_KEY)


def main():
    return False

if __name__ == '__main__':
    main()