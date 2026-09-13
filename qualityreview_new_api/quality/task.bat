cd@echo off
cd  /d "C:\venv"
call Scripts\activate.bat 
cd  /d "C:\venv\qualityreview_new_api\quality"     
python tasks.py 
deactivate     