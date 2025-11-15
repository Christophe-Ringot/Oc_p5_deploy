#!/bin/bash
# Script de démarrage rapide pour le développement local avec Docker Compose

set -e

echo "🚀 Démarrage de l'environnement de développement local..."

# Vérifier si .env existe
if [ ! -f .env ]; then
    echo "❌ Fichier .env non trouvé!"
    echo "Créez-le à partir de .env.example:"
    echo "  cp .env.example .env"
    echo "Puis éditez-le avec vos valeurs."
    exit 1
fi

echo "✅ Fichier .env trouvé"

# Vérifier si Docker est en cours d'exécution
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker n'est pas en cours d'exécution!"
    echo "Démarrez Docker Desktop et réessayez."
    exit 1
fi

echo "✅ Docker est en cours d'exécution"

# Construire et démarrer les services
echo "📦 Construction et démarrage des services..."
docker-compose up -d --build

echo ""
echo "⏳ Attente du démarrage complet des services..."
sleep 5

# Vérifier l'état des services
echo ""
echo "📊 État des services:"
docker-compose ps

echo ""
echo "✅ Environnement prêt!"
echo ""
echo "📝 URLs disponibles:"
echo "  - API (Swagger): http://localhost:8000/docs"
echo "  - API (Health): http://localhost:8000/health"
echo "  - PgAdmin: http://localhost:8080"
echo ""
echo "📋 Commandes utiles:"
echo "  - Voir les logs: docker-compose logs -f"
echo "  - Voir les logs API: docker-compose logs -f api"
echo "  - Arrêter: docker-compose down"
echo "  - Redémarrer: docker-compose restart api"
echo ""
echo "🎉 Bon développement!"
