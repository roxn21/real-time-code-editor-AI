import ollama
import json

def analyze_code(code: str) -> dict:
    """
    Sends code to DeepSeek-Coder for analysis and returns structured debugging suggestions.
    """
    model = "deepseek-coder:6.7b"
    prompt = f"""
    Analyze the following Python code and provide debugging suggestions in JSON format.
    
    Categories:
    1. Errors (syntax, runtime, logical)
    2. Warnings (potential issues, anti-patterns)
    3. Performance Improvements (optimizations)
    
    Return JSON with this structure:
    {{
        "errors": [{{"line": int, "message": str}}],
        "warnings": [{{"line": int, "message": str}}],
        "optimizations": [{{"line": int, "message": str}}]
    }}

    Code:
    {code}
    """

    response = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])

    try:
        structured_output = json.loads(response["message"]["content"])
        return structured_output
    except json.JSONDecodeError:
        return {"errors": [], "warnings": [], "optimizations": ["Failed to parse AI response"]}
