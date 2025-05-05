import pandas as pd
from pathlib import Path

class DFHandle():    
    def save_to_csv(self, df, edition):
            status = ''
            filename = r'C:\Users\Rafael\Desktop\codes\mtg_scrapper\data\price_' + edition + r'.csv'
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

    def df_splitted(self, edition, page):
        initial_position = page*self.batch_size
        final_position = (page+1)*self.batch_size

        if(final_position > self.df_size): 
            final_position = self.df_size

        with open(f"execution_{edition}.log", "a") as f:
            f.write(f"URLS A SEREM PROCESSADAS: {final_position - initial_position}\n")
            f.write(f"POSICAO DE INICIO: {initial_position}\n")
            f.write("---------------------------------------------------------------\n")
        
        return self.df_cards.iloc[initial_position : final_position, :].copy()   

    def df_formater(self, df, results):
        df['date'] = datetime.date.today().strftime('%Y-%m-%d')
        df['prices'] = [result["value"] for result in results]
        df['prices_mean'] = [result["mean"] for result in results]

        cols = df.columns.tolist()
        cols = [cols[8]] + cols[:8] + cols[9:]
        df = df[cols]

        return df