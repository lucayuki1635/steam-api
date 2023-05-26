import requests, json, re

class SteamAPI():
    def __init__(self):
        self.BASE_URL = 'https://steamcommunity.com'
        self.currencies = {
            'USD': 1, 
            'GBP': 2, 
            'EUR': 3, 
            'CHF': 4, 
            'RUB': 5, 
            'PLN': 6, 
            'BRL': 7, 
            'JPY': 8, 
            'NOK': 9, 
            'IDR': 10, 
            'MYR': 11, 
            'PHP': 12, 
            'SGD': 13, 
            'THB': 14, 
            'VND': 15, 
            'KRW': 16, 
            'TRY': 17, 
            'UAH': 18, 
            'MXN': 19, 
            'CAD': 20, 
            'AUD': 21, 
            'NZD': 22, 
            'CNY': 23, 
            'INR': 24, 
            'CLP': 25, 
            'PEN': 26, 
            'COP': 27, 
            'ZAR': 28, 
            'HKD': 29, 
            'TWD': 30, 
            'SAR': 31, 
            'AED': 32, 
            'SEK': 33, 
            'ARS': 34, 
            'ILS': 35, 
            'BYN': 36, 
            'KZT': 37, 
            'KWD': 38, 
            'QAR': 39, 
            'CRC': 40, 
            'UYU': 41, 
            'BGN': 42, 
            'HRK': 43, 
            'CZK': 44, 
            'DKK': 45, 
            'HUF': 46, 
            'RON': 47
        }
    
    def get_inventory(self, steam_id:int|str, app_id:int|str, language:str='english') -> dict:
        base_url = f'{self.BASE_URL}/inventory/{steam_id}/{app_id}/2?l={language}&count=2000'
        headers = {
            'Accept': '*/*',
            'Connection': 'keep-alive',
            'Host': 'steamcommunity.com',
            'Referer': f'{self.BASE_URL}/profiles/{steam_id}/inventory/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',

        }
        response = requests.get(base_url, headers=headers)
        if response.status_code != 200:
            if response.status_code == 403 and response.text == 'null':
                return {"Error Status Code": response.status_code, "Error type": "Inventory Privacy", "Text": response.text}
            return {"Error Status Code": response.status_code, "Text": response.text}
        json_data = json.loads(response.text)
        user_items = []
        if 'descriptions' in json_data:
            items_type = json_data['descriptions']
            items = json_data['assets']
            for i in items_type:
                for item in items:
                    if item['classid'] == i['classid']:
                        item_base_dict = {
                            "classID": i['classid'],
                            "name": i['market_name'],
                            "item_id": item['assetid'],
                            "tradelock": True if i["tradable"]==0 and i["marketable"]==1 else False,
                            "tradeable": True if i["marketable"]==1 else False,
                            "inpect": i['market_actions'][0]['link'].replace(r'M%listingid%', f'S{steam_id}').replace(r'%assetid%', f'{item["assetid"]}') if 'market_actions' in i.keys() else None,
                            "market name": i["market_hash_name"],
                            "mini picture": f"https://community.cloudflare.steamstatic.com/economy/image/{i['icon_url']}/96fx96f"
                            }
                        user_items.append(item_base_dict)
            return user_items
        else:
            return json_data
    
    def get_inventory_item_value(self, app_id:int|str, market_name:str, country:str='US', currency:str='USD') -> dict:
        headers = {
            'Accept': '*/*',
            'Connection': 'keep-alive',
            'Host': 'steamcommunity.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        }
        base_url = f"{self.BASE_URL}/market/priceoverview/?country={country}&currency={self.currencies[currency]}&appid={app_id}&market_hash_name={market_name}"
        response = requests.get(base_url, headers=headers)
        return json.loads(response)

    def get_market_item_value(self, app_id:int|str, market_name:str, country:str='US', currency:str='USD', language:str='english') -> dict :
        #Get market item id
        url_get_nameId = f'{self.BASE_URL}/market/listings/{app_id}/{market_name}'
        response = requests.get(url_get_nameId)
        if response.status_code != 200:
            return {"Error Status Code": response.status_code, "Text": response.text}
        
        html = response.text
        item_id = re.search(r'Market_LoadOrderSpread(.*?);', html).group(1).replace("( ","").replace(" )","")
        #Market sell and buy orders/price
        base_url = f"{self.BASE_URL}/market/itemordershistogram?country={country}&language={language}&currency={self.currencies[currency]}&item_nameid={item_id}&two_factor=0"
        response = requests.get(base_url)
        if response.status_code != 200:
            return {"Error Status Code": response.status_code, "Text": response.text}
        json_data = json.loads(response.text)
        data = {
            "sell order price": json_data["sell_order_graph"][0][0],
            "sell items quantity": json_data["sell_order_graph"][0][1],
            "buy order price": json_data["buy_order_graph"][0][0],
            "buy items quantity": json_data["buy_order_graph"][0][1]
        }
        return data