Schémas de données
==================

Cette page documente les schémas de données (modèles Pydantic et SQLAlchemy) utilisés par l'API.

Modèles Pydantic
----------------

EmployeeInput
~~~~~~~~~~~~

Modèle de validation pour les données d'entrée d'un employé lors d'une prédiction individuelle.

**Utilisation** : Corps de la requête POST ``/predict_one``

**Champs** :

.. list-table::
   :header-rows: 1
   :widths: 25 15 15 45

   * - Nom du champ
     - Type
     - Défaut
     - Description
   * - employee_id
     - Optional[int]
     - None
     - Identifiant unique de l'employé
   * - age
     - int
     - 35
     - Âge de l'employé en années
   * - nombre_heures_travaillees
     - int
     - 80
     - Nombre d'heures travaillées par mois
   * - annees_experience_totale
     - int
     - 10
     - Années d'expérience professionnelle totale
   * - annees_dans_l_entreprise
     - int
     - 5
     - Années passées dans l'entreprise actuelle
   * - annees_dans_le_poste_actuel
     - int
     - 2
     - Années dans le poste actuel
   * - annees_depuis_la_derniere_promotion
     - int
     - 1
     - Années depuis la dernière promotion
   * - revenu_mensuel
     - float
     - 5000.0
     - Revenu mensuel brut en euros
   * - heure_supplementaires
     - int
     - 0
     - Fait des heures supplémentaires (0: Non, 1: Oui)
   * - ayant_enfants
     - int
     - 1
     - A des enfants (0: Non, 1: Oui)
   * - distance_domicile_travail
     - float
     - 10.0
     - Distance entre domicile et travail en km
   * - departement
     - str
     - "Sales"
     - Département de l'employé
   * - niveau_education
     - int
     - 3
     - Niveau d'éducation (1-5)
   * - domaine_etude
     - str
     - "Life Sciences"
     - Domaine d'études
   * - genre
     - str
     - "Male"
     - Genre de l'employé
   * - poste
     - str
     - "Sales Executive"
     - Intitulé du poste
   * - statut_marital
     - str
     - "Married"
     - Statut marital
   * - nombre_experiences_precedentes
     - int
     - 2
     - Nombre d'entreprises précédentes
   * - note_evaluation_precedente
     - int
     - 3
     - Note de l'évaluation précédente (1-4)
   * - note_evaluation_actuelle
     - int
     - 3
     - Note de l'évaluation actuelle (1-4)
   * - augmentation_salaire_precedente
     - float
     - 0.15
     - Taux d'augmentation précédente (0.15 = 15%)
   * - satisfaction_employee_nature_travail
     - int
     - 3
     - Satisfaction nature du travail (1-4)
   * - satisfaction_employee_equilibre_pro_perso
     - int
     - 3
     - Satisfaction équilibre vie pro/perso (1-4)
   * - satisfaction_employee_environnement
     - int
     - 3
     - Satisfaction environnement de travail (1-4)
   * - satisfaction_employee_equipe
     - int
     - 3
     - Satisfaction avec l'équipe (1-4)
   * - implication_employee
     - int
     - 3
     - Niveau d'implication (1-4)
   * - annes_sous_responsable_actuel
     - int
     - 2
     - Années sous le responsable actuel
   * - nombre_employee_sous_responsabilite
     - int
     - 0
     - Nombre d'employés sous responsabilité
   * - niveau_hierarchique_poste
     - int
     - 2
     - Niveau hiérarchique du poste (1-5)
   * - nb_formations_suivies
     - int
     - 3
     - Nombre de formations suivies l'année dernière
   * - frequence_deplacement
     - str
     - "Travel_Rarely"
     - Fréquence de déplacement professionnel
   * - nombre_participation_pee
     - int
     - 1
     - Nombre de participations au PEE

**Valeurs possibles pour les champs catégoriels** :

Département
^^^^^^^^^^^

* "Sales"
* "Research & Development"
* "Human Resources"
* Autres départements selon vos données

Domaine d'études
^^^^^^^^^^^^^^^^

* "Life Sciences"
* "Medical"
* "Marketing"
* "Technical Degree"
* "Other"
* Autres selon vos données

Genre
^^^^^

* "Male"
* "Female"

Statut marital
^^^^^^^^^^^^^^

* "Single"
* "Married"
* "Divorced"

Fréquence de déplacement
^^^^^^^^^^^^^^^^^^^^^^^^

* "Non-Travel"
* "Travel_Rarely"
* "Travel_Frequently"

**Exemple JSON** :

