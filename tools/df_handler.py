import pandas as pd
import datetime
import os

from .logger import Logger
from pathlib import Path

class DFHandler():
    def __init__(self, edition):
        self.edition = edition
        self.current_path = os.getcwd()
        self.card_path =  self.current_path + f"\\data\\cards_{edition}.csv"

        self.df_cards = pd.read_csv(self.card_path)
        self.size = self.df_cards['name'].count()
        self.batch_size = 10

    def save(self, df):
        status = ''
        filename = self.current_path + f"\\data\\price_{self.edition}.csv" + self.edition + r'.csv'
        file_path = Path(filename)

        if(file_path.exists()):
            status = 'updated'
            actual_df = pd.read_csv(filename)
            updated_df = pd.concat([actual_df, df], ignore_index=True)
        else:
            status = 'created'
            updated_df = df

        updated_df.to_csv(filename, index=False)
        print(f"CSV file in path: {filename}, has been {status}")  

    def batch(self, batch_index):
        initial_position = batch_index*self.batch_size
        final_position = (batch_index+1)*self.batch_size
        
        final_position = self.size if final_position > self.size else final_position

        Logger(self.edition).write([
            f"URLS A SEREM PROCESSADAS: {final_position - initial_position}",
            f"POSICAO DE INICIO: {initial_position}",
            "---------------------------------------------------------------"
        ])

        return self.df_cards.iloc[initial_position : final_position, :].copy()   

    def add_metrics(self, df, results):
        df['date'] = datetime.date.today().strftime('%Y-%m-%d')
        df['prices'] = [result["value"] for result in results]
        df['prices_mean'] = [result["mean"] for result in results]
        df['prices_median'] = [result["median"] for result in results]
        df['prices_min'] = [result["min"] for result in results]

        cols = df.columns.tolist()
        cols = [cols[8]] + cols[:8] + cols[9:]
        df = df[cols]

        return df