@echo off
cd /d "C:\Users\Rafael\Desktop\codes\mtg_scrapper\"
call .venv\Scripts\activate.bat  :: Ativa o venv
python run.py
pause  :: Mantém a janela aberta