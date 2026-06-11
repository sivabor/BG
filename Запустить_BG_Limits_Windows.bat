@echo off
setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 >nul

set "ROOT=%~dp0"
set "APP_DIR=%ROOT%bank_guarantee_tool"
set "REQ_FILE=%APP_DIR%\requirements.txt"
set "APP_FILE=%APP_DIR%\app.py"
set "RUNTIME_DIR=%ROOT%.windows_runtime"
set "PORTABLE_DIR=%RUNTIME_DIR%\python"
set "PORTABLE_PY=%PORTABLE_DIR%\python.exe"
set "PYTHON_ZIP=%RUNTIME_DIR%\python-embed.zip"
set "GET_PIP=%RUNTIME_DIR%\get-pip.py"
set "PYTHON_EMBED_URL=https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip"
set "GET_PIP_URL=https://bootstrap.pypa.io/get-pip.py"

cls
echo ===============================================================
echo  BG ^& Limits — запуск для Windows одним файлом
echo ===============================================================
echo.
echo Этот файл сам подготовит локальную среду рядом с проектом:
echo  - НЕ устанавливает приложение в Windows;
echo  - НЕ требует командной строки;
echo  - зависимости кладет в папку .windows_runtime;
echo  - после запуска откроет веб-приложение в браузере.
echo.

if not exist "%APP_FILE%" (
    echo [ОШИБКА] Не найден файл приложения:
    echo %APP_FILE%
    echo.
    echo Убедитесь, что этот BAT-файл лежит в корне проекта рядом с папкой bank_guarantee_tool.
    pause
    exit /b 1
)

set "PYTHON_EXE="
set "PYTHON_ARGS="

if exist "%PORTABLE_PY%" (
    set "PYTHON_EXE=%PORTABLE_PY%"
    set "PYTHON_ARGS="
    goto :python_ready
)

where py >nul 2>nul
if %errorlevel%==0 (
    py -3 -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)" >nul 2>nul
    if !errorlevel!==0 (
        set "PYTHON_EXE=py"
        set "PYTHON_ARGS=-3"
        goto :python_ready
    )
)

where python >nul 2>nul
if %errorlevel%==0 (
    python -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)" >nul 2>nul
    if !errorlevel!==0 (
        set "PYTHON_EXE=python"
        set "PYTHON_ARGS="
        goto :python_ready
    )
)

echo Python 3.11+ не найден. Скачаю портативный Python в папку проекта.
echo Для первого запуска нужен интернет. Системная установка Python не требуется.
echo.
if not exist "%RUNTIME_DIR%" mkdir "%RUNTIME_DIR%"
if exist "%PORTABLE_DIR%" rmdir /s /q "%PORTABLE_DIR%"
mkdir "%PORTABLE_DIR%"

echo [1/4] Скачиваю портативный Python...
powershell -NoProfile -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%PYTHON_EMBED_URL%' -OutFile '%PYTHON_ZIP%'"
if errorlevel 1 goto :download_error

echo [2/4] Распаковываю Python...
powershell -NoProfile -ExecutionPolicy Bypass -Command "Expand-Archive -Path '%PYTHON_ZIP%' -DestinationPath '%PORTABLE_DIR%' -Force"
if errorlevel 1 goto :download_error

if exist "%PORTABLE_DIR%\python311._pth" (
    powershell -NoProfile -ExecutionPolicy Bypass -Command "(Get-Content '%PORTABLE_DIR%\python311._pth') -replace '#import site','import site' | Set-Content '%PORTABLE_DIR%\python311._pth'"
)

if not exist "%PORTABLE_PY%" (
    echo [ОШИБКА] Не удалось подготовить портативный Python.
    pause
    exit /b 1
)

set "PYTHON_EXE=%PORTABLE_PY%"
set "PYTHON_ARGS="

echo [3/4] Скачиваю установщик pip...
powershell -NoProfile -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%GET_PIP_URL%' -OutFile '%GET_PIP%'"
if errorlevel 1 goto :download_error

echo [4/4] Подключаю pip к портативному Python...
"%PORTABLE_PY%" "%GET_PIP%" --no-warn-script-location
if errorlevel 1 goto :pip_error

goto :python_ready

:python_ready
echo Использую Python: "%PYTHON_EXE%" %PYTHON_ARGS%
echo.
echo Устанавливаю/проверяю библиотеки приложения...
"%PYTHON_EXE%" %PYTHON_ARGS% -m pip install --upgrade pip
if errorlevel 1 goto :pip_error
"%PYTHON_EXE%" %PYTHON_ARGS% -m pip install -r "%REQ_FILE%"
if errorlevel 1 goto :pip_error

echo.
echo ===============================================================
echo  Приложение запускается. Если браузер не открылся сам,
echo  откройте адрес: http://localhost:8501
echo ===============================================================
echo.
cd /d "%ROOT%"
"%PYTHON_EXE%" %PYTHON_ARGS% -m streamlit run "%APP_FILE%" --server.headless false --server.port 8501
if errorlevel 1 goto :run_error
exit /b 0

:download_error
echo.
echo [ОШИБКА] Не удалось скачать или распаковать файлы.
echo Проверьте интернет-соединение или корпоративные ограничения доступа.
echo После устранения проблемы запустите этот файл еще раз.
pause
exit /b 1

:pip_error
echo.
echo [ОШИБКА] Не удалось установить библиотеки приложения.
echo Чаще всего причина — нет интернета или корпоративный proxy блокирует PyPI.
echo После устранения проблемы запустите этот файл еще раз.
pause
exit /b 1

:run_error
echo.
echo [ОШИБКА] Приложение не запустилось.
echo Пришлите разработчику текст ошибки из этого окна.
pause
exit /b 1
