class Logger():
    def __init__(self, edition):
        self.edition = edition
        self.path = r'C:\Users\Rafael\Desktop\codes\mtg_scrapper\data\cards_' + edition + r'.csv' 

    def write(self, message_arr):
        with open(f"execution_{self.edition}.log", "a") as f:
            for message in message_arr:
                f.write(f"{message}\n")

    
#%%
teste = 'abcdd'

print()