from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.services.ai_service import analyze_code

app = FastAPI()

class CodeInput(BaseModel):
    code: str

@app.post("/analyze/")
async def analyze_code_api(code_input: CodeInput):
    """
    Endpoint to analyze code using DeepSeek-Coder.
    """
    try:
        result = analyze_code(code_input.code)
        return {"suggestions": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
