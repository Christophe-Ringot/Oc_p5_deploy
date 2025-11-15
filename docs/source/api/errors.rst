Gestion des erreurs
===================

Cette page décrit comment l'API gère les erreurs et les codes de statut HTTP retournés.

Format des erreurs
------------------

Toutes les erreurs suivent un format JSON cohérent :

.. code-block:: json

   {
     "success": false,
     "error": "Description lisible de l'erreur",
     "error_type": "TypeError"
   }

Champs de la réponse d'erreur
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* ``success`` : Toujours ``false`` pour une erreur
* ``error`` : Message d'erreur descriptif en français
* ``error_type`` : Type de l'exception Python (optionnel)

Codes de statut HTTP
--------------------

200 OK
~~~~~~

**Signification** : Requête réussie

**Exemple** :

.. code-block:: bash

   GET /health
   # Réponse: 200 OK

**Cas d'utilisation** :

* Requêtes GET réussies
* Prédictions effectuées avec succès
* Suppression réussie

400 Bad Request
~~~~~~~~~~~~~~

**Signification** : Requête malformée ou données invalides

**Exemple** :

.. code-block:: json

   {
     "detail": [
       {
         "loc": ["body", "age"],
         "msg": "value is not a valid integer",
         "type": "type_error.integer"
       }
     ]
   }

**Causes courantes** :

* Type de données incorrect
* Champ requis manquant
* Format JSON invalide
* Valeur hors limites

**Comment corriger** :

1. Vérifiez que le JSON est bien formé
2. Vérifiez les types de données
3. Consultez la documentation des schémas
4. Utilisez la documentation interactive (``/docs``)

404 Not Found
~~~~~~~~~~~~

**Signification** : Ressource non trouvée

**Exemple** :

.. code-block:: json

   {
     "success": false,
     "error": "Prédiction avec l'ID 999 non trouvée"
   }

**Cas d'utilisation** :

* Prédiction avec un ID inexistant
* Aucune donnée après preprocessing
* Endpoint inexistant

**Comment corriger** :

1. Vérifiez l'ID de la ressource
2. Consultez la liste des ressources disponibles
3. Vérifiez l'URL de l'endpoint

422 Unprocessable Entity
~~~~~~~~~~~~~~~~~~~~~~~~

**Signification** : Validation Pydantic échouée

**Exemple** :

.. code-block:: json

   {
     "detail": [
       {
         "loc": ["body", "age"],
         "msg": "ensure this value is greater than 0",
         "type": "value_error.number.not_gt",
         "ctx": {"limit_value": 0}
       }
     ]
   }

**Causes courantes** :

* Contrainte de validation non respectée
* Type incompatible
* Valeur manquante pour un champ requis

**Comment corriger** :

1. Lisez le message d'erreur dans ``detail``
2. Consultez les contraintes du schéma
3. Ajustez vos données

500 Internal Server Error
~~~~~~~~~~~~~~~~~~~~~~~~~

**Signification** : Erreur interne du serveur

**Exemple** :

.. code-block:: json

   {
     "success": false,
     "error": "Database connection failed",
     "error_type": "OperationalError"
   }

**Causes courantes** :

* Erreur de connexion à la base de données
* Erreur dans le preprocessing
* Erreur du modèle ML
* Exception non gérée

**Comment corriger** :

1. Vérifiez les logs du serveur
2. Vérifiez la connexion à la base de données
3. Vérifiez que le modèle est chargé (``/health``)
4. Contactez l'administrateur si le problème persiste

503 Service Unavailable
~~~~~~~~~~~~~~~~~~~~~~~

**Signification** : Service temporairement indisponible

**Exemple** :

.. code-block:: json

   {
     "success": false,
     "error": "Le modèle n'est pas chargé. Vérifiez que full_pipeline.joblib existe."
   }

**Causes courantes** :

* Modèle ML non chargé
* Base de données inaccessible
* Service en maintenance

**Comment corriger** :

1. Vérifiez que le fichier modèle existe
2. Redémarrez le service
3. Consultez ``/health`` pour diagnostiquer

Erreurs par endpoint
--------------------

POST /predict
~~~~~~~~~~~~

**Erreurs possibles** :

.. list-table::
   :header-rows: 1
   :widths: 10 30 60

   * - Code
     - Erreur
     - Solution
   * - 503
     - Modèle non chargé
     - Vérifier la présence de ``full_pipeline.joblib``
   * - 404
     - Aucune donnée après preprocessing
     - Vérifier les données dans les tables sources
   * - 500
     - Erreur de connexion BDD
     - Vérifier ``DATABASE_URL`` dans ``.env``
   * - 500
     - Erreur lors du merge
     - Vérifier la cohérence des ``id_employee``

**Exemple de gestion** :

