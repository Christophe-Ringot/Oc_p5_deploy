Référence API
=============

Cette section documente tous les endpoints disponibles dans l'API de Prédiction de Turnover.

.. toctree::
   :maxdepth: 2

   endpoints
   schemas
   errors

Base URL
--------

En développement local :

.. code-block:: text

   http://localhost:8000

En production :

.. code-block:: text

   https://votre-domaine.com

Authentification
---------------

Actuellement, l'API ne nécessite pas d'authentification. Pour une utilisation en production,
il est recommandé d'ajouter une couche d'authentification (API Key, OAuth2, etc.).

Format des réponses
------------------

Toutes les réponses sont au format JSON.

Réponse de succès
~~~~~~~~~~~~~~~~

.. code-block:: json

   {
     "success": true,
     "data": { ... }
   }

Réponse d'erreur
~~~~~~~~~~~~~~~

.. code-block:: json

   {
     "success": false,
     "error": "Description de l'erreur",
     "error_type": "TypeError"
   }

Codes de statut HTTP
-------------------

L'API utilise les codes HTTP standards :

* ``200 OK`` : Requête réussie
* ``201 Created`` : Ressource créée
* ``400 Bad Request`` : Données invalides
* ``404 Not Found`` : Ressource non trouvée
* ``500 Internal Server Error`` : Erreur serveur
* ``503 Service Unavailable`` : Service indisponible (ex: modèle non chargé)

Pagination
----------

Les endpoints qui retournent des listes supportent la pagination :

Paramètres de requête
~~~~~~~~~~~~~~~~~~~~

* ``skip`` : Nombre d'éléments à sauter (défaut: 0)
* ``limit`` : Nombre maximum d'éléments à retourner (défaut: 100)

Exemple
~~~~~~~

.. code-block:: bash

   GET /predictions?skip=20&limit=10

Limites de taux
--------------

Actuellement, aucune limite de taux n'est implémentée. Pour la production,
il est recommandé d'ajouter un rate limiting.

Documentation interactive
-------------------------

L'API fournit une documentation interactive accessible via :

* **Swagger UI** : ``/docs``
* **ReDoc** : ``/redoc``

Ces interfaces permettent de :

* Visualiser tous les endpoints
* Tester les requêtes directement
* Voir les schémas de données
* Télécharger la spécification OpenAPI

Exemple d'utilisation
---------------------

Utilisation avec curl
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Vérifier l'état de l'API
   curl http://localhost:8000/health

   # Obtenir les prédictions
   curl http://localhost:8000/predictions

   # Prédire pour un employé
   curl -X POST http://localhost:8000/predict_one \
     -H "Content-Type: application/json" \
     -d '{"age": 35, "revenu_mensuel": 5000, ...}'

Utilisation avec Python
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import requests

   # URL de base
   BASE_URL = "http://localhost:8000"

   # Vérifier l'état
   response = requests.get(f"{BASE_URL}/health")
   print(response.json())

   # Prédiction individuelle
   employee_data = {
       "age": 35,
       "revenu_mensuel": 5000.0,
       "annees_experience_totale": 10,
       # ... autres champs
   }

   response = requests.post(
       f"{BASE_URL}/predict_one",
       json=employee_data
   )
   print(response.json())

Utilisation avec JavaScript
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: javascript

   // Avec fetch API
   const BASE_URL = 'http://localhost:8000';

   // Vérifier l'état
   fetch(`${BASE_URL}/health`)
     .then(response => response.json())
     .then(data => console.log(data));

   // Prédiction individuelle
   const employeeData = {
     age: 35,
     revenu_mensuel: 5000.0,
     // ... autres champs
   };

   fetch(`${BASE_URL}/predict_one`, {
     method: 'POST',
     headers: {
       'Content-Type': 'application/json',
     },
     body: JSON.stringify(employeeData)
   })
     .then(response => response.json())
     .then(data => console.log(data));

Bonnes pratiques
---------------

Gestion des erreurs
~~~~~~~~~~~~~~~~~~

Toujours vérifier le champ ``success`` dans la réponse :

.. code-block:: python

   response = requests.post(url, json=data)
   result = response.json()

   if result.get('success'):
       # Traiter les données
       predictions = result['predictions']
   else:
       # Gérer l'erreur
       error = result.get('error')
       print(f"Erreur: {error}")

Validation des données
~~~~~~~~~~~~~~~~~~~~~

Assurez-vous que toutes les données requises sont fournies et valides
avant d'envoyer une requête.

Gestion des timeouts
~~~~~~~~~~~~~~~~~~~~

Définissez des timeouts appropriés, surtout pour les prédictions batch :

.. code-block:: python

   response = requests.post(url, json=data, timeout=30)

Versioning
----------

L'API est actuellement en version **1.0.0**.

Les changements de version suivront le versioning sémantique (SemVer) :

* **MAJOR** : Changements incompatibles
* **MINOR** : Nouvelles fonctionnalités compatibles
* **PATCH** : Corrections de bugs
