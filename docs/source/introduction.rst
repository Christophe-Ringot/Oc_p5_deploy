Introduction
============

Contexte
--------

Le turnover des employés représente un défi majeur pour les entreprises. La capacité à prédire
et anticiper les départs permet de :

* Mettre en place des actions de rétention ciblées
* Réduire les coûts liés au recrutement et à la formation
* Maintenir la continuité opérationnelle
* Améliorer la satisfaction et l'engagement des employés

Objectif de l'API
-----------------

L'API de Prédiction de Turnover a été développée pour fournir un outil fiable et accessible
permettant de :

1. **Analyser** les données des employés de manière systématique
2. **Prédire** la probabilité de départ de chaque employé
3. **Identifier** les employés à risque élevé
4. **Stocker** l'historique des prédictions pour analyse

Modèle de Machine Learning
--------------------------

Le modèle utilisé par l'API a été entraîné sur un ensemble de données historiques comprenant :

* Données démographiques (âge, genre, distance domicile-travail)
* Données professionnelles (poste, département, ancienneté)
* Données de performance (évaluations, formations)
* Données de satisfaction (environnement, équilibre vie pro/perso)
* Données de rémunération (salaire, augmentations)

Le pipeline complet inclut :

* **Préprocessing** : Nettoyage et transformation des données
* **Feature Engineering** : Création de variables dérivées
* **Modèle de classification** : Prédiction binaire (reste/part)
* **Calibration** : Estimation des probabilités

Sources de données
-----------------

L'API consomme trois types de données RH :

SIRH (Système d'Information RH)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Table ``extrait_sirh`` contenant :

* Identifiant employé
* Informations démographiques
* Informations contractuelles
* Historique professionnel
* Données de mobilité

Évaluations
~~~~~~~~~~~

Table ``extrait_eval`` contenant :

* Numéro d'évaluation
* Notes de performance
* Augmentations salariales
* Nombre d'expériences précédentes

Sondages
~~~~~~~~

Table ``extrait_sondage`` contenant :

* Code sondage
* Scores de satisfaction (travail, équilibre, environnement, équipe)
* Niveau d'implication
* Données managériales

Prochaines étapes
----------------

Pour commencer à utiliser l'API :

1. Consultez le :doc:`installation` pour installer l'environnement
2. Référez-vous à la :doc:`api/index` pour utiliser les endpoints
3. Testez l'API avec la documentation interactive : http://localhost:8000/docs
