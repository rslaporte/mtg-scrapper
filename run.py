import asyncio
import math
import schedule
import time

from datetime import datetime
from tools.logger import Logger
from scraper import Scraper  

def main(edition):
    scraper = Scraper(edition) 
    logger = Logger(edition)

    executions = 0
    max_retries = 3
    max_executions = math.ceil(scraper.df.size / scraper.df.batch_size) 
    
    def job():        
        retry_count = 1
        nonlocal executions
        success = False

        print(f"Execução {executions + 1} iniciada...")
        logger.write([
            "##################################################################################",
            f"EXECUTANDO EM: {datetime.now()}"
        ])

        while not success and retry_count <= max_retries:              
            try:
                asyncio.run(scraper.run(executions)) 
                success = True

            except Exception as e:
                retry_count += 1
                logger.write([f"{datetime.now()} - ERRO NA EXECUCAO {executions + 1}: {str(e)}"])

                if retry_count <= max_retries:                    
                    time.sleep(180)                   

        executions += 1
        if executions >= max_executions:
            print("Execuções concluídas. Encerrando agendador.")
            

            return schedule.CancelJob 
        
    #First execution
    job()

    # Schedules the first execution and its repetitions every 15 minutes.
    schedule.every(15).minutes.do(job)

    # Keeps the scripts running until the end of the execution
    while executions < max_executions:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':  
    main("urza-s_saga")