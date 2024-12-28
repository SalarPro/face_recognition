@echo off
REM Run the first batch file in a new thread
start "" "C:\Users\Z Tech Office\GitHub\face_recognition\run_main_camera_enter.bat"

REM Run the second batch file in a new thread
start "" "C:\Users\Z Tech Office\GitHub\face_recognition\run_main_camera_exit.bat"

REM Add more batch files as needed
start "" "C:\Users\Z Tech Office\GitHub\face_recognition\run_main_face.bat"

REM Add more batch files as needed
start "" "C:\Users\Z Tech Office\GitHub\face_recognition\run_main_server.bat"
