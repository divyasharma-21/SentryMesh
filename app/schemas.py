"""Pydantic data schemas for SentryMesh Guardian API requests and responses.

Follows strict privacy, security, and response contracts.
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field, field_validator


class AnalyzeRequest(BaseModel):
    """Input payload for POST /analyze endpoint."""
    text: str = Field(..., min_length=2, max_length=8000, description="The communication or message content to inspect.")
    channel: str = Field(
        default="sms",
        description="Originating communication channel: sms | whatsapp | email | call | qr | website | app"
    )
    user_consent: bool = Field(
        default=True,
        description="Explicit user consent to analyze this content in-memory for security evaluation."
    )

    @field_validator("channel")
    @classmethod
    def validate_channel(cls, v: str) -> str:
        valid_channels = {"sms", "whatsapp", "email", "call", "qr", "website", "app"}
        clean = v.lower().strip()
        if clean not in valid_channels:
            return "sms"
        return clean


class ClassificationResult(BaseModel):
    """Predicted risk category and probability distribution."""
    predicted_label: str = Field(..., description="Categorical prediction")
    probabilities: Dict[str, float] = Field(..., description="Calibrated probabilities per class")


class ExtractedEntities(BaseModel):
    """Indicators of compromise and tokens parsed from input."""
    urls: List[str] = Field(default_factory=list)
    domains: List[str] = Field(default_factory=list)
    emails: List[str] = Field(default_factory=list)
    phone_numbers: List[str] = Field(default_factory=list)
    upi_ids: List[str] = Field(default_factory=list)
    amounts: List[str] = Field(default_factory=list)


class AnalyzeResponse(BaseModel):
    """Contract for POST /analyze output.

    Must contain:
      classification
      entities
      tactics
      verification
      explanation
      recommended_actions
      uncertainty
    """
    classification: ClassificationResult
    entities: ExtractedEntities
    tactics: Dict[str, float] = Field(..., description="Scores for detected manipulation tactics (0.0 to 1.0)")
    verification: Dict[str, Any] = Field(..., description="Signals from URL/domain reputation and heuristics")
    explanation: List[str] = Field(..., description="Step-by-step evidence-based reasons explaining the evaluation")
    recommended_actions: List[str] = Field(..., description="Immediate concrete safety steps for the user")
    uncertainty: str = Field(..., description="low | medium | high uncertainty indicator")


class ReportSubmission(BaseModel):
    """User-submitted feedback/threat report for quarantine buffer."""
    text: str = Field(..., min_length=5, max_length=8000)
    channel: str = "sms"
    suspected_label: Optional[str] = None
    user_notes: Optional[str] = None
    consent_anonymized_research: bool = True
