from fastapi import APIRouter, HTTPException
import schemas
from analysis_engine import run_analysis

router = APIRouter(prefix="/api/analysis", tags=["Analysis"])


@router.post("/run", response_model=schemas.AnalysisResultOut)
def analyze(
    body: schemas.AnalysisRequest,
):
    """Run the renovation analysis engine and return full result."""
    valid_categories = {"painting", "ceiling", "doors", "windows", "furniture"}
    valid_budgets = {"luxury", "moderate", "budget"}
    valid_property = {"urban", "rural"}

    if body.category not in valid_categories:
        raise HTTPException(status_code=422, detail=f"Invalid category. Choose from {valid_categories}")
    if body.budget not in valid_budgets:
        raise HTTPException(status_code=422, detail=f"Invalid budget. Choose from {valid_budgets}")
    if body.propertyType not in valid_property:
        raise HTTPException(status_code=422, detail=f"Invalid propertyType. Choose from {valid_property}")

    return run_analysis(body)

