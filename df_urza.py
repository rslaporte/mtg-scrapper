#%%
import pandas as pd

#%%
df = pd.read_csv('./data/urza-s_saga_price.csv')
df

#%%
df_cards = pd.read_csv('./data/cards_urza-s_saga.csv')
df_cards.iloc[139:,:]

#%%
try:
     x = y
except NameError:
     print(NameError.name)
     x = 10

x