import requests

class TornClient:
    BASE_URL = 'https://api.torn.com/torn/25?selections=stocks&key=CjUlbD4zl6TVTShs'

    def __init__(self, client_config):
        self.LISTING_FEE = client_config['ITEM_MARKET_LISTING_FEE']
        self.API_KEY = client_config['API_KEY']


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


    def getItems(self):
        print(f"key: {self.API_KEY}")
        selection = 'items'
        url = f"https://api.torn.com/torn/?selections={selection}&key={self.API_KEY}"
        print(f"URL : {url}")
        r = requests.get(url)
        return r.json()

    
    def getStock(self, id=""):
        url = self.BASE_URL
        r = requests.get(url)
        return r.json()['stocks']

def main():
    return False


if __name__ == '__main__':
    main()