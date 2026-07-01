@echo off
REM deploy_setup.bat — Script para preparar el despliegue en Windows

echo.
echo 🚀 Preparando Sorteos Universales para Internet...
echo.

REM 1. Limpiar caché Python
echo 1️⃣  Limpiando archivos de caché...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /s /q *.pyc > nul 2>&1
del /s /q *.pyo > nul 2>&1
echo ✓ Caché limpiado

REM 2. Inicializar Git (si no existe)
if not exist .git (
    echo.
    echo 2️⃣  Inicializando repositorio Git...
    git init
    echo ✓ Git inicializado
) else (
    echo.
    echo 2️⃣  Git ya estaba inicializado
)

REM 3. Agregar todos los archivos
echo.
echo 3️⃣  Agregando archivos...
git add .
echo ✓ Archivos listos

REM 4. Commit inicial
echo.
echo 4️⃣  Creando commit...
git commit -m "Sorteos Universales - Listo para despliegue" || echo ℹ️  No hay cambios nuevos

REM 5. Resumen
echo.
echo ════════════════════════════════════════════
echo ✅ PREPARACIÓN COMPLETADA
echo ════════════════════════════════════════════
echo.
echo 📋 Próximos pasos:
echo.
echo 1. Crea un repositorio en GitHub:
echo    → Ve a https://github.com/new
echo    → Nombre: sorteos-universales
echo    → Copia el comando git remote
echo.
echo 2. Conecta este repositorio a GitHub:
echo    git remote add origin https://github.com/TU_USUARIO/sorteos-universales.git
echo    git branch -M main
echo    git push -u origin main
echo.
echo 3. En Render (recomendado):
echo    → Ve a https://render.com
echo    → Click en 'New +' 'Web Service'
echo    → Selecciona tu repositorio GitHub
echo    → Render detecta Flask automáticamente
echo    → Deploy! 🚀
echo.
echo 📖 Lee DEPLOY.md para instrucciones detalladas
echo.
pause
