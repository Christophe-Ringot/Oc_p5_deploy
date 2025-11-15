Documentation API Prédiction Turnover
======================================

Bienvenue dans la documentation technique de l'API de Prédiction de Turnover.

Cette API, développée avec FastAPI, permet de prédire la probabilité qu'un employé quitte l'entreprise
en utilisant un modèle de machine learning entraîné sur des données RH.

.. toctree::
   :maxdepth: 2
   :caption: Table des matières:

   introduction
   installation
   api/index

Vue d'ensemble
--------------

L'API de Prédiction de Turnover est un système intelligent qui analyse les données des employés
pour identifier les risques de départ. Elle combine trois sources de données :

* **SIRH** : Données administratives et RH
* **Évaluations** : Données de performance
* **Sondages** : Données de satisfaction

Fonctionnalités principales
---------------------------

* Prédiction de turnover pour tous les employés en base de données
* Prédiction individuelle via saisie manuelle
* Stockage des prédictions dans une base de données
* API REST complète avec documentation interactive
* Gestion des prédictions (consultation, suppression)

Technologies utilisées
---------------------

* **FastAPI** : Framework web moderne et rapide
* **SQLAlchemy** : ORM pour la gestion de la base de données
* **Scikit-learn** : Machine Learning
* **PostgreSQL/SQLite** : Base de données
* **Pydantic** : Validation des données

Démarrage rapide
---------------

Installation
~~~~~~~~~~~~

.. code-block:: bash

   pip install -r requirements.txt

Configuration
~~~~~~~~~~~~~

Créez un fichier ``.env`` :

.. code-block:: bash

   DATABASE_URL=postgresql://user:password@localhost:5432/turnover_db
   POSTGRES_USER=user
   POSTGRES_PASSWORD=password
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=turnover_db

Lancement
~~~~~~~~~

.. code-block:: bash

   uvicorn app.main:app --reload

L'API sera disponible sur http://localhost:8000

Documentation interactive disponible sur http://localhost:8000/docs

Indices et tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
