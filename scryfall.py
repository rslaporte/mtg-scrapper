#%%
import requests
import pandas as pd

#%%
class ScryfallAPI:
    def __init__(self):
        self.url = "https://api.scryfall.com/" 
        self.headers = {"User-Agent": "MTGCardsSearchExample/1.0", "Accept": "*/*"}

    def getSets(self, set_name, path="sets"):
        sets = requests.get(self.url + path, headers=self.headers)
        sets = pd.json_normalize(sets.json()['data'])[['name', 'code']]
        
        df_sets = sets[sets['name'] == set_name]
        return df_sets

    def getCards(self, set_name, path="cards/search"):
        set_code = self.getSets(set_name)['code'].values[0]
        params = {"q": f"set:{set_code} lang:pt"}
        
        set_cards = requests.get(self.url + path, headers=self.headers, params=params)
        df_cards = pd.json_normalize(set_cards.json()['data'])[['name', "printed_name"]]
        
        df_cards['name_formatted'] = df_cards['name'].map(lambda x: x.lower().replace(' ', '+'))
        df_cards['edition_code'] = set_code.upper()
        df_cards['edition_pt'] = 'A Saga de Urza'
        df_cards['url'] = [f"https://www.ligamagic.com.br/?view=cards/card&card={card}" for card in df_cards['name_formatted']]

        formatted_name = set_name.lower().replace(' ', '_').replace("'", '-')
        df_cards.to_csv(f"../data/cards_{formatted_name}.csv", index=False)

        return df_cards

#%%
scryfall = ScryfallAPI().getCards("Urza's Saga")
