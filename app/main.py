from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import joblib
from app.utils.preprocessing import load_data_from_postgres, preprocess_input, safe_log_transform, SafeLogTransform, preprocess_single_employee
import os
from typing import Optional
from sqlalchemy.orm import Session
from database import get_db
from models import Prediction

app = FastAPI(
    title="API Prédiction Turnover",
    description="API pour prédire si des employés vont quitter l'entreprise",
    version="1.0.0"
)

DATABASE_URL = os.getenv("DATABASE_URL")


try:
    model_path = os.path.join(os.path.dirname(__file__), 'model', 'full_pipeline.joblib')
    pipeline = joblib.load(model_path)
    print("Pipeline chargé avec succès")
except Exception as e:
    print(f"Erreur lors du chargement du pipeline: {e}")
    pipeline = None


class EmployeeInput(BaseModel):
    employee_id: Optional[int] = None
    age: int = 35
    nombre_heures_travaillees: int = 80
    annees_experience_totale: int = 10
    annees_dans_l_entreprise: int = 5
    annees_dans_le_poste_actuel: int = 2
    annees_depuis_la_derniere_promotion: int = 1
    revenu_mensuel: float = 5000.0
    heure_supplementaires: int = 0
    ayant_enfants: int = 1
    distance_domicile_travail: float = 10.0
    departement: str = "Sales"
    niveau_education: int = 3
    domaine_etude: str = "Life Sciences"
    genre: str = "Male"
    poste: str = "Sales Executive"
    statut_marital: str = "Married"
    nombre_experiences_precedentes: int = 2
    note_evaluation_precedente: int = 3
    note_evaluation_actuelle: int = 3
    augmentation_salaire_precedente: float = 0.15
    satisfaction_employee_nature_travail: int = 3
    satisfaction_employee_equilibre_pro_perso: int = 3
    satisfaction_employee_environnement: int = 3
    satisfaction_employee_equipe: int = 3
    implication_employee: int = 3
    annes_sous_responsable_actuel: int = 2
    nombre_employee_sous_responsabilite: int = 0
    niveau_hierarchique_poste: int = 2
    nb_formations_suivies: int = 3
    frequence_deplacement: str = "Travel_Rarely"
    nombre_participation_pee: int = 1


@app.get("/")
async def root():
    return {
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

@app.get("/health")
async def health():
    return {
        "status": "healthy" if pipeline is not None else "unhealthy",
        "model_loaded": pipeline is not None,
        "database_url_configured": DATABASE_URL != "postgresql://user:password@localhost:5432/db_name"
    }


@app.post("/predict")
async def predict(db: Session = Depends(get_db)):
    if pipeline is None:
        return JSONResponse(
            status_code=503,
            content={
                "success": False,
                "error": "Le modèle n'est pas chargé. Vérifiez que full_pipeline.joblib existe."
            }
        )

    try:
        eval_df, sirh_df, sondage_df = load_data_from_postgres(DATABASE_URL)

        eval_df['id_employee'] = eval_df['eval_number'].astype(str).str.extract(r'(\d+)').astype(int)
        sondage_df['id_employee'] = sondage_df['code_sondage'].astype(str).str.extract(r'(\d+)').astype(int)

        merged_df = sirh_df.merge(eval_df, on='id_employee', how='inner')\
                           .merge(sondage_df, on='id_employee', how='inner')
        employee_ids = merged_df['id_employee'].values

        X = preprocess_input(eval_df, sirh_df, sondage_df)

        if len(X) == 0:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "error": "Aucune donnée après preprocessing (vérifiez les merge)"
                }
            )

        predictions = pipeline.predict(X)
        probabilities_full = pipeline.predict_proba(X)
        probabilities = probabilities_full[:, 1]

        results = []
        for i, (emp_id, pred, proba, proba_full) in enumerate(zip(employee_ids, predictions, probabilities, probabilities_full)):
            db_prediction = Prediction(
                employee_id=int(emp_id),
                prediction=int(pred),
                probability=float(proba),
                probabilities=proba_full.tolist()
            )
            db.add(db_prediction)

            results.append({
                "employee_id": int(emp_id),
                "employee_index": i,
                "will_leave": bool(pred),
                "probability": round(float(proba), 3),
                "risk_level": "HIGH" if proba > 0.50 else "LOW"
            })

        db.commit()

        high_risk_count = sum(1 for r in results if r["risk_level"] == "HIGH")
        low_risk_count = len(results) - high_risk_count

        return {
            "success": True,
            "total_employees": len(results),
            "statistics": {
                "high_risk": high_risk_count,
                "low_risk": low_risk_count,
                "high_risk_percentage": round((high_risk_count / len(results)) * 100, 2)
            },
            "predictions": results
        }

    except Exception as e:
        db.rollback()
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
        )


@app.post("/predict_one")
async def predict_one(employee: EmployeeInput, db: Session = Depends(get_db)):
    if pipeline is None:
        return JSONResponse(
            status_code=503,
            content={
                "success": False,
                "error": "Le modèle n'est pas chargé. Vérifiez que full_pipeline.joblib existe."
            }
        )

    try:
        employee_dict = employee.model_dump()
        X = preprocess_single_employee(employee_dict)

        prediction = pipeline.predict(X)[0]
        probabilities = pipeline.predict_proba(X)[0]
        probability = float(probabilities[1])

        db_prediction = Prediction(
            employee_id=employee_dict.get('employee_id'),
            prediction=int(prediction),
            probability=probability,
            probabilities=probabilities.tolist()
        )
        db.add(db_prediction)
        db.commit()
        db.refresh(db_prediction)

        return {
            "success": True,
            "prediction_id": db_prediction.id,
            "prediction": {
                "will_leave": bool(prediction),
                "probability": round(probability, 3),
                "risk_level": "HIGH" if probability > 0.50 else "LOW"
            }
        }

    except Exception as e:
        db.rollback()
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
        )


@app.get("/predictions")
async def get_all_predictions(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    try:
        predictions = db.query(Prediction).offset(skip).limit(limit).all()
        total = db.query(Prediction).count()

        return {
            "success": True,
            "total": total,
            "skip": skip,
            "limit": limit,
            "predictions": [
                {
                    "id": pred.id,
                    "employee_id": pred.employee_id,
                    "prediction": pred.prediction,
                    "probability": pred.probability,
                    "probabilities": pred.probabilities,
                    "created_at": pred.created_at.isoformat() if pred.created_at else None
                }
                for pred in predictions
            ]
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
        )


@app.get("/predictions/{prediction_id}")
async def get_prediction(prediction_id: int, db: Session = Depends(get_db)):
    try:
        prediction = db.query(Prediction).filter(Prediction.id == prediction_id).first()

        if not prediction:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "error": f"Prédiction avec l'ID {prediction_id} non trouvée"
                }
            )

        return {
            "success": True,
            "prediction": {
                "id": prediction.id,
                "employee_id": prediction.employee_id,
                "prediction": prediction.prediction,
                "probability": prediction.probability,
                "probabilities": prediction.probabilities,
                "created_at": prediction.created_at.isoformat() if prediction.created_at else None
            }
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
        )


@app.delete("/predictions/{prediction_id}")
async def delete_prediction(prediction_id: int, db: Session = Depends(get_db)):
    try:
        prediction = db.query(Prediction).filter(Prediction.id == prediction_id).first()

        if not prediction:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "error": f"Prédiction avec l'ID {prediction_id} non trouvée"
                }
            )

        db.delete(prediction)
        db.commit()

        return {
            "success": True,
            "message": f"Prédiction {prediction_id} supprimée avec succès"
        }
    except Exception as e:
        db.rollback()
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
