Endpoints
=========

Cette page documente tous les endpoints disponibles dans l'API.

Root
----

.. http:get:: /

   Point d'entrée de l'API. Retourne les informations générales et la liste des endpoints disponibles.

   **Exemple de requête** :

   .. code-block:: bash

      curl http://localhost:8000/

   **Exemple de réponse** :

   .. code-block:: json

      {
        "message": "API de prédiction de turnover",
        "version": "1.0.0",
        "endpoints": {
          "predict": "POST /predict - Prédire le turnover pour tous les employés en BDD",
          "predict_one": "POST /predict_one - Prédire le turnover pour un employé via input",
          "predictions": "GET /predictions - Récupérer toutes les prédictions enregistrées",
          "prediction_by_id": "GET /predictions/{id} - Récupérer une prédiction par ID",
          "delete_prediction": "DELETE /predictions/{id} - Supprimer une prédiction",
          "health": "GET /health - Vérifier l'état de l'API",
          "docs": "GET /docs - Documentation interactive"
        }
      }

   :statuscode 200: Succès

Health Check
------------

.. http:get:: /health

   Vérifie l'état de santé de l'API et de ses dépendances.

   **Exemple de requête** :

   .. code-block:: bash

      curl http://localhost:8000/health

   **Exemple de réponse** :

   .. code-block:: json

      {
        "status": "healthy",
        "model_loaded": true,
        "database_url_configured": true
      }

   :statuscode 200: Succès

   **Détails des champs** :

   * ``status`` : ``healthy`` si le modèle est chargé, ``unhealthy`` sinon
   * ``model_loaded`` : ``true`` si le pipeline ML est chargé
   * ``database_url_configured`` : ``true`` si la BDD est configurée correctement

Prédiction Batch
----------------

.. http:post:: /predict

   Prédit le turnover pour tous les employés présents dans la base de données.

   Cette route :

   1. Charge les données des 3 tables (SIRH, Évaluations, Sondages)
   2. Fusionne les données par ``id_employee``
   3. Applique le preprocessing et feature engineering
   4. Effectue les prédictions via le modèle ML
   5. Stocke les résultats en base de données
   6. Retourne les statistiques et détails

   **Exemple de requête** :

   .. code-block:: bash

      curl -X POST http://localhost:8000/predict

   **Exemple de réponse (succès)** :

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
          },
          {
            "employee_id": 2,
            "employee_index": 1,
            "will_leave": false,
            "probability": 0.234,
            "risk_level": "LOW"
          }
        ]
      }

   **Exemple de réponse (erreur)** :

   .. code-block:: json

      {
        "success": false,
        "error": "Aucune donnée après preprocessing",
        "error_type": "ValueError"
      }

   :statuscode 200: Prédictions effectuées avec succès
   :statuscode 404: Aucune donnée trouvée après preprocessing
   :statuscode 500: Erreur lors du traitement
   :statuscode 503: Modèle non chargé

   **Détails de la réponse** :

   * ``total_employees`` : Nombre total d'employés analysés
   * ``statistics.high_risk`` : Nombre d'employés à risque élevé (probabilité > 0.50)
   * ``statistics.low_risk`` : Nombre d'employés à risque faible
   * ``statistics.high_risk_percentage`` : Pourcentage d'employés à risque élevé
   * ``predictions[].employee_id`` : ID de l'employé
   * ``predictions[].will_leave`` : Prédiction binaire (true/false)
   * ``predictions[].probability`` : Probabilité de départ (0-1)
   * ``predictions[].risk_level`` : Niveau de risque (HIGH/LOW)

Prédiction Individuelle
-----------------------

