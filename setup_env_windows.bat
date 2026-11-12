@echo off
rem Script para crear/activar el entorno virtual e instalar dependencias
rem El entorno virtual se crea en la misma carpeta donde está este .bat
rem Uso: setup_env_windows.bat [nombre_entorno]

setlocal

rem Cambiar al directorio del script (asegura que el venv se cree en esta carpeta)
pushd "%~dp0" >nul 2>&1
if %errorlevel% neq 0 (
    echo No se pudo cambiar al directorio del script (%~dp0).
    endlocal
    exit /b 1
)

rem Ayuda
if "%~1"=="-h" goto :usage
if "%~1"=="--help" goto :usage
if "%~1"=="/?" goto :usage

rem Nombre del entorno (opcional)
set "ENV_NAME=%~1"
if "%ENV_NAME%"=="" set "ENV_NAME=gestor-archivos-env"

echo Usando entorno: "%ENV_NAME%"

rem Detectar Python (preferir py -3 si está disponible)
py -3 --version >nul 2>&1
if %errorlevel%==0 (
    set "PY_LAUNCHER=py -3"
) else (
    python --version >nul 2>&1
    if %errorlevel%==0 (
        set "PY_LAUNCHER=python"
    ) else (
        echo Python no está instalado. Por favor instálalo antes de continuar.
        popd >nul 2>&1
        endlocal
        exit /b 1
    )
)

rem Crear el entorno virtual si no existe (en la carpeta del script)
if not exist "%ENV_NAME%\" (
    echo Creando el entorno virtual "%ENV_NAME%" en "%~dp0"...
    %PY_LAUNCHER% -m venv "%ENV_NAME%"
    if %errorlevel% neq 0 (
        echo Error creando el entorno virtual.
        popd >nul 2>&1
        endlocal
        exit /b 1
    )
) else (
    echo El entorno virtual "%ENV_NAME%" ya existe.
)

rem Activar el entorno virtual
call "%ENV_NAME%\Scripts\activate.bat"
if %errorlevel% neq 0 (
    echo No se pudo activar el entorno virtual.
    popd >nul 2>&1
    endlocal
    exit /b 1
)

rem Ruta al python del venv (asegura usar el python del entorno)
set "VENV_PY=%ENV_NAME%\Scripts\python.exe"

rem Comprobar requirements.txt
if not exist "requirements.txt" (
    echo No se encontró el archivo requirements.txt.
    echo Crea el archivo con las dependencias necesarias y vuelve a ejecutar el script.
    popd >nul 2>&1
    endlocal
    exit /b 1
)

rem Instalar dependencias (usar el python del venv)
%VENV_PY% -m ensurepip --default-pip >nul 2>&1
%VENV_PY% -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo Error actualizando pip en el entorno virtual.
    popd >nul 2>&1
    endlocal
    exit /b 1
)

echo Instalando dependencias desde requirements.txt...
%VENV_PY% -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Ocurrió un error instalando dependencias.
    popd >nul 2>&1
    endlocal
    exit /b 1
)

echo Dependencias instaladas correctamente.
echo El entorno está listo. Para desactivarlo, usa el comando "deactivate".

popd >nul 2>&1
endlocal
exit /b 0

:usage
echo Uso: %~n0 [nombre_entorno]
echo   Si no se especifica, se usa "gestor-archivos-env" como nombre del entorno.
echo Ejemplo: %~n0 my-env
exit /b 0