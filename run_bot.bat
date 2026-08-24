@echo off
title Nexvora Shopee Telegram Bot
set PYTHONIOENCODING=utf-8

:loop
echo =======================================================
echo           Starting Telegram Shopee Bot...
echo  (Make sure VPN is connected if Telegram API is blocked)
echo =======================================================
python bot.py
echo.
echo [!] Bot disconnected or network failed. Retrying in 5 seconds...
timeout /t 5 /nobreak >nul
goto loop