.. http:post:: /predict_one

   Prédit le turnover pour un seul employé à partir de données fournies en entrée.

   **Exemple de requête** :

   .. code-block:: bash

      curl -X POST http://localhost:8000/predict_one \
        -H "Content-Type: application/json" \
        -d '{
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
        }'

   **Paramètres du body (JSON)** :

   Tous les champs ont des valeurs par défaut. Seuls les champs à modifier sont nécessaires.

   * ``employee_id`` (optionnel) : Identifiant de l'employé
   * ``age`` : Âge de l'employé (défaut: 35)
   * ``nombre_heures_travaillees`` : Heures travaillées par mois (défaut: 80)
   * ``annees_experience_totale`` : Années d'expérience totale (défaut: 10)
   * ``annees_dans_l_entreprise`` : Années dans l'entreprise (défaut: 5)
   * ``annees_dans_le_poste_actuel`` : Années dans le poste actuel (défaut: 2)
   * ``annees_depuis_la_derniere_promotion`` : Années depuis promotion (défaut: 1)
   * ``revenu_mensuel`` : Revenu mensuel en euros (défaut: 5000.0)
   * ``heure_supplementaires`` : Heures supplémentaires (0 ou 1) (défaut: 0)
   * ``ayant_enfants`` : A des enfants (0 ou 1) (défaut: 1)
   * ``distance_domicile_travail`` : Distance en km (défaut: 10.0)
   * ``departement`` : Département (défaut: "Sales")
   * ``niveau_education`` : Niveau d'éducation 1-5 (défaut: 3)
   * ``domaine_etude`` : Domaine d'études (défaut: "Life Sciences")
   * ``genre`` : Genre (défaut: "Male")
   * ``poste`` : Intitulé du poste (défaut: "Sales Executive")
   * ``statut_marital`` : Statut marital (défaut: "Married")
   * ``nombre_experiences_precedentes`` : Nombre d'expériences (défaut: 2)
   * ``note_evaluation_precedente`` : Note 1-4 (défaut: 3)
   * ``note_evaluation_actuelle`` : Note 1-4 (défaut: 3)
   * ``augmentation_salaire_precedente`` : Taux d'augmentation (défaut: 0.15)
   * ``satisfaction_employee_nature_travail`` : Score 1-4 (défaut: 3)
   * ``satisfaction_employee_equilibre_pro_perso`` : Score 1-4 (défaut: 3)
   * ``satisfaction_employee_environnement`` : Score 1-4 (défaut: 3)
   * ``satisfaction_employee_equipe`` : Score 1-4 (défaut: 3)
   * ``implication_employee`` : Score 1-4 (défaut: 3)
   * ``annes_sous_responsable_actuel`` : Années sous le manager (défaut: 2)
   * ``nombre_employee_sous_responsabilite`` : Nombre de subordonnés (défaut: 0)
   * ``niveau_hierarchique_poste`` : Niveau hiérarchique 1-5 (défaut: 2)
   * ``nb_formations_suivies`` : Nombre de formations (défaut: 3)
   * ``frequence_deplacement`` : Fréquence ("Travel_Rarely", "Travel_Frequently", "Non-Travel")
   * ``nombre_participation_pee`` : Participation au PEE (défaut: 1)

   **Exemple de réponse (succès)** :

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

   :statuscode 200: Prédiction effectuée avec succès
   :statuscode 400: Données invalides
   :statuscode 500: Erreur lors du traitement
   :statuscode 503: Modèle non chargé

Récupérer toutes les prédictions
--------------------------------

.. http:get:: /predictions

   Récupère toutes les prédictions stockées en base de données avec pagination.

   **Paramètres de requête** :

   * ``skip`` (optionnel) : Nombre d'éléments à sauter (défaut: 0)
   * ``limit`` (optionnel) : Nombre maximum d'éléments à retourner (défaut: 100)

   **Exemple de requête** :

   .. code-block:: bash

      curl "http://localhost:8000/predictions?skip=0&limit=10"

   **Exemple de réponse** :

   .. code-block:: json

      {
        "success": true,
        "total": 150,
        "skip": 0,
        "limit": 10,
        "predictions": [
          {
            "id": 1,
            "employee_id": 101,
            "prediction": 1,
            "probability": 0.785,
            "probabilities": [0.215, 0.785],
            "created_at": "2025-11-15T10:30:00"
          },
          {
            "id": 2,
            "employee_id": 102,
            "prediction": 0,
            "probability": 0.234,
            "probabilities": [0.766, 0.234],
            "created_at": "2025-11-15T10:30:01"
          }
        ]
      }

   :statuscode 200: Succès
   :statuscode 500: Erreur serveur

   **Détails de la réponse** :

   * ``total`` : Nombre total de prédictions en base
   * ``skip`` : Nombre d'éléments sautés
   * ``limit`` : Limite appliquée
   * ``predictions[].id`` : ID unique de la prédiction
   * ``predictions[].employee_id`` : ID de l'employé
   * ``predictions[].prediction`` : Prédiction (0 ou 1)
   * ``predictions[].probability`` : Probabilité de classe 1 (départ)
   * ``predictions[].probabilities`` : Tableau [P(reste), P(part)]
   * ``predictions[].created_at`` : Date de création (ISO 8601)

Récupérer une prédiction par ID
-------------------------------

.. http:get:: /predictions/{prediction_id}

   Récupère une prédiction spécifique par son ID.

   **Paramètres de chemin** :

   * ``prediction_id`` : ID de la prédiction

   **Exemple de requête** :

   .. code-block:: bash

      curl http://localhost:8000/predictions/42

   **Exemple de réponse (succès)** :

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

   **Exemple de réponse (non trouvé)** :

   .. code-block:: json

      {
        "success": false,
        "error": "Prédiction avec l'ID 42 non trouvée"
      }

   :statuscode 200: Prédiction trouvée
   :statuscode 404: Prédiction non trouvée
   :statuscode 500: Erreur serveur

Supprimer une prédiction
------------------------

.. http:delete:: /predictions/{prediction_id}

   Supprime une prédiction de la base de données.

   **Paramètres de chemin** :

   * ``prediction_id`` : ID de la prédiction à supprimer

   **Exemple de requête** :

   .. code-block:: bash

      curl -X DELETE http://localhost:8000/predictions/42

   **Exemple de réponse (succès)** :

   .. code-block:: json

      {
        "success": true,
        "message": "Prédiction 42 supprimée avec succès"
      }

   **Exemple de réponse (non trouvé)** :

   .. code-block:: json

      {
        "success": false,
        "error": "Prédiction avec l'ID 42 non trouvée"
      }

   :statuscode 200: Prédiction supprimée
   :statuscode 404: Prédiction non trouvée
   :statuscode 500: Erreur serveur

   .. warning::

      Cette opération est irréversible. Assurez-vous de vouloir supprimer la prédiction
      avant d'effectuer cette action.
