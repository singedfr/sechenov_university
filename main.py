from fastapi import FastAPI, HTTPException
from schemas import PatientData, PredictionResponse, ClassProbability, FeatureImpact
from recommendations import generate_recommendations
from ml_loader import loader


app = FastAPI(
    title="Anemia Screening Service",
    description="ИИ-сервис для скрининга дефицитных состояний",
    version="0.1.0",
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
    """Расширенная проверка состояния сервиса."""
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
                detail=f"ML-модель недоступна: {result.get('error', 'неизвестная ошибка')}",
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
        missing = result.get("missing_feature", [])
        if missing:
            critical = [
                f for f in missing
                if f in {
                    "hemoglobin", "MCV", "MCH", "MCHC", "RDW",
                    "ferritin", "serum_iron", "tsat", "stfr",
                    "vitamin_b12", "folate", "homocysteine", "mma",
                    "crp", "esr",
                }
            ]
            if critical:
                tests_to_add = ", ".join(critical[:10])
                rec_doctor += f"\n\n⚠️ Не хватает анализов для точного диагноза: {tests_to_add}. Рекомендуется досдать."
                rec_patient += "\n\nЧасть анализов не сдана — врач может назначить дополнительные исследования."
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
            missing_features=result.get("missing_features", [])
            data_completeness=result.get("data_completeness", 1.0),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Внутренняя ошибка сервиса: {str(e)}",
        )