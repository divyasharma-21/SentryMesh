"""FastAPI application entrypoint for SentryMesh Guardian.

Endpoints:
  - GET  /            : Health check, system version, operational status
  - POST /analyze     : Full cognitive analysis (Observe -> Detect -> Analyse -> Explain -> Respond)
  - POST /report      : Quarantined community threat reporting with PII redaction
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from app.schemas import AnalyzeRequest, AnalyzeResponse, ReportSubmission
from app.analyzer import analyze_communication
from app.reporting import submit_user_report

app = FastAPI(
    title="SentryMesh Guardian API",
    description="Privacy-preserving AI Cybersecurity Defense System against scams, phishing, fraud calls, and UPI fraud.",
    version="1.0.0"
)

# Enable CORS for local testing and web frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health"])
def root_status():
    """Returns system status, active channels, and defense framework state."""
    return {
        "status": "operational",
        "service": "SentryMesh Guardian API",
        "version": "1.0.0",
        "framework": "Observe -> Detect -> Analyse -> Explain -> Respond -> Learn",
        "channels_supported": ["sms", "whatsapp", "email", "call", "qr", "website", "app"]
    }


@app.post("/analyze", response_model=AnalyzeResponse, tags=["Inspection"])
def analyze_endpoint(payload: AnalyzeRequest):
    """Inspects suspicious communication and delivers evidence-based explanations with safe countermeasures.

    Strict Privacy Guarantee:
      - Processed entirely in-memory.
      - Never logged to database without explicit report submission.
      - PII stripped and sanitized.
    """
    if not payload.user_consent:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User consent is required to process communication content."
        )

    try:
        result = analyze_communication(text=payload.text, channel=payload.channel)
        return result
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while evaluating the input: {str(exc)}"
        )


@app.post("/report", tags=["Reporting"])
def report_endpoint(payload: ReportSubmission):
    """Submits anonymized threat telemetry to moderator quarantine.

    Strict Non-Automatic Ingestion:
      - Quarantined until human safety engineers review.
      - Zero direct feedback into training models.
    """
    try:
        res = submit_user_report(payload.model_dump())
        return res
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit quarantine report: {str(exc)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
