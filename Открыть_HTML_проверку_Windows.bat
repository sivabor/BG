@echo off
setlocal
chcp 65001 >nul
set "ROOT=%~dp0"
set "HTML_FILE=%ROOT%Проверить_BG_Limits_HTML.html"

echo Открываю HTML-проверку BG ^& Limits...
if not exist "%HTML_FILE%" (
    echo [ОШИБКА] Не найден файл: %HTML_FILE%
    echo Убедитесь, что BAT-файл лежит рядом с HTML-файлом в корне проекта.
    pause
    exit /b 1
)
start "" "%HTML_FILE%"
exit /b 0
