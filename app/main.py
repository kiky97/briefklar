import io
import os
from pathlib import Path

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, Response

from . import pipeline
from .config import get_settings
from .ics import facts_to_ics
from .llm import get_llm
from .schemas import AnalyzeRequest, AnalyzeResponse, AskRequest, Facts, ReplyRequest, TextResponse

STATIC = Path(__file__).parent / "static"
# Swagger UI loads its assets from a public CDN, so it is off by default to keep the
# app free of outbound requests (air-gapped deployments). Enable with ENABLE_API_DOCS=1.
_docs = os.getenv("ENABLE_API_DOCS", "").lower() in ("1", "true", "yes")
app = FastAPI(
    title="Apertus Letter Helper",
    docs_url="/docs" if _docs else None,
    redoc_url="/redoc" if _docs else None,
    openapi_url="/openapi.json" if _docs else None,
)


def _llm_errors(fn):
    try:
        return fn()
    except ValueError as e:
        raise HTTPException(502, f"The model returned output that could not be parsed: {e}")
    except Exception as e:  # network / auth errors from the inference endpoint
        raise HTTPException(502, f"Model call failed: {type(e).__name__}: {e}")


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


@app.get("/api/health")
def health():
    s = get_settings()
    return {"model": s.model, "base_url": s.base_url, "mock": s.mock, "has_key": bool(s.api_key)}


@app.post("/api/upload", response_model=TextResponse)
async def upload(file: UploadFile = File(...)):
    data = await file.read()
    name = (file.filename or "").lower()
    if name.endswith(".pdf"):
        try:
            from pypdf import PdfReader
        except ImportError:
            raise HTTPException(400, "PDF support needs `pip install pypdf`.")
        text = "\n".join(page.extract_text() or "" for page in PdfReader(io.BytesIO(data)).pages)
        if not text.strip():
            raise HTTPException(400, "This PDF has no text layer (it is probably a scan). Paste the text instead.")
        return TextResponse(text=text)
    try:
        return TextResponse(text=data.decode("utf-8"))
    except UnicodeDecodeError:
        return TextResponse(text=data.decode("latin-1"))


@app.post("/api/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest, llm=Depends(get_llm)):
    def run():
        facts = pipeline.extract_facts(llm, req.letter)
        return AnalyzeResponse(facts=facts, explanation=pipeline.explain(llm, req.letter, facts, req.language))

    return _llm_errors(run)


@app.post("/api/ask", response_model=TextResponse)
def ask(req: AskRequest, llm=Depends(get_llm)):
    return _llm_errors(lambda: TextResponse(text=pipeline.ask(llm, req.letter, req.facts, req.language, req.question, req.history)))


@app.post("/api/reply", response_model=TextResponse)
def reply(req: ReplyRequest, llm=Depends(get_llm)):
    return _llm_errors(lambda: TextResponse(text=pipeline.draft_reply(llm, req.letter, req.facts, req.language, req.intent)))


@app.post("/api/ics")
def ics(facts: Facts):
    return Response(
        facts_to_ics(facts),
        media_type="text/calendar",
        headers={"Content-Disposition": 'attachment; filename="letter-deadlines.ics"'},
    )
