Installation
============

Prérequis
---------

Avant d'installer l'API, assurez-vous d'avoir :

* **Python 3.11+** installé
* **PostgreSQL 12+** (ou SQLite pour développement)
* **pip** pour la gestion des packages
* **Git** pour cloner le repository
* **Virtualenv** (recommandé)

Cloner le projet
----------------

.. code-block:: bash

   git clone https://github.com/votre-repo/api-turnover.git
   cd api-turnover

Créer un environnement virtuel
------------------------------

Il est fortement recommandé d'utiliser un environnement virtuel :

.. code-block:: bash

   # Création de l'environnement virtuel
   python -m venv venv

   # Activation (Windows)
   venv\Scripts\activate

   # Activation (Linux/Mac)
   source venv/bin/activate

Installer les dépendances
-------------------------

.. code-block:: bash

   pip install -r requirements.txt

Dépendances principales
~~~~~~~~~~~~~~~~~~~~~~

Le fichier ``requirements.txt`` contient :

* **fastapi==0.120.1** : Framework web
* **uvicorn==0.38.0** : Serveur ASGI
* **SQLAlchemy==2.0.44** : ORM
* **psycopg2==2.9.11** : Driver PostgreSQL
* **pydantic==2.12.3** : Validation de données
* **scikit-learn==1.7.2** : Machine Learning
* **pandas==2.3.3** : Manipulation de données
* **numpy==2.3.4** : Calcul numérique
* **joblib==1.5.2** : Sérialisation du modèle
* **python-dotenv==1.2.1** : Gestion des variables d'environnement

Dépendances de développement
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Pour le développement et les tests :

* **pytest==8.4.2** : Framework de tests
* **pytest-cov==7.0.0** : Couverture de code
* **httpx==0.28.1** : Client HTTP pour tests

Configuration de la base de données
-----------------------------------

Option 1 : PostgreSQL (Production)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Installer PostgreSQL
^^^^^^^^^^^^^^^^^^^^^^^

Téléchargez et installez PostgreSQL depuis https://www.postgresql.org/download/

2. Créer la base de données
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: sql

   CREATE DATABASE turnover_db;
   CREATE USER turnover_user WITH PASSWORD 'votre_mot_de_passe';
   GRANT ALL PRIVILEGES ON DATABASE turnover_db TO turnover_user;

3. Charger les données initiales
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   python data/create_db.py

Option 2 : SQLite (Développement)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

SQLite est utilisé automatiquement si PostgreSQL n'est pas configuré.
Aucune configuration spéciale n'est nécessaire.

Configuration des variables d'environnement
-------------------------------------------

Créez un fichier ``.env`` à la racine du projet :

.. code-block:: bash

   # Configuration PostgreSQL
   POSTGRES_USER=turnover_user
   POSTGRES_PASSWORD=votre_mot_de_passe
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=turnover_db

   # URL complète de la base de données
   DATABASE_URL=postgresql://turnover_user:votre_mot_de_passe@localhost:5432/turnover_db

Pour SQLite (développement), laissez ces variables non définies.

Vérification du modèle ML
-------------------------

Le modèle pré-entraîné doit être présent dans :

.. code-block:: text

   app/model/full_pipeline.joblib

Si le fichier n'existe pas, vous devrez :

1. Entraîner le modèle avec vos données
2. Placer le fichier ``.joblib`` dans ``app/model/``

Lancement de l'API
-----------------

Mode développement
~~~~~~~~~~~~~~~~~

.. code-block:: bash

   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

Options :

* ``--reload`` : Rechargement automatique lors des modifications
* ``--host 0.0.0.0`` : Accessible depuis toutes les interfaces réseau
* ``--port 8000`` : Port d'écoute

Mode production
~~~~~~~~~~~~~~

.. code-block:: bash

   uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

Options supplémentaires :

* ``--workers 4`` : Nombre de workers (processus)
* Sans ``--reload`` pour de meilleures performances

Vérification de l'installation
------------------------------

1. Vérifier l'état de l'API
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   curl http://localhost:8000/health

Réponse attendue :

.. code-block:: json

   {
     "status": "healthy",
     "model_loaded": true,
     "database_url_configured": true
   }

2. Accéder à la documentation interactive
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ouvrez votre navigateur et allez à :

* **Swagger UI** : http://localhost:8000/docs
* **ReDoc** : http://localhost:8000/redoc

3. Tester un endpoint
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   curl http://localhost:8000/

Réponse attendue :

.. code-block:: json

   {
     "message": "API de prédiction de turnover",
     "version": "1.0.0",
     "endpoints": { ... }
   }

Résolution des problèmes courants
---------------------------------

Erreur de connexion à PostgreSQL
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problème** : ``connection refused`` ou ``could not connect to server``

**Solutions** :

1. Vérifiez que PostgreSQL est démarré
2. Vérifiez les variables d'environnement dans ``.env``
3. Vérifiez le fichier ``pg_hba.conf`` pour les permissions
4. Testez la connexion manuellement :

.. code-block:: bash

   psql -h localhost -U turnover_user -d turnover_db

Modèle non chargé
~~~~~~~~~~~~~~~~

**Problème** : ``model_loaded: false`` dans ``/health``

**Solutions** :

1. Vérifiez la présence du fichier ``app/model/full_pipeline.joblib``
2. Vérifiez les permissions de lecture
3. Consultez les logs au démarrage pour les erreurs

Erreur d'importation
~~~~~~~~~~~~~~~~~~~

**Problème** : ``ModuleNotFoundError``

**Solutions** :

1. Vérifiez que l'environnement virtuel est activé
2. Réinstallez les dépendances : ``pip install -r requirements.txt``
3. Vérifiez la version de Python : ``python --version``

Prochaines étapes
----------------

Maintenant que l'installation est terminée :

* Explorez la :doc:`api/index` pour utiliser les endpoints
* Testez l'API avec la documentation interactive : http://localhost:8000/docs
