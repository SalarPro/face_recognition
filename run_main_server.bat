@echo off
REM Change to the directory where your project is located
cd /d C:\Users\Z Tech Office\GitHub\face_recognition


title Server

REM Activate the virtual environment
call myenv\Scripts\activate

REM Run the main.py script
python src/mainServer.py

REM Deactivate the virtual environment
deactivate