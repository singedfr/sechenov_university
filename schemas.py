from pydantic import BaseModel
from typing import Optional, List


class PatientData(BaseModel):
    patient_id: str
    age_years: Optional[float] = None
    sex: Optional[str] = None
    hemoglobin: Optional[float] = None
    MCV: Optional[float] = None
    MCH: Optional[float] = None
    MCHC: Optional[float] = None
    RDW: Optional[float] = None
    hematocrit: Optional[float] = None
    rbc: Optional[float] = None
    ferritin: Optional[float] = None
    vitamin_b12: Optional[float] = None
    folate: Optional[float] = None
    crp: Optional[float] = None


class FeatureImpact(BaseModel):
    feature: str
    value: Optional[float] = None
    impact: float


class ClassProbability(BaseModel):
    name: str
    probability: float


class PredictionResponse(BaseModel):
    patient_id: str
    anemia_present: bool
    anemia_confidence: float
    class_prediction: str
    class_probability: float
    top_3_classes: List[ClassProbability]
    top_3_features: List[FeatureImpact]
    recommendation_for_doctor: str
    recommendation_for_patient: str
    missing_features: List[str] = []
    data_completeness: float = 1.0