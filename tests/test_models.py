import pytest
from app.models import Prediction
from datetime import datetime


def test_prediction_model_creation():
    prediction = Prediction(
        employee_id=123,
        prediction=1,
        probability=0.75,
        probabilities=[0.25, 0.75]
    )

    assert prediction.employee_id == 123
    assert prediction.prediction == 1
    assert prediction.probability == 0.75
    assert prediction.probabilities == [0.25, 0.75]


def test_prediction_model_with_null_employee_id():
    prediction = Prediction(
        employee_id=None,
        prediction=0,
        probability=0.25,
        probabilities=[0.75, 0.25]
    )

    assert prediction.employee_id is None
    assert prediction.prediction == 0


def test_prediction_model_all_fields():
    prediction = Prediction(
        id=1,
        employee_id=456,
        prediction=1,
        probability=0.85,
        probabilities=[0.15, 0.85]
    )

    assert prediction.id == 1
    assert prediction.employee_id == 456
    assert prediction.prediction == 1
    assert prediction.probability == 0.85
    assert prediction.probabilities == [0.15, 0.85]
