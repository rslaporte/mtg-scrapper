#%%
import numpy as np
import asyncio
import time
import pytesseract
import io

from tools.df_handler import DFHandler
from tools.logger import Logger

from playwright.async_api import async_playwright
from PIL import Image
import cv2

#%%
class Scraper:
    def __init__(self, edition):
        self.edition = edition
        self.df = DFHandler(edition)

    async def navigate(self, browser, card):
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

        # Converts to gray scale
        gray = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)

        # Add contrast
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Back to PIL
        final_image = Image.fromarray(thresh)

        # OCR: Turn image to string
        digit = pytesseract.image_to_string(
            final_image, 
            config='--psm 10 -c tessedit_char_whitelist=0123456789,'
        ).strip()

        return digit
    

    async def get_price(self, browser, card):
        prices = []
        page = await self.navigate(browser, card)        
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

            ##Total number os scraped prices
            if(len(prices) == 8): break

        prices = {
            "value": np.array(prices),
            "median": np.median(prices) if len(prices) else 0,
            "mean": np.mean(prices) if len(prices) else 0,
            "min": np.min(prices) if len(prices) else 0
        }

        return prices

    async def run(self, batch_index):
        start_time = time.time() 
        
        df_paginated = self.df.batch(batch_index)

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
                     for card in df_paginated.itertuples(index=False)
            ]

            results = await asyncio.gather(*tasks)
            await browser.close()

        df_paginated = self.df.add_metrics(df_paginated, results)
        self.df.save(df_paginated)

        Logger(self.edition).write([
            f"URLS PROCESSADAS: {len(results)}",
            f"TEMPO TOTAL DE EXECUCAO: {time.time() - start_time} SEGUNDOS"
        ])
        
        return df_paginated