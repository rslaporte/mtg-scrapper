#%%
import numpy as np
import pandas as pd
import asyncio
import datetime
import time
import pytesseract
import io

from pathlib import Path

from playwright.async_api import async_playwright
from PIL import Image
import cv2

#%%
class Scraper:
    def __init__(self, cards_path):
        self.df_cards = pd.read_csv(cards_path)
        self.df_size = self.df_cards['name'].count()
        self.batch_size = 10

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
        df['prices_median'] = [result["median"] for result in results]
        df['prices_min'] = [result["min"] for result in results]

        cols = df.columns.tolist()
        cols = [cols[8]] + cols[:8] + cols[9:]
        df = df[cols]

        return df


    async def browser_handle(self, browser, card):
        #Getting the page
        page = await browser.new_page()
        await page.goto(card.url, wait_until="load")   

        #Getting the relevant buttons
        lgpd_button = page.get_by_role('button', name="Permitir Todos os Cookies")
        edition_element = page.get_by_title(card.edition_pt).get_by_role('checkbox')
        
        #Click on LGPD Button
        if(await lgpd_button.count()): 
            await lgpd_button.click()

        #Click on Edition Button
        if(await edition_element.count()): 
            await edition_element.check() 
    
        return page

    #Using OCR to get the prices
    async def image_to_string(self, price_element):
        #Getting the element image

        image_bytes = await price_element.screenshot()        
        image = Image.open(io.BytesIO(image_bytes))

        # Convert PIL image to OpenCV format
        image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        # Converte para escala de cinza
        gray = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)

        # Aumenta contraste e faz binarização
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Volta para PIL
        final_image = Image.fromarray(thresh)

        digit = pytesseract.image_to_string(
            final_image, 
            config='--psm 10 -c tessedit_char_whitelist=0123456789,'
        ).strip()

        return digit
    

    async def get_price(self, browser, card):
        prices = []
        page = await self.browser_handle(browser, card)        
        price_elements = page.locator('.price > .new-price').filter(visible=True)

        for price_element in await price_elements.all():
            price = 0          
            price_class = await price_element.get_attribute("class")

            if price_class != "new-price":
                price = await self.image_to_string(price_element)               

            else:
                price = await price_element.inner_text()

            price = price.replace(".","").replace(",", ".").replace("R$", "").strip()
            if(price.endswith(".")): price = price[:-1]

            try:
                prices.append(float(price))
            except:
                continue

            ##Number of prices scrapped
            if(len(prices) == 8): break

        prices = {
            "value": np.array(prices),
            "median": np.median(prices) if len(prices) else 0,
            "mean": np.mean(prices) if len(prices) else 0,
            "min": np.min(prices) if len(prices) else 0
        }

        return prices

    async def run(self, edition, page):
        start_time = time.time() 
        
        df_splitted = self.df_splitted(edition, page)

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 800},
                extra_http_headers={
                    "Accept-Language": "en-US,en;q=0.9",
                    "Upgrade-Insecure-Requests": "1",
                    "DNT": "1",  # Do Not Track
                }
            )

            #use row (np.array) in the function
            tasks = [self.get_price(context, card) 
                     for card in df_splitted.itertuples(index=False)
            ]

            results = await asyncio.gather(*tasks)
            await browser.close()


        df_splitted = self.df_formater(df_splitted, results)
        self.save_to_csv(df_splitted, edition)

        with open(f"execution_{edition}.log", "a") as f:
            f.write(f"URLS PROCESSADAS: {len(results)}\n")
            f.write(f"TEMPO TOTAL DE EXECUCAO: {time.time() - start_time} SEGUNDOS\n")
        
        return df_splitted