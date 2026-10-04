from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from schemas import PatientData, PredictionResponse, ClassProbability, FeatureImpact
from recommendations import generate_recommendations
from ml_loader import loader


app = FastAPI(
    title="Anemia Screening Service",
    description="ИИ-сервис для скрининга дефицитных состояний",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "Anemia service is running",
        "model_loaded": loader.loaded,
    }


@app.get("/health")
def health():
    return {
        "status": "ok" if loader.loaded else "degraded",
        "model_loaded": loader.loaded,
        "model_error": loader.load_error,
        "features_count": len(loader.feature_names) if loader.feature_names else 0,
    }


@app.post("/predict", response_model=PredictionResponse)
def predict(data: PatientData) -> PredictionResponse:
    try:
        data_dict = data.model_dump()
        result = loader.predict(data_dict)

        if not result.get("ok"):
            raise HTTPException(
                status_code=503,
                detail=f"ML model unavailable: {result.get('error', 'unknown error')}",
            )

        anemia_classes = {
            "iron_deficiency_anemia", "B12_deficiency_anemia",
            "folate_deficiency_anemia", "inflammation_anemia",
            "mixed_deficiency", "anemia_other",
        }
        class_pred = result["class_prediction"]
        anemia_present = class_pred in anemia_classes

        rec_doctor, rec_patient = generate_recommendations(
            class_name=class_pred,
            anemia_present=anemia_present,
            data=data,
        )

        missing = result.get("missing_features", [])
        if missing:
            critical = [
                f for f in missing
                if f in {
                    "hemoglobin", "MCV", "MCH", "MCHC", "RDW",
                    "ferritin", "serum_iron", "TSAT", "sTfR",
                    "vitamin_B12", "active_B12", "folate", "homocysteine", "MMA",
                    "CRP", "ESR",
                }
            ]
            if critical:
                tests_to_add = ", ".join(critical[:10])
                rec_doctor += f"\n\n[!] Missing tests for accurate diagnosis: {tests_to_add}. Recommended to add."
                rec_patient += "\n\nSome tests are missing - the doctor may order additional ones."

        return PredictionResponse(
            patient_id=data.patient_id,
            anemia_present=anemia_present,
            anemia_confidence=result["class_probability"],
            class_prediction=class_pred,
            class_probability=result["class_probability"],
            top_3_classes=[
                ClassProbability(name=c["name"], probability=c["probability"])
                for c in result["top_3_classes"]
            ],
            top_3_features=[
                FeatureImpact(
                    feature=f["feature"],
                    value=f["value"],
                    impact=f["impact"],
                )
                for f in result["top_3_features"]
            ],
            recommendation_for_doctor=rec_doctor,
            recommendation_for_patient=rec_patient,
            missing_features=result.get("missing_features", []),
            data_completeness=result.get("data_completeness", 1.0),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal service error: {str(e)}",
        )
