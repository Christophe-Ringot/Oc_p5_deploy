@echo off
REM Script de démarrage rapide pour le développement local avec Docker Compose (Windows)

echo 🚀 Démarrage de l'environnement de développement local...
echo.

REM Vérifier si .env existe
if not exist .env (
    echo ❌ Fichier .env non trouvé!
    echo Créez-le à partir de .env.example:
    echo   copy .env.example .env
    echo Puis éditez-le avec vos valeurs.
    exit /b 1
)

echo ✅ Fichier .env trouvé

REM Vérifier si Docker est en cours d'exécution
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker n'est pas en cours d'exécution!
    echo Démarrez Docker Desktop et réessayez.
    exit /b 1
)

echo ✅ Docker est en cours d'exécution

REM Construire et démarrer les services
echo 📦 Construction et démarrage des services...
docker-compose up -d --build

echo.
echo ⏳ Attente du démarrage complet des services...
timeout /t 5 /nobreak >nul

REM Vérifier l'état des services
echo.
echo 📊 État des services:
docker-compose ps

echo.
echo ✅ Environnement prêt!
echo.
echo 📝 URLs disponibles:
echo   - API (Swagger): http://localhost:8000/docs
echo   - API (Health): http://localhost:8000/health
echo   - PgAdmin: http://localhost:8080
echo.
echo 📋 Commandes utiles:
echo   - Voir les logs: docker-compose logs -f
echo   - Voir les logs API: docker-compose logs -f api
echo   - Arrêter: docker-compose down
echo   - Redémarrer: docker-compose restart api
echo.
echo 🎉 Bon développement!
echo.
pause
