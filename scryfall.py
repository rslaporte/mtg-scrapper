#%%
import requests
import pandas as pd

#%%
class ScryfallAPI:
    def __init__(self):
        self.url = "https://api.scryfall.com/" 
        self.headers = {"User-Agent": "MTGCardsSearchExample/1.0", "Accept": "*/*"}

    def cards_df(self, card_pages, set_name):
        frames = []
        set_code = self.getSets(set_name)['code'].values[0]        

        for cards in card_pages:
            df_cards = pd.json_normalize(cards)[['name', 'printed_name', 'type_line', 'mana_cost', 'colors']]        
            df_cards['name_formatted'] = df_cards['name'].map(lambda x: x.lower().replace(' ', '+'))
            df_cards['edition_code'] = set_code.upper()
            df_cards['edition_pt'] = 'A Saga de Urza'
            df_cards['url'] = [f"https://www.ligamagic.com.br/?view=cards/card&card={card}" for card in df_cards['name_formatted']]
            
            frames.append(df_cards.drop(columns=['name_formatted']))

        formatted_name = set_name.lower().replace(' ', '_').replace("'", '-')
        df_cards = pd.concat(frames)

        return {
            "df": df_cards,
            "formatted_name": formatted_name
        }
    
    def cards_to_csv(self, set_name):
        cards = self.getCards(set_name)
        df_cards, formatted_name = self.cards_df(cards, set_name).values()
        
        df_cards.to_csv(r"C:\Users\Rafael\Desktop\codes\mtg_scrapper\data\cards_" + formatted_name + ".csv", index=False)
        return df_cards

    def getSets(self, set_name, path="sets"):
        sets = requests.get(self.url + path, headers=self.headers)
        sets = pd.json_normalize(sets.json()['data'])[['name', 'code']]
        
        df_sets = sets[sets['name'] == set_name]
        return df_sets

    def getCards(self, set_name, path="cards/search"):
        card_pages = []
        set_code = self.getSets(set_name)['code'].values[0]
        
        params = {"q": f"set:{set_code} lang:pt"}
        url = self.url + path
        
        #Getting every page
        while url:
            response = requests.get(url, headers=self.headers, params=params)
            data = response.json()

            if response.status_code != 200: break

            card_pages.extend(data['data'])
            url = data.get('next_page')

        return card_pages

#%%
scryfall = ScryfallAPI()
df = scryfall.cards_to_csv("Urza's Saga")

# %%
scryfall.getCards("Urza's Saga")
