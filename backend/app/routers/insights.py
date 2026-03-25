"""Insights router: SSE streaming and query endpoints."""
import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from ..core.session import get_session
from ..models.insights import QueryRequest, QueryResponse
from ..utils.insights_generator import (
    generate_llm_insights_stream,
    extract_data_insights,
    GEMINI_AVAILABLE,
)

router = APIRouter(tags=["insights"])


@router.get("/insights/{session_id}")
async def stream_insights(session_id: str) -> StreamingResponse:
    """Stream AI insights as Server-Sent Events."""
    session = get_session(session_id)
    df = session["df"]

    async def event_generator():
        async for chunk in generate_llm_insights_stream(df):
            yield chunk
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/query/{session_id}", response_model=QueryResponse)
async def query_data(session_id: str, request: QueryRequest) -> QueryResponse:
    """Answer a user question about the dataset using Gemini."""
    from ..core.config import settings

    session = get_session(session_id)
    df = session["df"]

    if not GEMINI_AVAILABLE:
        return QueryResponse(
            question=request.question,
            answer="",
            error="Google Generative AI package not installed.",
        )

    if not settings.GEMINI_API_KEY:
        return QueryResponse(
            question=request.question,
            answer="",
            error="GEMINI_API_KEY not configured.",
        )

    try:
        import google.generativeai as genai

        genai.configure(api_key=settings.GEMINI_API_KEY)
        insights = extract_data_insights(df)
        context = json.dumps(
            {
                "shape": insights["basic_info"]["shape"],
                "columns": insights["basic_info"]["columns"],
                "dtypes": {k: str(v) for k, v in insights["basic_info"]["dtypes"].items()},
                "missing_values": insights["missing_values"],
                "quality": insights["quality"],
            },
            default=str,
        )
        prompt = (
            f"Dataset context:\n{context}\n\n"
            f"User question: {request.question}\n\n"
            "Provide a concise, data-driven answer."
        )
        model = genai.GenerativeModel(settings.GEMINI_MODEL)
        response = model.generate_content(prompt)
        return QueryResponse(question=request.question, answer=response.text)
    except Exception as e:
        return QueryResponse(question=request.question, answer="", error=str(e))
