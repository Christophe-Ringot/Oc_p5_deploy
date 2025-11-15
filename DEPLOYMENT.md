# Guide de déploiement

## Configuration de la base de données

L'application détecte automatiquement l'environnement et configure la base de données appropriée :

### 🚀 Hugging Face Spaces

Sur Hugging Face Spaces, l'application utilise **automatiquement SQLite**. Aucune configuration n'est nécessaire.

La détection se fait via la variable d'environnement `SPACE_ID` qui est automatiquement définie par Hugging Face.

**Logs attendus :**
```
🔧 Utilisation de SQLite (Hugging Face ou environnement sans PostgreSQL)
Création des tables...
✓ Tables des modèles créées
✓ Table 'extrait_sirh' créée avec 1470 lignes
✓ Table 'extrait_eval' créée avec 1470 lignes
✓ Table 'extrait_sondage' créée avec 1470 lignes
✅ Base de données initialisée avec succès !
```

### 💻 Développement local avec PostgreSQL

Pour utiliser PostgreSQL en local, configurez les variables d'environnement suivantes dans un fichier `.env` :

```env
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_database_name
```

**Important :** Ne définissez pas `SPACE_ID` en local.

**Logs attendus :**
```
🔧 Utilisation de PostgreSQL: localhost:5432/your_database_name
```

### 🧪 Tests CI/CD (GitHub Actions)

Les tests utilisent automatiquement PostgreSQL via les services Docker configurés dans `.github/workflows/`.

## Dépannage

### Erreur "connection to server at localhost, port 5432 failed"

Cette erreur indique que l'application essaie de se connecter à PostgreSQL alors qu'elle devrait utiliser SQLite.

**Causes possibles :**
1. Les variables d'environnement PostgreSQL sont définies sur Hugging Face
2. La variable `SPACE_ID` n'est pas détectée

**Solution :**
Vérifiez que les variables PostgreSQL (`POSTGRES_USER`, `DB_PORT`, etc.) ne sont **pas** définies dans les secrets de votre Hugging Face Space.

### Vérifier la configuration active

Consultez les logs au démarrage de l'application. Vous devriez voir soit :
- `🔧 Utilisation de SQLite (Hugging Face ou environnement sans PostgreSQL)`
- `🔧 Utilisation de PostgreSQL: host:port/database`

## Architecture

```
├── app/
│   ├── database.py       # Configuration auto de la base de données
│   ├── init_db.py        # Initialisation des tables au démarrage
│   └── main.py           # API FastAPI
├── data/                 # Fichiers CSV chargés automatiquement
│   ├── extrait_sirh.csv
│   ├── extrait_eval.csv
│   └── extrait_sondage.csv
└── tests/                # Tests unitaires avec couverture >75%
```