.. code-block:: python

   response = requests.post('http://localhost:8000/predict')
   data = response.json()

   if response.status_code == 503:
       print("Le modèle n'est pas disponible")
   elif response.status_code == 404:
       print("Aucune donnée à prédire")
   elif not data.get('success'):
       print(f"Erreur: {data.get('error')}")

POST /predict_one
~~~~~~~~~~~~~~~~

**Erreurs possibles** :

.. list-table::
   :header-rows: 1
   :widths: 10 30 60

   * - Code
     - Erreur
     - Solution
   * - 503
     - Modèle non chargé
     - Vérifier la présence du modèle
   * - 422
     - Validation échouée
     - Vérifier les types et valeurs des champs
   * - 500
     - Erreur de preprocessing
     - Vérifier les valeurs fournies

**Exemple de gestion** :

.. code-block:: python

   employee_data = {"age": 35, "revenu_mensuel": 5000.0}
   response = requests.post(
       'http://localhost:8000/predict_one',
       json=employee_data
   )

   if response.status_code == 422:
       errors = response.json()['detail']
       for error in errors:
           field = error['loc'][-1]
           message = error['msg']
           print(f"Erreur sur {field}: {message}")

GET /predictions
~~~~~~~~~~~~~~~

**Erreurs possibles** :

.. list-table::
   :header-rows: 1
   :widths: 10 30 60

   * - Code
     - Erreur
     - Solution
   * - 500
     - Erreur de connexion BDD
     - Vérifier la connexion à la base

GET /predictions/{id}
~~~~~~~~~~~~~~~~~~~~

**Erreurs possibles** :

.. list-table::
   :header-rows: 1
   :widths: 10 30 60

   * - Code
     - Erreur
     - Solution
   * - 404
     - Prédiction non trouvée
     - Vérifier l'ID de la prédiction
   * - 422
     - ID invalide
     - Fournir un entier valide
   * - 500
     - Erreur de connexion BDD
     - Vérifier la connexion

DELETE /predictions/{id}
~~~~~~~~~~~~~~~~~~~~~~~

**Erreurs possibles** :

.. list-table::
   :header-rows: 1
   :widths: 10 30 60

   * - Code
     - Erreur
     - Solution
   * - 404
     - Prédiction non trouvée
     - Vérifier l'ID de la prédiction
   * - 500
     - Erreur lors de la suppression
     - Vérifier les contraintes de base de données

Gestion des erreurs réseau
--------------------------

Timeouts
~~~~~~~~

Définissez toujours un timeout pour éviter les blocages :

.. code-block:: python

   import requests

   try:
       response = requests.post(
           'http://localhost:8000/predict',
           timeout=30  # 30 secondes
       )
   except requests.exceptions.Timeout:
       print("La requête a pris trop de temps")

Erreurs de connexion
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import requests

   try:
       response = requests.get('http://localhost:8000/health')
   except requests.exceptions.ConnectionError:
       print("Impossible de se connecter à l'API")

Bonnes pratiques
----------------

1. Toujours vérifier le champ ``success``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   response = requests.post(url, json=data)
   result = response.json()

   if result.get('success'):
       # Traiter les données
       pass
   else:
       # Gérer l'erreur
       error = result.get('error')
       print(f"Erreur: {error}")

2. Gérer les codes HTTP
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   if response.status_code == 200:
       # Succès
       pass
   elif response.status_code == 404:
       # Non trouvé
       pass
   elif response.status_code >= 500:
       # Erreur serveur
       pass

3. Implémenter des retries
~~~~~~~~~~~~~~~~~~~~~~~~~~

Pour les erreurs temporaires (500, 503) :

.. code-block:: python

   from requests.adapters import HTTPAdapter
   from requests.packages.urllib3.util.retry import Retry

   session = requests.Session()
   retry = Retry(
       total=3,
       backoff_factor=0.5,
       status_forcelist=[500, 502, 503, 504]
   )
   adapter = HTTPAdapter(max_retries=retry)
   session.mount('http://', adapter)

   response = session.post(url, json=data)

4. Logger les erreurs
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import logging

   logger = logging.getLogger(__name__)

   try:
       response = requests.post(url, json=data)
       response.raise_for_status()
   except requests.exceptions.HTTPError as e:
       logger.error(f"Erreur HTTP: {e}")
       logger.error(f"Réponse: {e.response.text}")

Debugging
---------

Vérifier l'état de l'API
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   curl http://localhost:8000/health

Activer les logs détaillés
~~~~~~~~~~~~~~~~~~~~~~~~~~

Démarrer Uvicorn avec le niveau de log DEBUG :

.. code-block:: bash

   uvicorn app.main:app --log-level debug

Utiliser la documentation interactive
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Swagger UI permet de tester les endpoints et voir les erreurs :

http://localhost:8000/docs

Consulter les logs du serveur
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Les logs contiennent des informations détaillées sur les erreurs :

.. code-block:: bash

   # Voir les logs en temps réel
   tail -f uvicorn.log
