from fastapi import FastAPI, HTTPException
from schemas import (
    PatientData,
    PredictionResponse,
    ClassProbability,
    FeatureImpact,
)
from recommendations import generate_recommendations


app = FastAPI(
    title="Anemia Screening Service",
    description="ИИ-сервис для скрининга дефицитных состояний",
    version="0.1.0",
)


def mock_predict(data: PatientData) -> dict:
    hb = data.hemoglobin if data.hemoglobin is not None else 140.0
    threshold = 120.0 if data.sex == "female" else 130.0
    is_anemia = hb < threshold

    if is_anemia:
        class_pred = "iron_deficiency_anemia"
        class_prob = 0.85
    else:
        class_pred = "no_anemia_no_deficiency"
        class_prob = 0.90

    return {
        "anemia_present": is_anemia,
        "anemia_confidence": 0.92,
        "class_prediction": class_pred,
        "class_probability": class_prob,
        "top_3_classes": [
            (class_pred, class_prob),
            ("mixed_deficiency", 0.08),
            ("inflammation_anemia", 0.04),
        ],
        "top_3_features": [
            ("hemoglobin", data.hemoglobin, -0.45),
            ("ferritin", data.ferritin, -0.30),
            ("mcv", data.mcv, -0.20),
        ],
    }


@app.get("/")
def root():
    return {"status": "ok", "message": "Anemia service is running"}


@app.post("/predict", response_model=PredictionResponse)
def predict(data: PatientData) -> PredictionResponse:
    try:
        result = mock_predict(data)
        rec_doctor, rec_patient = generate_recommendations(
            class_name=result["class_prediction"],
            anemia_present=result["anemia_present"],
            data=data,
        )
        return PredictionResponse(
            patient_id=data.patient_id,
            anemia_present=result["anemia_present"],
            anemia_confidence=result["anemia_confidence"],
            class_prediction=result["class_prediction"],
            class_probability=result["class_probability"],
            top_3_classes=[
                ClassProbability(name=c, probability=p)
                for c, p in result["top_3_classes"]
            ],
            top_3_features=[
                FeatureImpact(feature=f, value=v, impact=i)
                for f, v, i in result["top_3_features"]
            ],
            recommendation_for_doctor=rec_doctor,
            recommendation_for_patient=rec_patient,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")