# Guide Docker Compose

Ce guide explique comment lancer l'application complète avec Docker Compose en local.

## 🚀 Démarrage rapide

### 1. Configuration des variables d'environnement

Copiez le fichier `.env.example` vers `.env` et configurez vos valeurs:

```bash
cp .env.example .env
```

Éditez `.env` avec vos propres valeurs:
```env
POSTGRES_USER=myuser
POSTGRES_PASSWORD=mypassword
DB_NAME=turnover_db
PGADMIN_DEFAULT_EMAIL=admin@example.com
PGADMIN_DEFAULT_PASSWORD=adminpass
```

### 2. Lancer tous les services

```bash
docker-compose up -d
```

Cela démarre 3 services:
- **db**: Base de données PostgreSQL (port 5432)
- **api**: API FastAPI (port 8000)
- **pgadmin**: Interface web PgAdmin (port 8080)

### 3. Vérifier que tout fonctionne

**API:**
- Swagger UI: http://localhost:8000/docs
- Health check: http://localhost:8000/health

**PgAdmin:**
- Interface: http://localhost:8080
- Identifiants: ceux définis dans `.env`

## 📋 Services disponibles

### Service `db` - PostgreSQL

Base de données PostgreSQL avec:
- Healthcheck automatique
- Persistence des données via volume `local_pgdata`
- Port exposé: 5432

### Service `api` - FastAPI

API de prédiction de turnover avec:
- Hot-reload activé (les modifications du code sont détectées automatiquement)
- Connexion automatique à PostgreSQL
- Initialisation automatique de la base de données au démarrage
- Port exposé: 8000

**Volumes montés:**
- `./app:/app/app` - Code de l'application (hot-reload)
- `./data:/app/data` - Fichiers CSV

### Service `pgadmin` - Interface d'administration

Interface web pour gérer PostgreSQL:
- Port exposé: 8080
- Persistence des configurations via volume `pgadmin_data`

## 🛠️ Commandes utiles

### Démarrer les services
```bash
# Tout démarrer en arrière-plan
docker-compose up -d

# Tout démarrer avec logs
docker-compose up

# Démarrer seulement certains services
docker-compose up -d db api
```

### Voir les logs
```bash
# Tous les services
docker-compose logs -f

# Un service spécifique
docker-compose logs -f api
docker-compose logs -f db
```

### Arrêter les services
```bash
# Arrêter sans supprimer les volumes
docker-compose down

# Arrêter et supprimer les volumes (⚠️ perte de données)
docker-compose down -v
```

### Rebuild l'API après modification du Dockerfile
```bash
docker-compose up -d --build api
```

### Accéder au shell d'un container
```bash
# Shell de l'API
docker-compose exec api sh

# Shell de PostgreSQL
docker-compose exec db psql -U your_username -d turnover_db
```

## 🔍 Vérification de la configuration

### Vérifier que PostgreSQL est utilisé

Connectez-vous au container de l'API:
```bash
docker-compose exec api python test_database_url.py
```

Vous devriez voir:
```
DATABASE_URL: postgresql://...
✅ PostgreSQL est utilisé
```

### Vérifier les données dans PostgreSQL

Via PgAdmin (http://localhost:8080):
1. Connectez-vous avec vos identifiants
2. Ajoutez un serveur:
   - Host: `db` (nom du service Docker)
   - Port: `5432`
   - Database: `turnover_db`
   - Username/Password: ceux de `.env`
3. Explorez les tables:
   - `extrait_sirh` (1470 lignes)
   - `extrait_eval` (1470 lignes)
   - `extrait_sondage` (1470 lignes)
   - `predictions` (créée automatiquement)

Ou via ligne de commande:
```bash
docker-compose exec db psql -U your_username -d turnover_db -c "SELECT COUNT(*) FROM extrait_sirh;"
```

## 🐛 Dépannage

### L'API ne démarre pas

**Vérifier les logs:**
```bash
docker-compose logs api
```

**Causes communes:**
- PostgreSQL pas encore prêt → Le healthcheck devrait gérer ça
- Variables d'environnement manquantes → Vérifiez `.env`
- Port 8000 déjà utilisé → Changez le port dans `docker-compose.yml`

### PostgreSQL refuse les connexions

**Vérifier que la base est prête:**
```bash
docker-compose exec db pg_isready -U your_username
```

### Reset complet

Pour repartir de zéro:
```bash
docker-compose down -v
docker-compose up -d
```

## 📊 Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   PgAdmin   │────>│  PostgreSQL │<────│   FastAPI   │
│  (port 8080)│     │  (port 5432)│     │  (port 8000)│
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │   Volumes   │
                    │  - pgdata   │
                    │  - pgadmin  │
                    └─────────────┘
```

## 🌐 Différences avec Hugging Face

| Aspect | Docker Local | Hugging Face Spaces |
|--------|--------------|---------------------|
| Base de données | PostgreSQL | SQLite |
| Détection | Via variables d'env | Via `SPACE_ID` |
| Persistence | Volumes Docker | Système de fichiers |
| Port | 8000 | Assigné automatiquement |
| Hot-reload | ✅ Oui | ❌ Non |

## 🔐 Sécurité

**Important:**
- Ne committez JAMAIS le fichier `.env`
- Utilisez des mots de passe forts
- En production, utilisez Docker secrets ou un gestionnaire de secrets