.. code-block:: json

   {
     "employee_id": 999,
     "age": 35,
     "nombre_heures_travaillees": 80,
     "annees_experience_totale": 10,
     "annees_dans_l_entreprise": 5,
     "annees_dans_le_poste_actuel": 2,
     "annees_depuis_la_derniere_promotion": 1,
     "revenu_mensuel": 5000.0,
     "heure_supplementaires": 0,
     "ayant_enfants": 1,
     "distance_domicile_travail": 10.0,
     "departement": "Sales",
     "niveau_education": 3,
     "domaine_etude": "Life Sciences",
     "genre": "Male",
     "poste": "Sales Executive",
     "statut_marital": "Married",
     "nombre_experiences_precedentes": 2,
     "note_evaluation_precedente": 3,
     "note_evaluation_actuelle": 3,
     "augmentation_salaire_precedente": 0.15,
     "satisfaction_employee_nature_travail": 3,
     "satisfaction_employee_equilibre_pro_perso": 3,
     "satisfaction_employee_environnement": 3,
     "satisfaction_employee_equipe": 3,
     "implication_employee": 3,
     "annes_sous_responsable_actuel": 2,
     "nombre_employee_sous_responsabilite": 0,
     "niveau_hierarchique_poste": 2,
     "nb_formations_suivies": 3,
     "frequence_deplacement": "Travel_Rarely",
     "nombre_participation_pee": 1
   }

Modèles SQLAlchemy
------------------

Prediction
~~~~~~~~~~

Modèle de base de données pour stocker les prédictions.

**Table** : ``predictions``

**Champs** :

.. list-table::
   :header-rows: 1
   :widths: 20 15 65

   * - Nom du champ
     - Type SQL
     - Description
   * - id
     - Integer (PK)
     - Identifiant unique auto-incrémenté
   * - employee_id
     - Integer
     - Référence à l'employé (peut être NULL)
   * - prediction
     - Integer
     - Résultat de la prédiction (0: reste, 1: part)
   * - probability
     - Float
     - Probabilité que l'employé parte (0.0-1.0)
   * - probabilities
     - JSON
     - Tableau des probabilités [P(reste), P(part)]
   * - created_at
     - DateTime
     - Date et heure de création (timezone UTC)

**Indexes** :

* Index sur ``id`` (clé primaire)

**Exemple de représentation** :

.. code-block:: python

   <Prediction(id=1, employee_id=101, prediction=1, probability=0.785)>

**Exemple de données** :

.. code-block:: json

   {
     "id": 1,
     "employee_id": 101,
     "prediction": 1,
     "probability": 0.785,
     "probabilities": [0.215, 0.785],
     "created_at": "2025-11-15T10:30:00.000000"
   }

Schémas de réponse
------------------

PredictResponse
~~~~~~~~~~~~~~

Réponse de l'endpoint ``POST /predict`` (batch)

.. code-block:: json

   {
     "success": true,
     "total_employees": 150,
     "statistics": {
       "high_risk": 45,
       "low_risk": 105,
       "high_risk_percentage": 30.0
     },
     "predictions": [
       {
         "employee_id": 1,
         "employee_index": 0,
         "will_leave": true,
         "probability": 0.785,
         "risk_level": "HIGH"
       }
     ]
   }

PredictOneResponse
~~~~~~~~~~~~~~~~~

Réponse de l'endpoint ``POST /predict_one``

.. code-block:: json

   {
     "success": true,
     "prediction_id": 42,
     "prediction": {
       "will_leave": true,
       "probability": 0.785,
       "risk_level": "HIGH"
     }
   }

PredictionsListResponse
~~~~~~~~~~~~~~~~~~~~~~

Réponse de l'endpoint ``GET /predictions``

.. code-block:: json

   {
     "success": true,
     "total": 150,
     "skip": 0,
     "limit": 100,
     "predictions": [
       {
         "id": 1,
         "employee_id": 101,
         "prediction": 1,
         "probability": 0.785,
         "probabilities": [0.215, 0.785],
         "created_at": "2025-11-15T10:30:00"
       }
     ]
   }

PredictionDetailResponse
~~~~~~~~~~~~~~~~~~~~~~~

Réponse de l'endpoint ``GET /predictions/{id}``

.. code-block:: json

   {
     "success": true,
     "prediction": {
       "id": 42,
       "employee_id": 101,
       "prediction": 1,
       "probability": 0.785,
       "probabilities": [0.215, 0.785],
       "created_at": "2025-11-15T10:30:00"
     }
   }

ErrorResponse
~~~~~~~~~~~~

Réponse en cas d'erreur

.. code-block:: json

   {
     "success": false,
     "error": "Description de l'erreur",
     "error_type": "ExceptionType"
   }

HealthResponse
~~~~~~~~~~~~~

Réponse de l'endpoint ``GET /health``

.. code-block:: json

   {
     "status": "healthy",
     "model_loaded": true,
     "database_url_configured": true
   }

Validation des données
----------------------

Contraintes de validation
~~~~~~~~~~~~~~~~~~~~~~~~~

Les contraintes suivantes sont appliquées automatiquement par Pydantic :

**Âge** :

* Type: entier
* Plage recommandée: 18-70

**Revenu mensuel** :

* Type: float
* Valeur > 0

**Scores de satisfaction** :

* Type: entier
* Plage: 1-4

**Notes d'évaluation** :

* Type: entier
* Plage: 1-4

**Niveau d'éducation** :

* Type: entier
* Plage: 1-5

**Niveau hiérarchique** :

* Type: entier
* Plage: 1-5

Gestion des erreurs de validation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Si les données fournies ne respectent pas le schéma, une erreur 422 est retournée par FastAPI :

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
