@echo off
title AI News Validator - Starter
echo ==========================================
echo    AI NEWS VALIDATOR & FACT CHECKER
echo ==========================================
echo.
echo [1/2] Checking & Installing Dependencies...
pip install -r requirements.txt
echo.
echo [2/2] Launching AI Engine (Streamlit)...
streamlit run web_app.py
pause
