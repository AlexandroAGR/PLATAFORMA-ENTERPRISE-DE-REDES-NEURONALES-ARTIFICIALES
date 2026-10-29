@echo off
setlocal
cd /d "%~dp0apps\web"
echo =============================================
echo   NEUROLAB ENTERPRISE - DEMO SIMULADA
echo =============================================
where node >nul 2>nul
if errorlevel 1 (echo ERROR: Instala Node.js 20 o superior.& pause & exit /b 1)
if not exist "node_modules" (
  echo Instalando dependencias del frontend...
  call npm install
  if errorlevel 1 (echo ERROR instalando dependencias.& pause & exit /b 1)
)
echo Iniciando la aplicacion web...
call npm run dev
pause
