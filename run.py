import asyncio
import math
import schedule
import time
from datetime import datetime
from scraper import Scraper  # Importa a classe Scraeper do seu módulo

def main():    
    scraper = Scraper(r'C:\Users\Rafael\Desktop\codes\mtg_scrapper\data\cards_urza-s_saga.csv')

    max_retries = 3
    max_executions = math.ceil(scraper.df_size / scraper.batch_size) 
    executions = 0   

    def job():        
        retry_count = 1
        nonlocal executions
        success = False

        print(f"Execução {executions + 1} iniciada...")
        with open("execution.log", "a") as f:
            f.write("##################################################################################\n")
            f.write(f"EXECUTANDO EM: {datetime.now()}\n")

        while not success and retry_count <= max_retries:              
            try:
                asyncio.run(scraper.run(executions)) 
                success = True

            except Exception as e:
                retry_count += 1

                with open("execution.log", "a") as f:
                    f.write(f"{datetime.now()} - ERRO NA EXECUCAO {executions + 1}: {str(e)}\n")

                if retry_count <= max_retries:                    
                    time.sleep(180)                   

        executions += 1
        if executions >= max_executions:
            print("Execuções concluídas. Encerrando agendador.")

            with open("execution.log", "a") as f:
                f.write(f"EXECUCAO DO SCRIPT CONCLUIDA.\n")

            return schedule.CancelJob 
        
    #First execution
    job()

    # Agenda a primeira execução imediata + repetições a cada 10 minutos
    schedule.every(15).minutes.do(job)

    # Mantém o script rodando até que todas as execuções sejam completadas
    while executions < max_executions:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    main()