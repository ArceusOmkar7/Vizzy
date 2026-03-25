"""Export router: GET /api/export/{session_id}/pdf"""
from fastapi import APIRouter
from fastapi.responses import Response
from ..core.session import get_session
from ..utils.pdf_report import generate_pdf_report

router = APIRouter(tags=["export"])


@router.get("/export/{session_id}/pdf")
def export_pdf(session_id: str) -> Response:
    """Generate and return a PDF report for the session's dataset."""
    session = get_session(session_id)
    df = session["df"]
    filename = session.get("filename", "dataset")
    pdf_bytes = generate_pdf_report(df, dataset_name=filename)
    safe_filename = filename.rsplit(".", 1)[0] + "_report.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={safe_filename}"},
    )
