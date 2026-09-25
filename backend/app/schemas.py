"""Pydantic request and response schemas for ParentCall Guardian."""

from typing import List, Literal, Optional
from pydantic import BaseModel, Field, field_validator


InputType = Literal[
    "call_transcript",
    "sms",
    "whatsapp",
    "email",
    "payment_message",
    "social_message"
]

PredictedLabel = Literal["suspicious", "legitimate"]

SafetyLevel = Literal[
    "high_risk",
    "suspicious_needs_verification",
    "uncertain_needs_verification",
    "no_strong_risk_signal"
]


class HealthResponse(BaseModel):
    status: str = "ok"
    model_loaded: bool
    model_name: str
    selected_suspicious_threshold: float
    audio_transcription_configured: bool
    voice_authenticity_configured: bool


class TextAnalysisRequest(BaseModel):
    text: str = Field(..., description="Message text or transcript to analyze")
    input_type: InputType = Field(
        default="call_transcript",
        description="Source vector of the communication"
    )

    @field_validator("text")
    @classmethod
    def validate_non_whitespace_length(cls, v: str) -> str:
        stripped = v.strip()
        non_whitespace_chars = "".join(v.split())
        if len(non_whitespace_chars) < 10:
            raise ValueError("Text must contain at least 10 non-whitespace characters.")
        return stripped


class EvidenceItem(BaseModel):
    feature: str = Field(..., description="Active n-gram or word feature")
    contribution: float = Field(..., description="Linear contribution toward prediction")


class ModelEvidence(BaseModel):
    signals_favoring_suspicious: List[EvidenceItem] = Field(default_factory=list)
    signals_favoring_legitimate: List[EvidenceItem] = Field(default_factory=list)


class ExplanationBlock(BaseModel):
    summary: str
    evidence_summary: List[str]
    uncertainty_note: str


class TextAnalysisResponse(BaseModel):
    module: str = "parent_call_guardian"
    status: str = "analyzed"
    predicted_label: PredictedLabel
    suspicious_probability: float
    selected_threshold: float
    safety_level: SafetyLevel
    input_type: InputType
    model_evidence: ModelEvidence
    explanation: ExplanationBlock
    recommended_actions: List[str]
    privacy_notice: str
    disclaimer: str


class FamilyShareRequest(BaseModel):
    safety_level: SafetyLevel
    suspicious_probability: float
    evidence_summary: List[str] = Field(default_factory=list)
    recommended_actions: List[str] = Field(default_factory=list)
    disclaimer: Optional[str] = None


class FamilyShareResponse(BaseModel):
    title: str = "SentryMesh Guardian Alert"
    safety_level: SafetyLevel
    safety_level_display: str
    why_text: str
    recommended_action_text: str
    disclaimer_text: str
    full_share_text: str


class AudioNotConfiguredResponse(BaseModel):
    module: str
    status: str = "not_configured"
    message: str


class AudioAnalysisResponse(BaseModel):
    module: str = "parent_call_audio"
    status: str = "analyzed"
    transcription_analysis: Optional[TextAnalysisResponse] = None
    voice_authenticity_analysis: Optional[dict] = None
