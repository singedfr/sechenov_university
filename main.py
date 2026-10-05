from fastapi import File, UploadFile
from pdf_parser import parse_pdf
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from schemas import PatientData, PredictionResponse, ClassProbability, FeatureImpact
from recommendations import generate_recommendations
from ml_loader import loader
from storage import save_patient, get_patient, count_patients


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


@app.post("/parse-pdf")
async def parse_pdf_endpoint(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Поддерживаются только PDF-файлы.",
        )

    try:
        contents = await file.read()

        if len(contents) > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="Файл слишком большой (максимум 10 МБ).",
            )

        result = parse_pdf(contents)

        if not result["ok"]:
            raise HTTPException(
                status_code=422,
                detail=result.get("error", "Не удалось распознать PDF."),
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка обработки PDF: {str(e)}",
        )


from pydantic import BaseModel as _BM
from typing import Optional as _Opt


class SaveRequest(_BM):
    patient_id: str
    result: dict


class PatientLookupResponse(_BM):
    patient_id: str
    created_at: str
    result: dict


@app.post("/patients")
def create_patient(payload: SaveRequest):
    try:
        short_id = save_patient(payload.result)
        return {
            "ok": True,
            "patient_id": short_id,
            "message": "Результат сохранён. Передайте этот ID пациенту.",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Не удалось сохранить: {str(e)}")


@app.get("/patients/{patient_id}", response_model=PatientLookupResponse)
def read_patient(patient_id: str):
    record = get_patient(patient_id)
    if record is None:
        raise HTTPException(
            status_code=404,
            detail="Результат с таким ID не найден. Проверьте код.",
        )
    return PatientLookupResponse(**record)


@app.get("/admin/stats")
def admin_stats():
    return {"patients_count": count_patients()}
